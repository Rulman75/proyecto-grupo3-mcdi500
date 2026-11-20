"""
Comunicación de resultados (Fase 4 — Semana 3, Grupo 3 MCDI500):
Del conjunto procesado en la Fase 3 a la copia interpretable con unidades y categorías
originales para construir visualizaciones explicativas, calcular intervalos de confianza
de Wilson y verificar la fidelidad contra los datos de origen.
"""

import ast
import math
from pathlib import Path
import numpy as np
import pandas as pd


ARTEFACTOS_F3 = {
    "entrenamiento": "entrenamiento_f3.csv",
    "prueba": "prueba_f3.csv",
    "diccionario": "diccionario_f3.csv",
    "parametros": "parametros_f3.csv",
}


def exportar_artefactos_f3(
    df_entrenamiento: pd.DataFrame,
    df_prueba: pd.DataFrame,
    pipeline_ajustado: object,
    carpeta_destino: str | Path = "F2/data/processed",
) -> dict[str, Path]:
    """
    Exporta los cuatro artefactos formales que conectan el Pipeline POO de la Fase 3
    con el cuaderno de visualización y comunicación de la Fase 4:
    1) entrenamiento_f3.csv, 2) prueba_f3.csv, 3) diccionario_f3.csv y 4) parametros_f3.csv.
    """
    carpeta = Path(carpeta_destino)
    carpeta.mkdir(parents=True, exist_ok=True)

    ruta_train = carpeta / ARTEFACTOS_F3["entrenamiento"]
    ruta_test = carpeta / ARTEFACTOS_F3["prueba"]
    ruta_dicc = carpeta / ARTEFACTOS_F3["diccionario"]
    ruta_params = carpeta / ARTEFACTOS_F3["parametros"]

    df_entrenamiento.to_csv(ruta_train, index=False, encoding="utf-8")
    df_prueba.to_csv(ruta_test, index=False, encoding="utf-8")

    df_dicc = pd.DataFrame({
        "orden": range(1, len(df_entrenamiento.columns) + 1),
        "columna": list(df_entrenamiento.columns),
        "dtype": [str(t) for t in df_entrenamiento.dtypes],
    })
    df_dicc.to_csv(ruta_dicc, index=False, encoding="utf-8")

    filas_params = []
    for paso in pipeline_ajustado.pasos:
        p = paso.parametros
        if "frec_rut_anon" in p:
            p = dict(p)
            p["frec_rut_anon"] = {"resumen_anonimizado": len(p["frec_rut_anon"])}
        filas_params.append({
            "paso": paso.nombre,
            "repr_paso": repr(paso),
            "parametros": repr(p),
        })
    pd.DataFrame(filas_params).to_csv(ruta_params, index=False, encoding="utf-8")

    return {
        "entrenamiento": ruta_train,
        "prueba": ruta_test,
        "diccionario": ruta_dicc,
        "parametros": ruta_params,
    }


def cargar_artefactos(carpeta: str | Path = "F2/data/processed") -> dict[str, pd.DataFrame]:
    """
    Lee los cuatro artefactos que entrega la Fase 3.
    Si falta alguno, lanza FileNotFoundError indicando qué cuaderno ejecutar.
    """
    ruta_carpeta = Path(carpeta)
    faltantes = [
        archivo for archivo in ARTEFACTOS_F3.values()
        if not (ruta_carpeta / archivo).exists()
    ]
    if faltantes:
        raise FileNotFoundError(
            f"Faltan artefactos de la Fase 3 en '{ruta_carpeta.as_posix()}': {faltantes}. "
            "Ejecute primero F3/notebooks/F3_NucleoAlgoritmico_POO.ipynb."
        )
    return {
        nombre: pd.read_csv(ruta_carpeta / archivo, encoding="utf-8")
        for nombre, archivo in ARTEFACTOS_F3.items()
    }


def leer_parametros(tabla_parametros: pd.DataFrame) -> dict:
    """
    Convierte la tabla de parámetros de la Fase 3 en un diccionario seguro en memoria
    empleando ast.literal_eval (sin ejecutar código arbitrario).
    """
    parametros = {}
    for _, fila in tabla_parametros.iterrows():
        try:
            parametros[str(fila["paso"])] = ast.literal_eval(str(fila["parametros"]))
        except (ValueError, SyntaxError) as error:
            raise ValueError(
                f"Parámetros ilegibles en el paso {fila['paso']}: {fila['parametros']!r}"
            ) from error
    return parametros


def revertir_escalamiento(df: pd.DataFrame, parametros: dict) -> pd.DataFrame:
    """
    Devuelve una copia con las variables continuas recuperadas en sus unidades originales
    invirtiendo exactamente la fórmula de EscaladorRobusto:
        x_original = x_rob * ric + mediana
    """
    if "EscaladorRobusto" not in parametros:
        raise KeyError("No se encontraron los parámetros de 'EscaladorRobusto' en el diccionario.")
    resultado = df.copy()
    stats_escalador = parametros["EscaladorRobusto"]
    for col, info in stats_escalador.items():
        col_rob = f"{col}_rob"
        if col_rob not in resultado.columns:
            raise KeyError(f"Falta la columna escalada '{col_rob}' para revertir '{col}'.")
        resultado[f"{col}_revertida"] = resultado[col_rob] * float(info["ric"]) + float(info["mediana"])
    return resultado


