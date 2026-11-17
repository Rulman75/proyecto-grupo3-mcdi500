"""
Módulo de funciones de limpieza interanual, rescate geográfico vectorizado, cálculo longitudinal
de persistencia, referencia funcional sin clases y comparación contra la Sumativa 1 (MCDI500).
"""

import io
from pathlib import Path
import re
import subprocess
import unicodedata
import numpy as np
import pandas as pd


MAPA_REGIONES_CHILE = {
    "Libertador Gral. Bernardo O'Higgins": "Libertador General Bernardo O'Higgins",
    "Araucanía": "La Araucanía",
    "Aysén del Gral. Carlos Ibañez del Campo": "Aysén del General Carlos Ibáñez del Campo",
}


def depurar_registros_base(df: pd.DataFrame) -> pd.DataFrame:
    """
    Elimina filas duplicadas exactas (118 registros) y descarta explícitamente las declaraciones
    sin masa declarada ('cantidad_kg' nulo: 21 registros), ya que la masa declarada es la variable
    analítica central y no debe inventarse mediante imputación.
    """
    if "cantidad_kg" not in df.columns:
        raise KeyError("La columna 'cantidad_kg' es obligatoria para depurar registros base.")
    df_sin_dup = df.drop_duplicates().copy()
    df_valido = df_sin_dup.dropna(subset=["cantidad_kg"]).copy().reset_index(drop=True)
    return df_valido


def normalizar_glosa_individual(valor: str) -> str:
    """Quita tildes, pasa a mayúsculas, unifica separadores ('##' y ';') y ordena componentes."""
    if pd.isna(valor):
        return "SIN CLASIFICAR"
    nfkd = unicodedata.normalize("NFKD", str(valor))
    sin_tildes = "".join(c for c in nfkd if not unicodedata.combining(c)).upper().strip()
    partes = [p.strip() for p in re.split(r"##|;", sin_tildes) if p.strip()]
    return " + ".join(sorted(set(partes))) if partes else "SIN CLASIFICAR"


def normalizar_peligrosidad_fila_a_fila(serie: pd.Series) -> pd.Series:
    """Versión base (Fase 2): aplica la normalización fila por fila sobre toda la serie."""
    return serie.apply(normalizar_glosa_individual)


def normalizar_peligrosidad_por_unicos(serie: pd.Series) -> pd.Series:
    """
    Versión optimizada (Fase 3): normaliza únicamente los valores únicos (812 glosas distintas)
    en un diccionario en memoria y los proyecta sobre las 118.141 filas mediante .map().
    """
    valores_unicos = serie.dropna().unique()
    mapa_canonico = {val: normalizar_glosa_individual(val) for val in valores_unicos}
    return serie.map(mapa_canonico).fillna("SIN CLASIFICAR")


def estandarizar_regiones_y_peligrosidad(df: pd.DataFrame, usar_optimizado: bool = True) -> pd.DataFrame:
    """
    Homologa las etiquetas de 'region' (de 19 variantes a las 16 regiones oficiales de Chile),
    corrige el dígito extra de 'id_ciiu4' en 2024 (truncando a 5 caracteres alfanuméricos),
    limpia 'id_peligrosidad', estandariza 'peligrosidad' (de 812 a 93 categorías canónicas)
    y normaliza 'estado_materia'.
    """
    df_out = df.copy()
    if "region" in df_out.columns:
        df_out["region"] = df_out["region"].astype(str).str.strip().replace(MAPA_REGIONES_CHILE)
    if "id_ciiu4" in df_out.columns:
        mask_ciiu = df_out["id_ciiu4"].notna()
        df_out.loc[mask_ciiu, "id_ciiu4"] = (
            df_out.loc[mask_ciiu, "id_ciiu4"].astype(str).str.strip().str[:5]
        )
    if "id_peligrosidad" in df_out.columns:
        df_out["id_peligrosidad"] = df_out["id_peligrosidad"].astype(str).str.strip().str.rstrip(",")
    if "peligrosidad" in df_out.columns:
        if usar_optimizado:
            df_out["peligrosidad"] = normalizar_peligrosidad_por_unicos(df_out["peligrosidad"])
        else:
            df_out["peligrosidad"] = normalizar_peligrosidad_fila_a_fila(df_out["peligrosidad"])
    if "estado_materia" in df_out.columns:
        df_out["estado_materia"] = df_out["estado_materia"].astype(str).str.strip().str.lower()
    return df_out


