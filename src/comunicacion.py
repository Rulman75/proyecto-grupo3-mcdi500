"""
Comunicación de resultados (Fase 4 — Semana 3, Grupo 3 MCDI500):
Del conjunto procesado en la Fase 3 a la copia interpretable con unidades y categorías
originales para construir visualizaciones explicativas, agregar por establecimiento único
independiente (id_vu), descomponer la variación interanual (persistentes, entrantes y salientes),
calcular curvas de Lorenz / índice de Gini e intervalos de confianza de Wilson al 95 %.
"""

import ast
import hashlib
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

SHA256_BASE_MAESTRA_OFICIAL = "7de8ff0ed46488dcc52a551788d12bc3e9c6599a7b9afd1c30eb1139c60dc44b"

REGIONES_MACROZONA_NORTE = {
    "Arica y Parinacota",
    "Tarapacá",
    "Antofagasta",
    "Atacama",
    "Coquimbo",
}


def fmt_miles(valor: int | float) -> str:
    """Formatea un entero con punto como separador de miles (convención en español)."""
    return f"{int(round(float(valor))):,}".replace(",", ".")


def fmt_dec(valor: float, decimales: int = 1) -> str:
    """Formatea un número decimal con punto de miles y coma decimal (convención en español)."""
    texto = f"{float(valor):,.{decimales}f}"
    return texto.replace(",", "_").replace(".", ",").replace("_", ".")


def fmt_pct(valor: float, decimales: int = 1) -> str:
    """Formatea un porcentaje con coma decimal (ej. 55,7 %)."""
    return f"{fmt_dec(valor, decimales)} %"


def verificar_sha256_origen(
    ruta_excel: str | Path,
    sha256_esperado: str = SHA256_BASE_MAESTRA_OFICIAL,
) -> str:
    """
    Calcula y verifica la huella criptográfica SHA-256 del archivo Excel de origen
    (Base_Maestra_2023_2025.xlsx) para garantizar trazabilidad e integridad bit a bit.
    """
    ruta = Path(ruta_excel)
    if not ruta.exists():
        raise FileNotFoundError(f"No se encontró el archivo de origen en: {ruta.as_posix()}")
    hash_calculado = hashlib.sha256(ruta.read_bytes()).hexdigest()
    if sha256_esperado and hash_calculado.lower() != sha256_esperado.lower():
        raise ValueError(
            f"La huella SHA-256 de '{ruta.name}' ({hash_calculado}) no coincide con la oficial ({sha256_esperado})."
        )
    return hash_calculado


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
    empleando ast.literal_eval (normalizando previamente valores nan a None).
    """
    parametros = {}
    for _, fila in tabla_parametros.iterrows():
        try:
            texto_limpio = str(fila["parametros"]).replace(": nan,", ": None,").replace(": nan}", ": None}")
            parametros[str(fila["paso"])] = ast.literal_eval(texto_limpio)
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

    if "ImputadorPorGrupo" in parametros and "id_rubro" in resultado.columns:
        info_rubro = parametros["ImputadorPorGrupo"].get("categoricas", {}).get("rubro", {})
        mapa_rubro = {
            int(k): str(v)
            for k, v in info_rubro.get("por_grupo", {}).items()
            if v is not None and str(v) != "nan"
        }
        respaldo_rubro = str(info_rubro.get("respaldo", "Otras actividades"))
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


def resumir_por_establecimiento(
    df_legible: pd.DataFrame,
    umbral_ton_anual: float = 12.0,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Consolida las declaraciones a dos unidades de análisis sin correlación intra-declaración:
    1) df_establecimientos (1 fila por id_vu, N = 12.189 observaciones independientes):
       define 'es_gran_generador_planta' = 1 si la suma anual del establecimiento es >= 12 t/año
       en al menos un año del período (D.S. N° 148 Art. 25), junto con macrozona, sector y persistencia.
    2) df_establecimiento_anio (1 fila por par id_vu-año, N = 28.099).
    """
    if df_legible.empty:
        raise ValueError("El DataFrame para resumir por establecimiento está vacío.")
    col_ton = "cantidad_ton" if "cantidad_ton" in df_legible.columns else "cantidad_kg"
    factor = 1.0 if col_ton == "cantidad_ton" else 0.001

    est_anio = df_legible.groupby(["id_vu", "año"], as_index=False).agg(
        ton_anual=(col_ton, lambda s: float(s.sum()) * factor),
        n_declaraciones_anio=(col_ton, "count"),
        n_anios_declarados_vu=("n_anios_declarados_vu", "first"),
        trayectoria_vu=("trayectoria_vu", "first"),
        region=("region", "first"),
        rubro_nombre=("rubro_nombre", "first"),
        id_rubro=("id_rubro", "first"),
        codigo_territorial=("codigo_territorial", "first"),
        es_gran_generador_decl=("es_gran_generador_bin", "max"),
    )
    est_anio["es_gran_generador_anual"] = (est_anio["ton_anual"] >= float(umbral_ton_anual)).astype(int)

    est = est_anio.groupby("id_vu", as_index=False).agg(
        ton_total_trienio=("ton_anual", "sum"),
        ton_anual_max=("ton_anual", "max"),
        ton_anual_media=("ton_anual", "mean"),
        n_declaraciones_total=("n_declaraciones_anio", "sum"),
        n_anios_declarados_vu=("n_anios_declarados_vu", "first"),
        trayectoria_vu=("trayectoria_vu", "first"),
        region=("region", "first"),
        rubro_nombre=("rubro_nombre", "first"),
        id_rubro=("id_rubro", "first"),
        codigo_territorial=("codigo_territorial", "first"),
        es_gran_generador_planta=("es_gran_generador_anual", "max"),
        es_gran_generador_decl_alguna=("es_gran_generador_decl", "max"),
    )
    est["es_nucleo_persistente"] = (est["n_anios_declarados_vu"] == 3).astype(int)
    est["grupo_persistencia_bin"] = np.where(
        est["es_nucleo_persistente"] == 1,
        "Núcleo persistente (3 años)",
        "No persistente (1–2 años)",
    )
    est["sector_minero_bin"] = np.where(
        est["rubro_nombre"] == "Minería",
        "Minería",
        "Otros 18 rubros no mineros",
    )
    est["macrozona"] = np.where(
        est["region"].isin(REGIONES_MACROZONA_NORTE),
        "Macrozona Norte Minera (5 reg.)",
        "Resto del país (11 reg.)",
    )
    return est, est_anio


