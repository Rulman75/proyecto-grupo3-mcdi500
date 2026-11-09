"""
Módulo de funciones reutilizables para exploración, limpieza interanual, rescate geográfico,
imputación y trazabilidad de la Base Maestra RETC 2023-2025 (Fase 2 - MCDI500).
Grupo 3: Madeleine Aguilera, Victoria Álvarez, Ignacio Peña y Raúl Hormazábal.
"""
 
from pathlib import Path
import re
import unicodedata
import numpy as np
import pandas as pd
 
 
MAPA_REGIONES_CHILE = {
    "Libertador Gral. Bernardo O'Higgins": "Libertador General Bernardo O'Higgins",
    "Araucanía": "La Araucanía",
    "Aysén del Gral. Carlos Ibañez del Campo": "Aysén del General Carlos Ibáñez del Campo",
}
 
 
def cargar_datos_seguro(ruta_archivo: str | Path) -> pd.DataFrame:
    """
    Carga un archivo Excel (.xlsx) o CSV de forma controlada validando su existencia y contenido.
    Aplica manejo de excepciones (try/except) según buenas prácticas de software científico.
    """
    ruta = Path(ruta_archivo)
    try:
        if not ruta.exists():
            raise FileNotFoundError(f"El archivo no existe en la ruta: {ruta}")
        if ruta.suffix.lower() in {".xlsx", ".xls"}:
            df = pd.read_excel(ruta)
        else:
            df = pd.read_csv(ruta, encoding="utf-8")
        if df.empty:
            raise ValueError(f"El archivo '{ruta.name}' está vacío (0 filas).")
        return df
    except (FileNotFoundError, ValueError) as err:
        print(f"[ERROR DE VALIDACIÓN] {err}")
        raise
    except Exception as err:
        print(f"[ERROR INESPERADO] No se pudo leer '{ruta}': {err}")
        raise
 
 
def diagnosticar_variables(df: pd.DataFrame) -> pd.DataFrame:
    """
    Recorre las columnas del DataFrame mediante un ciclo for y condicionales
    para cuantificar nulos, valores únicos y valores atípicos (criterio 1.5 * RIC).
    """
    if not isinstance(df, pd.DataFrame) or df.empty:
        raise ValueError("Se requiere un DataFrame no vacío para diagnosticar variables.")
 
    reporte = []
    for col in df.columns:
        serie = df[col]
        nulos_n = int(serie.isna().sum())
        nulos_pct = round((nulos_n / len(df)) * 100, 2)
        unicos_n = int(serie.nunique(dropna=True))
 
        if pd.api.types.is_numeric_dtype(serie) and not pd.api.types.is_bool_dtype(serie):
            s_limpia = serie.dropna()
            q1 = float(s_limpia.quantile(0.25))
            mediana = float(s_limpia.median())
            media = float(s_limpia.mean())
            q3 = float(s_limpia.quantile(0.75))
            ric = q3 - q1
            lim_inf = q1 - 1.5 * ric
            lim_sup = q3 + 1.5 * ric
            outliers_n = int(((s_limpia < lim_inf) | (s_limpia > lim_sup)).sum())
            outliers_pct = round((outliers_n / len(s_limpia)) * 100, 2)
        else:
            media = mediana = ric = np.nan
            outliers_n = 0
            outliers_pct = 0.0
 
        reporte.append({
            "variable": col,
            "dtype": str(serie.dtype),
            "unicos": unicos_n,
            "nulos_n": nulos_n,
            "nulos_pct": nulos_pct,
            "media": round(media, 2) if pd.notna(media) else np.nan,
            "mediana": round(mediana, 2) if pd.notna(mediana) else np.nan,
            "ric": round(ric, 2) if pd.notna(ric) else np.nan,
            "outliers_iqr_n": outliers_n,
            "outliers_iqr_pct": outliers_pct,
        })
 
    return pd.DataFrame(reporte)
 
 
def _normalizar_glosa_peligrosidad(valor: str) -> str:
    """Quita tildes, pasa a mayúsculas, unifica separadores ('##' y ';') y ordena componentes."""
    if pd.isna(valor):
        return "SIN CLASIFICAR"
    nfkd = unicodedata.normalize("NFKD", str(valor))
    sin_tildes = "".join(c for c in nfkd if not unicodedata.combining(c)).upper().strip()
    partes = [p.strip() for p in re.split(r"##|;", sin_tildes) if p.strip()]
    return " + ".join(sorted(set(partes))) if partes else "SIN CLASIFICAR"
 
 
def estandarizar_regiones_y_peligrosidad(df: pd.DataFrame) -> pd.DataFrame:
    """
    Homologa las etiquetas de 'region' (de 19 variantes a las 16 regiones de Chile),
    corrige el dígito extra de 'id_ciiu4' en 2024 (truncando a 5 caracteres alfanuméricos),
    limpia 'id_peligrosidad', estandariza 'peligrosidad' (de 812 a 93 categorías canónicas)
    y normaliza 'estado_materia'.
    """
    df_out = df.copy()
    if "region" in df_out.columns:
        df_out["region"] = df_out["region"].astype(str).str.strip().replace(MAPA_REGIONES_CHILE)
    if "id_ciiu4" in df_out.columns:
        mask_ciiu = df_out["id_ciiu4"].notna()
        df_out.loc[mask_ciiu, "id_ciiu4"] = df_out.loc[mask_ciiu, "id_ciiu4"].astype(str).str.strip().str[:5]
    if "id_peligrosidad" in df_out.columns:
        df_out["id_peligrosidad"] = df_out["id_peligrosidad"].astype(str).str.strip().str.rstrip(",")
    if "peligrosidad" in df_out.columns:
        df_out["peligrosidad"] = df_out["peligrosidad"].apply(_normalizar_glosa_peligrosidad)
    if "estado_materia" in df_out.columns:
        df_out["estado_materia"] = df_out["estado_materia"].astype(str).str.strip().str.lower()
    return df_out
 
 