def _rescatar_valor_coordenada(val, min_val: float, max_val: float) -> float:
    """Versión escalar (Fase 2): recupera el punto decimal valor por valor con bucle while."""
    if pd.isna(val):
        return np.nan
    v = float(val)
    if min_val <= v <= max_val:
        return round(v, 6)
    if v < 0:
        while v < min_val and abs(v) > 100.0:
            v /= 10.0
    if min_val <= v <= max_val:
        return round(v, 6)
    return np.nan


def rescatar_serie_coordenada_bucle(serie: pd.Series, min_val: float, max_val: float) -> pd.Series:
    """Aplica el rescate de coordenadas valor por valor mediante .apply()."""
    return serie.apply(lambda x: _rescatar_valor_coordenada(x, min_val, max_val))


def rescatar_serie_coordenada_vectorizada(serie: pd.Series, min_val: float, max_val: float) -> pd.Series:
    """
    Versión vectorizada (Fase 3): divide en bloque todas las coordenadas fuera de escala
    operando sobre arreglos de punto flotante de pandas/NumPy y filtra el rango de Chile.
    """
    s = serie.astype(float).copy()
    mask_escala = (s < min_val) & (s.abs() > 100.0)
    while mask_escala.any():
        s.loc[mask_escala] = s.loc[mask_escala] / 10.0
        mask_escala = (s < min_val) & (s.abs() > 100.0)
    s = s.where((s >= min_val) & (s <= max_val), np.nan)
    return s.round(6)


def rescatar_coordenadas_chile(df: pd.DataFrame, usar_vectorizado: bool = True) -> pd.DataFrame:
    """
    Corrige la pérdida del punto decimal en latitud/longitud del año 2024 y convierte en NaN
    cualquier coordenada fuera de Chile Continental e Insular:
    latitud en [-57.0, -17.0] y longitud en [-110.0, -65.0].
    """
    df_out = df.copy()
    if "latitud" in df_out.columns:
        if usar_vectorizado:
            df_out["latitud"] = rescatar_serie_coordenada_vectorizada(df_out["latitud"], -57.0, -17.0)
        else:
            df_out["latitud"] = rescatar_serie_coordenada_bucle(df_out["latitud"], -57.0, -17.0)
    if "longitud" in df_out.columns:
        if usar_vectorizado:
            df_out["longitud"] = rescatar_serie_coordenada_vectorizada(df_out["longitud"], -110.0, -65.0)
        else:
            df_out["longitud"] = rescatar_serie_coordenada_bucle(df_out["longitud"], -110.0, -65.0)
    return df_out


def agregar_atributos_deterministas(df: pd.DataFrame) -> pd.DataFrame:
    """
    Agrega las variables derivadas que no dependen de parámetros estadísticos aprendidos:
    - Persistencia longitudinal del establecimiento ('n_anios_declarados_vu' y 'es_generador_persistente_bin').
    - Complejidad de peligrosidad ('n_peligrosidades' y 'multi_peligrosidad_bin').
    - Umbral regulatorio D.S. 148 Art. 25 ('es_gran_generador_bin' >= 12.000 kg/año).
    - Índice temporal trianual ('anio_indice' = año - 2023).
    """
    df_out = df.copy()
    df_out["n_anios_declarados_vu"] = df_out.groupby("id_vu")["año"].transform("nunique").astype(int)
    df_out["es_generador_persistente_bin"] = (df_out["n_anios_declarados_vu"] == 3).astype(int)

    df_out["n_peligrosidades"] = df_out["peligrosidad"].astype(str).str.count(r" \+ ") + 1
    df_out["multi_peligrosidad_bin"] = (df_out["n_peligrosidades"] > 1).astype(int)
    df_out["es_gran_generador_bin"] = (df_out["cantidad_kg"] >= 12000.0).astype(int)
    df_out["anio_indice"] = (df_out["año"] - 2023).astype(int)
    return df_out