def descomponer_cambio_interanual(
    df_legible: pd.DataFrame,
    anio_inicio: int,
    anio_fin: int,
    excluir_ids: list[int] | set[int] | None = None,
) -> dict[str, float | int]:
    """
    Descompone exactamente la variación del volumen total entre anio_inicio y anio_fin en:
        cambio_total = variacion_persistentes + volumen_entrantes - volumen_salientes
    Clasifica a los establecimientos (id_vu) del par de años en:
    - persistentes: declaran en ambos años (anio_inicio y anio_fin)
    - entrantes: declaran solo en anio_fin
    - salientes: declaran solo en anio_inicio
    Verifica por contrato (assert) la identidad contable exacta.
    """
    col_ton = "cantidad_ton" if "cantidad_ton" in df_legible.columns else "cantidad_kg"
    factor = 1.0 if col_ton == "cantidad_ton" else 0.001

    datos = df_legible
    if excluir_ids is not None and len(excluir_ids) > 0:
        datos = datos[~datos["id_vu"].isin(set(excluir_ids))]

    s_ini = (
        datos[datos["año"] == anio_inicio]
        .groupby("id_vu")[col_ton]
        .sum()
        .mul(factor)
    )
    s_fin = (
        datos[datos["año"] == anio_fin]
        .groupby("id_vu")[col_ton]
        .sum()
        .mul(factor)
    )

    ids_persistentes = s_ini.index.intersection(s_fin.index)
    ids_entrantes = s_fin.index.difference(s_ini.index)
    ids_salientes = s_ini.index.difference(s_fin.index)

    vol_ini = float(s_ini.sum())
    vol_fin = float(s_fin.sum())
    cambio_total = vol_fin - vol_ini

    var_persistentes = float(s_fin.loc[ids_persistentes].sum() - s_ini.loc[ids_persistentes].sum())
    vol_entrantes = float(s_fin.loc[ids_entrantes].sum())
    vol_salientes = float(s_ini.loc[ids_salientes].sum())

    suma_componentes = var_persistentes + vol_entrantes - vol_salientes
    if not np.isclose(cambio_total, suma_componentes, atol=1e-6):
        raise AssertionError(
            f"Fallo de identidad en descomposición {anio_inicio}->{anio_fin}: "
            f"cambio_total={cambio_total} != {suma_componentes}"
        )

    return {
        "anio_inicio": int(anio_inicio),
        "anio_fin": int(anio_fin),
        "vol_inicio_ton": round(vol_ini, 4),
        "vol_fin_ton": round(vol_fin, 4),
        "cambio_total_ton": round(cambio_total, 4),
        "variacion_persistentes_ton": round(var_persistentes, 4),
        "volumen_entrantes_ton": round(vol_entrantes, 4),
        "volumen_salientes_ton": round(vol_salientes, 4),
        "n_persistentes": int(len(ids_persistentes)),
        "n_entrantes": int(len(ids_entrantes)),
        "n_salientes": int(len(ids_salientes)),
    }


