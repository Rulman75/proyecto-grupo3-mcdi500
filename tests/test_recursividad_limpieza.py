"""
Pruebas unitarias con pytest para las funciones recursivas (árbol vacío, árbol de un solo nivel
y árbol con valores nulos) y la equivalencia entre la versión funcional y el Pipeline POO.
"""

import numpy as np
import pandas as pd

from src import (
    CodificadorCategorias,
    EscaladorRobusto,
    ImputadorPorGrupo,
    Pipeline,
    aplanar_estructura_recursiva,
    construir_arbol_ciiu,
    preprocesar_version_funcional,
    sumar_volumen_recursivo,
)


def test_recursividad_arbol_vacio():
    """Caso borde 1: Un árbol vacío debe devolver exactamente 0.0."""
    assert sumar_volumen_recursivo({}) == 0.0
    assert sumar_volumen_recursivo(None) == 0.0


def test_recursividad_arbol_un_solo_nivel():
    """Caso borde 2: Un árbol de un solo nivel suma directamente sus hojas."""
    arbol_1_nivel = {"Minería": 120.5, "Industria Manufacturera": 79.5, "Comercio": 50.0}
    assert sumar_volumen_recursivo(arbol_1_nivel) == 250.0


def test_recursividad_arbol_con_valores_nulos():
    """Caso borde 3: Un árbol jerárquico con hojas None o NaN ignora los nulos sin lanzar error."""
    arbol_con_nulos = {
        "Minería": {
            "B0400": {"40001": 100.0, "40002": np.nan, "40003": None},
        },
        "Química": {
            "C2011": {"201101": 50.25},
            "SubarbolVacio": {},
        },
    }
    assert sumar_volumen_recursivo(arbol_con_nulos) == 150.25


def test_aplanar_estructura_recursiva_oculta_ruts_individuales():
    """Verifica que aplanar_estructura_recursiva resuma 'frec_rut_anon' sin expandir RUTs."""
    anidado = {
        "CodificadorCategorias": {
            "top_comunas": ["SANTIAGO"],
            "frec_rut_anon": {"a1b2c3d4": 10, "e5f6g7h8": 5},
        }
    }
    plano = aplanar_estructura_recursiva(anidado)
    assert "CodificadorCategorias.frec_rut_anon.total_entradas_anonimizadas" in plano
    assert plano["CodificadorCategorias.frec_rut_anon.total_entradas_anonimizadas"] == 2


def test_equivalencia_no_circular_funcional_vs_poo():
    """
    Demuestra sobre una tabla sintética que preprocesar_version_funcional (sin clases)
    y el Pipeline POO entregan exactamente el mismo DataFrame.
    """
    df_sintetico = pd.DataFrame({
        "año": [2023, 2024, 2025, 2023, 2024],
        "id_vu": [1, 1, 1, 2, 2],
        "rut_razon_social": ["RUT_1", "RUT_1", "RUT_1", "RUT_2", "RUT_2"],
        "id_ciiu4": ["C2011", "C2011", "C2011", "B0400", None],
        "ciiu4": ["Química", "Química", "Química", "Minería", None],
        "id_ciiu6": [201101.0, 201101.0, 201101.0, 40001.0, np.nan],
        "ciiu6": ["Quim", "Quim", "Quim", "Min", None],
        "id_rubro": [5, 5, 5, 1, 1],
        "rubro": ["Química", "Química", "Química", "Minería", None],
        "codigo_territorial": [13101, 13101, 13101, 2101, 2101],
        "comuna": ["SANTIAGO", "SANTIAGO", "SANTIAGO", "ANTOFAGASTA", "ANTOFAGASTA"],
        "provincia": ["Santiago", "Santiago", "Santiago", "Antofagasta", "Antofagasta"],
        "region": ["Metropolitana", "Metropolitana", "Metropolitana", "Antofagasta", "Antofagasta"],
        "latitud": [-33.45, -33.45, np.nan, -23.65, -23.65],
        "longitud": [-70.66, -70.66, -70.66, -70.40, np.nan],
        "cantidad_kg": [15000.0, 12000.0, np.nan, 500.0, 800.0],
        "id_peligrosidad": ["08,", "08", "08", "06", "06"],
        "peligrosidad": ["tóxico##corrosivo", "CORROSIVO;TOXICO", "TOXICO", "INFLAMABLE", "INFLAMABLE"],
        "id_lista_a": ["A3020", None, "A3020", "A1010", "A1010"],
        "id_estado_materia": [1, 1, 1, 3, 3],
        "estado_materia": ["Líquido", "líquido", "líquido", "Sólido", "sólido"],
    })

    df_func = preprocesar_version_funcional(df_sintetico, top_n_comunas=10)

    from src import (
        agregar_atributos_deterministas,
        depurar_registros_base,
        estandarizar_regiones_y_peligrosidad,
        rescatar_coordenadas_chile,
    )
    df_base = agregar_atributos_deterministas(
        rescatar_coordenadas_chile(
            estandarizar_regiones_y_peligrosidad(depurar_registros_base(df_sintetico))
        )
    )
    pipe = Pipeline([
        ImputadorPorGrupo(
            cols_numericas=["latitud", "longitud"],
            cols_categoricas=["id_lista_a", "id_ciiu4", "ciiu4", "id_ciiu6", "ciiu6", "rubro"],
        ),
        CodificadorCategorias(top_n_comunas=10),
        EscaladorRobusto(
            columnas=["cantidad_kg", "latitud", "longitud", "frecuencia_declaraciones_rut", "n_peligrosidades"],
            descartar_texto=True,
        ),
    ])
    df_poo = pipe.ajustar_transformar(df_base)
    pd.testing.assert_frame_equal(df_func, df_poo)
