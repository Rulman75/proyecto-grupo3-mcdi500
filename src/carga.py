"""
Módulo de carga segura, verificación de esquema y diagnóstico estadístico inicial.
Compartido por los notebooks de Fase 2 y Fase 3 (Proyecto Grupo 3 - MCDI500).
"""

from pathlib import Path
import numpy as np
import pandas as pd

COLUMNAS_ESPERADAS_RETC = [
    "año", "id_vu", "rut_razon_social", "id_ciiu4", "ciiu4",
    "id_ciiu6", "ciiu6", "id_rubro", "rubro", "codigo_territorial",
    "comuna", "provincia", "region", "latitud", "longitud",
    "cantidad_kg", "id_peligrosidad", "peligrosidad", "id_lista_a",
    "id_estado_materia", "estado_materia",
]


def cargar_datos_seguro(
    ruta_archivo: str | Path,
    columnas_esperadas: list[str] | None = None,
) -> pd.DataFrame:
    """
    Carga un archivo Excel (.xlsx) o CSV validando su existencia, contenido no vacío
    y correspondencia de columnas esperadas.
    """
    ruta = Path(ruta_archivo)
    try:
        if not ruta.exists():
            raise FileNotFoundError(
                f"El archivo no existe en '{ruta}'. Descárguelo desde https://datos.gob.cl/dataset/generacion-de-residuos-peligrosos "
                "y ubíquelo en F1/data/raw/Base_Maestra_2023_2025.xlsx según las instrucciones del README.md."
            )
        if ruta.suffix.lower() in {".xlsx", ".xls"}:
            df = pd.read_excel(ruta)
        elif ruta.suffix.lower() == ".csv":
            df = pd.read_csv(ruta, encoding="utf-8")
        else:
            raise ValueError(f"Formato de archivo no soportado: '{ruta.suffix}'. Use .xlsx o .csv.")

        if df.empty:
            raise ValueError(f"El archivo '{ruta.name}' está vacío (0 filas).")

        if columnas_esperadas is not None:
            faltantes = [c for c in columnas_esperadas if c not in df.columns]
            if faltantes:
                raise KeyError(f"Faltan columnas obligatorias en '{ruta.name}': {faltantes}")

        return df
    except (FileNotFoundError, ValueError, KeyError) as err:
        print(f"[ERROR DE VALIDACIÓN EN CARGA] {err}")
        raise


def diagnosticar_variables(df: pd.DataFrame) -> pd.DataFrame:
    """
    Recorre las columnas del DataFrame cuantificando tipo de dato, cardinalidad,
    valores faltantes y proporción de valores atípicos según criterio 1.5 * RIC.
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
            if not s_limpia.empty:
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