def calcular_concentracion_y_lorenz(
    volumenes: pd.Series | np.ndarray,
) -> dict[str, object]:
    """
    Calcula las métricas de concentración extrema de volumen por establecimiento:
    - Participación (%) y tonelaje del Top 1 %, Top 5 % y Top 10 % superior.
    - Índice de concentración de Gini en [0, 1].
    - Mediana y rango intercuartílico (Q25, Q75).
    - Coordenadas (x_lorenz, y_lorenz) de la curva de Lorenz desde (0, 0) hasta (1, 1).
    """
    arr = np.asarray(volumenes, dtype=float)
    arr = arr[~np.isnan(arr)]
    if arr.size == 0 or float(arr.sum()) <= 0.0:
        raise ValueError("La serie de volúmenes debe ser no vacía y con suma positiva.")

    n = int(arr.size)
    total = float(arr.sum())
    desc = np.sort(arr)[::-1]
    asc = desc[::-1]

    k1 = max(1, int(round(0.01 * n)))
    k5 = max(1, int(round(0.05 * n)))
    k10 = max(1, int(round(0.10 * n)))

    idx = np.arange(1, n + 1, dtype=float)
    gini = float((2.0 * np.sum(idx * asc) / (n * total)) - ((n + 1.0) / n))

    x_lorenz = np.concatenate([[0.0], idx / n])
    y_lorenz = np.concatenate([[0.0], np.cumsum(asc) / total])

    return {
        "n_establecimientos": n,
        "volumen_total": round(total, 4),
        "n_top1_pct": k1,
        "ton_top1_pct": round(float(desc[:k1].sum()), 4),
        "share_top1_pct": round(float(desc[:k1].sum() / total * 100.0), 4),
        "n_top5_pct": k5,
        "ton_top5_pct": round(float(desc[:k5].sum()), 4),
        "share_top5_pct": round(float(desc[:k5].sum() / total * 100.0), 4),
        "n_top10_pct": k10,
        "ton_top10_pct": round(float(desc[:k10].sum()), 4),
        "share_top10_pct": round(float(desc[:k10].sum() / total * 100.0), 4),
        "gini": round(gini, 6),
        "mediana": round(float(np.median(arr)), 4),
        "q25": round(float(np.percentile(arr, 25)), 4),
        "q75": round(float(np.percentile(arr, 75)), 4),
        "x_lorenz": x_lorenz,
        "y_lorenz": y_lorenz,
    }


def auditar_rotacion_administrativa(
    df_legible: pd.DataFrame,
    anio_inicio: int,
    anio_fin: int,
) -> dict[str, int | float]:
    """
    Evalúa cuántos establecimientos clasificados como 'salientes' en anio_inicio y
    'entrantes' en anio_fin coinciden simultáneamente en (codigo_territorial, frecuencia_rut, id_rubro),
    permitiendo acotar posibles cambios administrativos de identificador id_vu.
    """
    col_ton = "cantidad_ton" if "cantidad_ton" in df_legible.columns else "cantidad_kg"
    factor = 1.0 if col_ton == "cantidad_ton" else 0.001
    col_frec = (
        "frecuencia_declaraciones_rut_revertida"
        if "frecuencia_declaraciones_rut_revertida" in df_legible.columns
        else "frecuencia_declaraciones_rut"
    )

    est_a = df_legible.groupby(["id_vu", "año"], as_index=False).agg(
        ton=(col_ton, lambda s: float(s.sum()) * factor),
        comuna=("codigo_territorial", "first"),
        rubro=("id_rubro", "first"),
        frec_rut=(col_frec, lambda s: int(round(float(s.iloc[0])))),
    )
    e1 = est_a[est_a["año"] == anio_inicio]
    e2 = est_a[est_a["año"] == anio_fin]
    sal = e1[~e1["id_vu"].isin(e2["id_vu"])]
    ent = e2[~e2["id_vu"].isin(e1["id_vu"])]

    claves_sal = set(zip(sal["comuna"], sal["frec_rut"], sal["rubro"]))
    claves_ent = set(zip(ent["comuna"], ent["frec_rut"], ent["rubro"]))
    comunes = claves_sal.intersection(claves_ent)

    sal_match = sal[sal.set_index(["comuna", "frec_rut", "rubro"]).index.isin(comunes)]
    ent_match = ent[ent.set_index(["comuna", "frec_rut", "rubro"]).index.isin(comunes)]

    return {
        "anio_inicio": int(anio_inicio),
        "anio_fin": int(anio_fin),
        "n_salientes": int(len(sal)),
        "n_entrantes": int(len(ent)),
        "ternas_coincidentes": int(len(comunes)),
        "salientes_coincidentes": int(len(sal_match)),
        "entrantes_coincidentes": int(len(ent_match)),
        "ton_salientes_coincidentes": round(float(sal_match["ton"].sum()), 2),
        "ton_entrantes_coincidentes": round(float(ent_match["ton"].sum()), 2),
    }


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