def _rescatar_valor_coordenada(val, min_val: float, max_val: float) -> float:
    """Recupera el punto decimal en coordenadas exportadas como enteros y valida el rango."""
    if pd.isna(val):
        return np.nan
    v = float(val)
    if min_val <= v <= max_val:
        return round(v, 6)
    if v < 0:
        while v < min_val and abs(v) > 100:
            v /= 10.0
    if min_val <= v <= max_val:
        return round(v, 6)
    return np.nan
 
 
def rescatar_coordenadas_chile(df: pd.DataFrame) -> pd.DataFrame:
    """
    Corrige la pérdida del punto decimal en latitud/longitud del año 2024 y convierte en NaN
    cualquier coordenada que quede fuera de los límites geográficos de Chile:
    latitud en [-57.0, -17.0] y longitud en [-110.0, -65.0].
    """
    df_out = df.copy()
    if "latitud" in df_out.columns:
        df_out["latitud"] = df_out["latitud"].apply(lambda x: _rescatar_valor_coordenada(x, -57.0, -17.0))
    if "longitud" in df_out.columns:
        df_out["longitud"] = df_out["longitud"].apply(lambda x: _rescatar_valor_coordenada(x, -110.0, -65.0))
    return df_out
 
 
def comparar_estrategias_nulos(
    df: pd.DataFrame, col_num: str = "cantidad_kg", col_grupo: str = "region"
) -> pd.DataFrame:
    """
    Compara cuantitativamente tres estrategias frente a valores faltantes:
    1) Eliminación por lista (dropna), 2) Imputación por media global y
    3) Imputación por mediana agrupada por región.
    """
    n_total = len(df)
    df_dropna = df.dropna()
    serie_orig = df[col_num]
    s_media = serie_orig.fillna(serie_orig.mean())
    s_mediana_grp = serie_orig.fillna(df.groupby(col_grupo)[col_num].transform("median"))
 
    return pd.DataFrame([
        {
            "estrategia": "Original (con nulos)",
            "filas_resultantes": n_total,
            "pct_filas_perdidas": 0.0,
            "media_var": round(float(serie_orig.mean()), 2),
            "mediana_var": round(float(serie_orig.median()), 2),
            "std_var": round(float(serie_orig.std()), 2),
        },
        {
            "estrategia": "1. Eliminación (dropna)",
            "filas_resultantes": len(df_dropna),
            "pct_filas_perdidas": round(((n_total - len(df_dropna)) / n_total) * 100, 2),
            "media_var": round(float(df_dropna[col_num].mean()), 2),
            "mediana_var": round(float(df_dropna[col_num].median()), 2),
            "std_var": round(float(df_dropna[col_num].std()), 2),
        },
        {
            "estrategia": "2. Imputación por media global",
            "filas_resultantes": n_total,
            "pct_filas_perdidas": 0.0,
            "media_var": round(float(s_media.mean()), 2),
            "mediana_var": round(float(s_media.median()), 2),
            "std_var": round(float(s_media.std()), 2),
        },
        {
            "estrategia": f"3. Imputación por mediana de {col_grupo} (Elegida)",
            "filas_resultantes": n_total,
            "pct_filas_perdidas": 0.0,
            "media_var": round(float(s_mediana_grp.mean()), 2),
            "mediana_var": round(float(s_mediana_grp.median()), 2),
            "std_var": round(float(s_mediana_grp.std()), 2),
        },
    ])
 
 
def imputar_por_grupo_con_flag(
    df: pd.DataFrame,
    cols_numericas: list[str],
    cols_categoricas: list[str],
    col_grupo_num: str = "region",
    col_grupo_cat: str = "id_rubro",
) -> pd.DataFrame:
    """
    Imputa variables numéricas con la mediana de su región y variables categóricas
    con la moda de su rubro, creando columnas binarias '<col>_imputado' (0/1).
    """
    df_out = df.copy()
 
    for col in cols_numericas:
        if df_out[col].isna().sum() > 0:
            df_out[f"{col}_imputado"] = df_out[col].isna().astype(int)
            medianas_grupo = df_out.groupby(col_grupo_num)[col].transform("median")
            df_out[col] = df_out[col].fillna(medianas_grupo).fillna(df_out[col].median())
 
    for col in cols_categoricas:
        if df_out[col].isna().sum() > 0:
            df_out[f"{col}_imputado"] = df_out[col].isna().astype(int)
            modas_grupo = df_out.groupby(col_grupo_cat)[col].transform(
                lambda s: s.mode().iloc[0] if not s.mode().empty else np.nan
            )
            moda_global = df_out[col].mode().iloc[0]
            df_out[col] = df_out[col].fillna(modas_grupo).fillna(moda_global)
 
    return df_out