def preprocesar_version_funcional(
    df_raw: pd.DataFrame,
    top_n_comunas: int = 10,
) -> pd.DataFrame:
    """
    Implementación procedural/funcional pura (sin clases ni Pipeline) de todas las etapas
    de la Fase 2 corregida. Permite verificar de forma no circular que la arquitectura
    orientada a objetos de la Fase 3 produce exactamente el mismo resultado.
    """
    df = depurar_registros_base(df_raw)
    df = estandarizar_regiones_y_peligrosidad(df, usar_optimizado=True)
    df = rescatar_coordenadas_chile(df, usar_vectorizado=True)
    df = agregar_atributos_deterministas(df)

    # 1. Imputación numérica por región y categórica por id_rubro (sin clases)
    for col in ["latitud", "longitud"]:
        if True:
            df[f"{col}_imputado"] = df[col].isna().astype(int)
            med_reg = df.groupby("region")[col].median().to_dict()
            respaldo = float(df[col].median()) if pd.notna(df[col].median()) else 0.0
            df[col] = df[col].fillna(df["region"].map(med_reg)).fillna(respaldo)

    for col in ["id_lista_a", "id_ciiu4", "ciiu4", "id_ciiu6", "ciiu6", "rubro"]:
        if True:
            df[f"{col}_imputado"] = df[col].isna().astype(int)
            modas_rubro = (
                df.groupby("id_rubro")[col]
                .apply(lambda s: s.mode().iloc[0] if not s.mode().empty else np.nan)
                .to_dict()
            )
            moda_gl = df[col].mode().iloc[0] if not df[col].mode().empty else "SIN_DATO"
            df[col] = df[col].fillna(df["id_rubro"].map(modas_rubro)).fillna(moda_gl)

    # 2. Codificación categórica por frecuencia y One-Hot (sin clases)
    top_comunas = df["comuna"].value_counts().nlargest(top_n_comunas).index.tolist()
    df["comuna_agrupada"] = df["comuna"].where(df["comuna"].isin(top_comunas), "OTROS")

    df["frecuencia_declaraciones_rut"] = (
        df["rut_razon_social"].map(df["rut_razon_social"].value_counts()).fillna(0).astype(int)
    )
    df["frecuencia_ciiu4"] = df["id_ciiu4"].map(df["id_ciiu4"].value_counts()).fillna(0).astype(int)
    df["frecuencia_lista_a"] = df["id_lista_a"].map(df["id_lista_a"].value_counts()).fillna(0).astype(int)

    for cat in sorted(df["region"].dropna().unique().tolist()):
        df[f"reg_{cat}"] = (df["region"] == cat).astype(int)
    for cat in sorted(df["estado_materia"].dropna().unique().tolist()):
        df[f"estado_{cat}"] = (df["estado_materia"] == cat).astype(int)
    for cat in sorted(df["comuna_agrupada"].dropna().unique().tolist()):
        df[f"comuna_top_{cat}"] = (df["comuna_agrupada"] == cat).astype(int)

    # 3. Escalamiento robusto con mediana y RIC y descarte de columnas textuales (sin clases)
    cols_escalar = [
        "cantidad_kg", "latitud", "longitud", "frecuencia_declaraciones_rut", "n_peligrosidades"
    ]
    for col in cols_escalar:
        s = df[col].dropna()
        mediana = float(s.median())
        ric = float(s.quantile(0.75) - s.quantile(0.25))
        ric = ric if ric != 0.0 else 1.0
        df[f"{col}_rob"] = (df[col] - mediana) / ric

    cols_texto = df.select_dtypes(exclude=["number"]).columns.tolist()
    df = df.drop(columns=cols_texto)
    return df