def reconstruir_categorias(df: pd.DataFrame, parametros: dict) -> pd.DataFrame:
    """
    Reconstruye las variables categóricas legibles ('region', 'estado_materia' y 'comuna_agrupada')
    a partir de las columnas indicadoras One-Hot (0/1) usando el vocabulario aprendido en Fase 3.
    Verifica que cada fila tenga exactamente una categoría activa por grupo.
    """
    if "CodificadorCategorias" not in parametros:
        raise KeyError("No se encontraron los parámetros de 'CodificadorCategorias' en el diccionario.")
    resultado = df.copy()
    p_cod = parametros["CodificadorCategorias"]

    bloques = [
        ("region", "reg_", p_cod["cats_region"]),
        ("estado_materia", "estado_", p_cod["cats_estado"]),
        ("comuna_agrupada", "comuna_top_", p_cod["cats_comuna_top"]),
    ]
    for nombre_col, prefijo, categorias in bloques:
        mapa_cols = {f"{prefijo}{cat}": cat for cat in categorias}
        faltantes = [c for c in mapa_cols if c not in resultado.columns]
        if faltantes:
            raise KeyError(f"Faltan columnas indicadoras para reconstruir '{nombre_col}': {faltantes}")
        sub_bloque = resultado[list(mapa_cols.keys())]
        if not (sub_bloque.sum(axis=1) == 1).all():
            raise ValueError(f"En '{nombre_col}' existen filas sin exactamente una categoría activa (suma != 1).")
        resultado[nombre_col] = sub_bloque.idxmax(axis=1).map(mapa_cols)

    # Reconstruir la glosa sectorial 'rubro_nombre' directamente desde los parámetros aprendidos en Fase 3
    if "ImputadorPorGrupo" in parametros and "id_rubro" in resultado.columns:
        info_rubro = parametros["ImputadorPorGrupo"].get("categoricas", {}).get("rubro", {})
        mapa_rubro = {int(k): str(v) for k, v in info_rubro.get("por_grupo", {}).items()}
        respaldo_rubro = str(info_rubro.get("respaldo", "Otros"))
        resultado["rubro_nombre"] = resultado["id_rubro"].map(mapa_rubro).fillna(respaldo_rubro)

    return resultado


def copia_interpretable(df: pd.DataFrame, parametros: dict) -> pd.DataFrame:
    """
    Construye la copia interpretable para visualización y comunicación en Fase 4:
    1) Invierte el escalamiento robusto recuperando las unidades físicas originales (kg, grados).
    2) Reconstruye las etiquetas categóricas ('region', 'estado_materia', 'comuna_agrupada').
    3) Agrega etiquetas legibles para trayectoria de persistencia y condición de gran generador.
    """
    df_rev = revertir_escalamiento(df, parametros)
    df_leg = reconstruir_categorias(df_rev, parametros)

    mapa_trayectoria = {
        3: "Núcleo persistente (3 años)",
        2: "Intermitente (2 años)",
        1: "Ocasional: entra o sale (1 año)",
    }
    if "n_anios_declarados_vu" in df_leg.columns:
        df_leg["trayectoria_vu"] = df_leg["n_anios_declarados_vu"].map(mapa_trayectoria)
    if "es_gran_generador_bin" in df_leg.columns:
        df_leg["categoria_generador"] = np.where(
            df_leg["es_gran_generador_bin"] == 1,
            "Gran Generador (>= 12 t/año)",
            "Pequeño / Mediano (< 12 t/año)",
        )
    if "cantidad_kg" in df_leg.columns:
        df_leg["cantidad_ton"] = df_leg["cantidad_kg"] / 1000.0
    return df_leg


def intervalo_wilson(exitos: int, total: int, z: float = 1.96) -> tuple[float, float]:
    """
    Calcula el intervalo de confianza de Wilson al 95 % para una proporción binomial.
    Garantiza límites dentro de [0, 1] incluso con proporciones pequeñas o tamaños asimétricos.
    """
    if total <= 0:
        raise ValueError("No se puede estimar una proporción con total <= 0 observaciones.")
    if exitos < 0 or exitos > total:
        raise ValueError("El número de éxitos debe estar entre 0 y total.")
    p = exitos / total
    denominador = 1.0 + (z ** 2) / total
    centro = (p + (z ** 2) / (2.0 * total)) / denominador
    margen = (z * math.sqrt((p * (1.0 - p) / total) + ((z ** 2) / (4.0 * (total ** 2))))) / denominador
    inferior = 0.0 if exitos == 0 else max(0.0, centro - margen)
    superior = 1.0 if exitos == total else min(1.0, centro + margen)
    return round(inferior, 6), round(superior, 6)


def tasa_por_grupo(df: pd.DataFrame, grupo: str, objetivo: str) -> pd.DataFrame:
    """
    Calcula la tasa de un evento binario por grupo junto con el tamaño muestral (n)
    y su intervalo de confianza de Wilson al 95 %.
    """
    if df.empty:
        raise ValueError("El DataFrame está vacío.")
    filas = []
    for valor, sub in df.groupby(grupo, observed=True):
        n = len(sub)
        casos = int(sub[objetivo].sum())
        inf, sup = intervalo_wilson(casos, n)
        filas.append({
            grupo: valor,
            "n": n,
            "casos": casos,
            "tasa": casos / n,
            "ic_inferior": inf,
            "ic_superior": sup,
        })
    return pd.DataFrame(filas)


def guardar_figura(figura: object, carpeta: str | Path, nombre: str, dpi: int = 200) -> Path:
    """Guarda una figura de Matplotlib en formato PNG a 200 ppp y devuelve su ruta."""
    ruta_dir = Path(carpeta)
    ruta_dir.mkdir(parents=True, exist_ok=True)
    ruta_archivo = ruta_dir / f"{nombre}.png"
    figura.savefig(ruta_archivo, dpi=dpi, bbox_inches="tight")
    return ruta_archivo