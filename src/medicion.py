"""
Módulo de medición empírica de eficiencia (timeit mínimo + tracemalloc) y funciones recursivas
sobre la jerarquía de actividad económica CIIU y metadatos del Pipeline (Fase 3 - MCDI500).
"""

import timeit
import tracemalloc
from typing import Callable
import pandas as pd


def medir_tiempo_y_memoria(funcion: Callable, repeticiones: int = 5, numero: int = 1) -> dict:
    """
    Ejecuta una función sin argumentos midiendo:
    1) El tiempo mínimo de ejecución en segundos con timeit.repeat (evita ruido del sistema operativo).
    2) El pico de memoria asignada por Python en MB mediante tracemalloc.
    """
    tiempos = timeit.repeat(funcion, repeat=repeticiones, number=numero)
    tiempo_min_s = min(tiempos) / numero

    tracemalloc.start()
    resultado = funcion()
    _, pico_bytes = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    pico_mb = pico_bytes / (1024 * 1024)

    return {
        "resultado": resultado,
        "tiempo_min_s": round(tiempo_min_s, 5),
        "memoria_pico_mb": round(pico_mb, 3),
    }


def comparar_implementaciones(
    nombre_operacion: str,
    version_a: Callable,
    version_b: Callable,
    etiqueta_a: str = "Versión A (Línea base F2)",
    etiqueta_b: str = "Versión B (Optimizada F3)",
    repeticiones: int = 5,
) -> dict:
    """
    Verifica primero la equivalencia funcional entre dos implementaciones y luego compara
    su tiempo mínimo (timeit) y su pico de memoria (tracemalloc).
    """
    med_a = medir_tiempo_y_memoria(version_a, repeticiones=repeticiones)
    med_b = medir_tiempo_y_memoria(version_b, repeticiones=repeticiones)

    res_a, res_b = med_a["resultado"], med_b["resultado"]
    if isinstance(res_a, pd.Series) and isinstance(res_b, pd.Series):
        pd.testing.assert_series_equal(res_a, res_b, check_names=False)
    elif isinstance(res_a, pd.DataFrame) and isinstance(res_b, pd.DataFrame):
        pd.testing.assert_frame_equal(res_a, res_b)
    else:
        assert res_a == res_b, f"Discrepancia de resultados en '{nombre_operacion}'"

    razon_velocidad = round(med_a["tiempo_min_s"] / max(med_b["tiempo_min_s"], 1e-9), 1)
    return {
        "operacion": nombre_operacion,
        "etiqueta_a": etiqueta_a,
        "tiempo_a_s": med_a["tiempo_min_s"],
        "memoria_a_mb": med_a["memoria_pico_mb"],
        "etiqueta_b": etiqueta_b,
        "tiempo_b_s": med_b["tiempo_min_s"],
        "memoria_b_mb": med_b["memoria_pico_mb"],
        "aceleracion_x": razon_velocidad,
        "equivalencia_verificada": True,
    }


def medir_curva_crecimiento(
    df: pd.DataFrame,
    fn_a: Callable[[pd.DataFrame], object],
    fn_b: Callable[[pd.DataFrame], object],
    tamanos: list[int] | None = None,
    repeticiones: int = 3,
) -> pd.DataFrame:
    """Evalúa cómo escalan el tiempo y la memoria de dos implementaciones al crecer N."""
    if tamanos is None:
        tamanos = [1000, 10000, 50000, len(df)]

    filas = []
    for n in tamanos:
        sub_df = df.iloc[: min(n, len(df))].copy()
        m_a = medir_tiempo_y_memoria(lambda: fn_a(sub_df), repeticiones=repeticiones)
        m_b = medir_tiempo_y_memoria(lambda: fn_b(sub_df), repeticiones=repeticiones)
        filas.append({
            "n_filas": len(sub_df),
            "tiempo_a_s": m_a["tiempo_min_s"],
            "tiempo_b_s": m_b["tiempo_min_s"],
            "aceleracion_x": round(m_a["tiempo_min_s"] / max(m_b["tiempo_min_s"], 1e-9), 1),
            "memoria_a_mb": m_a["memoria_pico_mb"],
            "memoria_b_mb": m_b["memoria_pico_mb"],
        })
    return pd.DataFrame(filas)


def persistencia_con_bucle(df: pd.DataFrame) -> pd.Series:
    """Versión iterativa con bucle explícito en Python para contar años declarados por id_vu."""
    anios_por_id: dict[int, set] = {}
    for id_v, anio in zip(df["id_vu"], df["año"]):
        if id_v not in anios_por_id:
            anios_por_id[id_v] = set()
        anios_por_id[id_v].add(anio)
    conteo = {k: len(v) for k, v in anios_por_id.items()}
    return pd.Series([conteo[i] for i in df["id_vu"]], index=df.index, dtype=int)


def persistencia_vectorizada(df: pd.DataFrame) -> pd.Series:
    """Versión vectorizada con groupby + transform('nunique') en Cython/pandas."""
    return df.groupby("id_vu")["año"].transform("nunique").astype(int)


# =====================================================================
# RECURSIVIDAD: Jerarquía CIIU (Rubro -> CIIU4 -> CIIU6) y Metadatos
# =====================================================================

def construir_arbol_ciiu(df: pd.DataFrame) -> dict:
    """
    Construye un árbol jerárquico anidado de 3 niveles de profundidad:
    Nivel 1: Rubro productivo ('rubro') -> Nivel 2: CIIU 4 dígitos ('id_ciiu4')
    -> Nivel 3 (hoja): CIIU 6 dígitos ('id_ciiu6') con su masa declarada total en kg.
    """
    agrupado = (
        df.groupby(["rubro", "id_ciiu4", "id_ciiu6"], as_index=False)["cantidad_kg"]
        .sum()
    )
    arbol: dict = {}
    for row in agrupado.itertuples(index=False):
        r_dict = arbol.setdefault(str(row.rubro), {})
        c4_dict = r_dict.setdefault(str(row.id_ciiu4), {})
        c4_dict[str(row.id_ciiu6)] = float(row.cantidad_kg)
    return arbol


def sumar_volumen_recursivo(nodo: dict | float | int) -> float:
    """
    Recorre recursivamente un árbol jerárquico de profundidad arbitraria sumando las hojas.
    - Caso base: el nodo es un valor numérico (hoja del árbol CIIU6) y devuelve float(nodo).
    - Caso recursivo: el nodo es un diccionario y suma recursivamente cada uno de sus subárboles.
    """
    if not isinstance(nodo, dict):
        return float(nodo)
    return sum(sumar_volumen_recursivo(subnodo) for subnodo in nodo.values())


def aplanar_estructura_recursiva(estructura: dict, prefijo: str = "") -> dict:
    """
    Convierte recursivamente un diccionario anidado de profundidad arbitraria
    en un diccionario plano de claves compuestas 'nivel1.nivel2.clave'.
    """
    plano = {}
    for clave, valor in estructura.items():
        compuesta = f"{prefijo}.{clave}" if prefijo else str(clave)
        if isinstance(valor, dict) and len(valor) > 0:
            plano.update(aplanar_estructura_recursiva(valor, compuesta))
        else:
            plano[compuesta] = valor
    return plano