def comparar_con_entregable_sumativa1(
    df_actual: pd.DataFrame,
    ruta_repo: str | Path = ".",
) -> tuple[pd.DataFrame, dict]:
    """
    Compara el DataFrame actual (Fase 2 corregida / Fase 3) contra la versión entregada
    en la Sumativa 1 (118.162 filas × 68 columnas), recuperándola desde Git si está disponible
    y construyendo la tabla detallada de diferencias en filas y columnas, su motivo y su efecto.
    """
    filas_s1 = 118162
    cols_s1 = 68
    recuperado_git = False

    try:
        commit_hash = subprocess.check_output(
            ["git", "-C", str(ruta_repo), "log", "--grep=Update README Asistencia y uso ético de IA", "-n", "1", "--format=%H"],
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
        if not commit_hash:
            commit_hash = "7adaee7"
        raw_bytes = subprocess.check_output(
            ["git", "-C", str(ruta_repo), "show", f"{commit_hash}:F2/data/processed/base_maestra_2023_2025_clean.csv"],
            stderr=subprocess.DEVNULL,
        )
        df_s1 = pd.read_csv(io.BytesIO(raw_bytes), nrows=5)
        cols_s1 = len(df_s1.columns)
        recuperado_git = True
    except Exception:
        pass

    diferencias = [
        {
            "elemento": "Filas del conjunto procesado",
            "sumativa_1": f"{filas_s1:,} filas",
            "fase_3_actual": f"{len(df_actual):,} filas",
            "cambio": "-21 filas",
            "motivo": "No imputar la variable objetivo 'cantidad_kg' cuando está ausente.",
            "efecto": "Elimina 21 registros sin masa declarada y evita introducir valores artificiales en el volumen.",
        },
        {
            "elemento": "Columna 'cantidad_kg_imputado'",
            "sumativa_1": "Presente (binaria 0/1)",
            "fase_3_actual": "Eliminada",
            "cambio": "-1 columna",
            "motivo": "Al descartar las 21 filas sin 'cantidad_kg', ningún valor de masa es imputado.",
            "efecto": "Evita mantener una columna constante de puros ceros sin varianza.",
        },
        {
            "elemento": "Columna 'estado_materia_ord'",
            "sumativa_1": "Presente (1 a 4)",
            "fase_3_actual": "Eliminada",
            "cambio": "-1 columna",
            "motivo": "Eliminar la doble codificación (ordinal y nominal simultánea) de 'estado_materia'.",
            "efecto": "Se conserva únicamente la codificación One-Hot nominal (4 columnas), eliminando el orden artificial.",
        },
        {
            "elemento": "Columnas 'anio_sin' y 'anio_cos'",
            "sumativa_1": "Presentes (2 columnas)",
            "fase_3_actual": "Eliminadas",
            "cambio": "-2 columnas",
            "motivo": "Tres años consecutivos (2023, 2024 y 2025) no constituyen un ciclo periódico.",
            "efecto": "Se reemplazan por el índice lineal 'anio_indice' (0, 1, 2) que representa el avance temporal real.",
        },
        {
            "elemento": "Columnas 'ciiu4_n_palabras', 'ciiu6_largo_chars' y 'ciiu4_n_palabras_rob'",
            "sumativa_1": "Presentes (3 columnas)",
            "fase_3_actual": "Eliminadas",
            "cambio": "-3 columnas",
            "motivo": "El largo de la glosa CIIU no aporta información sobre persistencia ni volumen de residuos.",
            "efecto": "Reduce dimensionalidad y ruido conservando la información sectorial en 'id_rubro' y 'frecuencia_ciiu4'.",
        },
    ]

    resumen = {
        "filas_sumativa1": filas_s1,
        "columnas_sumativa1": cols_s1,
        "filas_actual": len(df_actual),
        "columnas_actual": df_actual.shape[1],
        "diferencia_filas": len(df_actual) - filas_s1,
        "diferencia_columnas": df_actual.shape[1] - cols_s1,
        "verificado_desde_git": recuperado_git,
    }
    return pd.DataFrame(diferencias), resumen
