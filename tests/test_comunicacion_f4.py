"""
Pruebas unitarias automatizadas para el módulo `src/comunicacion.py` (Fase 4).
Incluye pruebas sobre tablas pequeñas hechas a mano para reversión de escalamiento,
reconstrucción de categorías, intervalo de Wilson, descomposición interanual exacta
(persistentes + entrantes - salientes), curva de Lorenz / Gini y agregación independiente
por establecimiento único (id_vu).
"""

import numpy as np
import pandas as pd
import pytest

from src.comunicacion import (
    cargar_artefactos,
    revertir_escalamiento,
    reconstruir_categorias,
    intervalo_wilson,
    descomponer_cambio_interanual,
    calcular_concentracion_y_lorenz,
    resumir_por_establecimiento,
)


def test_revertir_escalamiento_recupera_unidades_originales():
    """Comprueba que x_rob * ric + mediana recupera exactamente los valores originales."""
    df_sintetico = pd.DataFrame({
        "cantidad_kg_rob": [0.0, 1.0, -0.5, 10.0],
        "latitud_rob": [0.0, -1.0, 0.5, 2.0],
    })
    parametros = {
        "EscaladorRobusto": {
            "cantidad_kg": {"mediana": 200.0, "ric": 1000.0},
            "latitud": {"mediana": -33.45, "ric": 2.0},
        }
    }
    rev = revertir_escalamiento(df_sintetico, parametros)
    assert np.allclose(rev["cantidad_kg_revertida"], [200.0, 1200.0, -300.0, 10200.0])
    assert np.allclose(rev["latitud_revertida"], [-33.45, -35.45, -32.45, -29.45])


def test_reconstruir_categorias_valida_one_hot_y_detecta_inconsistencia():
    """Verifica la reconstrucción de etiquetas desde One-Hot y el rechazo de filas con suma != 1."""
    df_ok = pd.DataFrame({
        "id_rubro": [4, 20],
        "reg_Antofagasta": [1, 0],
        "reg_Metropolitana": [0, 1],
        "estado_Solido": [1, 0],
        "estado_Liquido": [0, 1],
        "comuna_top_Antofagasta": [1, 0],
        "comuna_top_Santiago": [0, 1],
    })
    parametros = {
        "CodificadorCategorias": {
            "cats_region": ["Antofagasta", "Metropolitana"],
            "cats_estado": ["Solido", "Liquido"],
            "cats_comuna_top": ["Antofagasta", "Santiago"],
        },
        "ImputadorPorGrupo": {
            "categoricas": {
                "rubro": {
                    "por_grupo": {4: "Minería", 20: "Otras actividades"},
                    "respaldo": "Otras actividades",
                }
            }
        },
    }
    rec = reconstruir_categorias(df_ok, parametros)
    assert list(rec["region"]) == ["Antofagasta", "Metropolitana"]
    assert list(rec["rubro_nombre"]) == ["Minería", "Otras actividades"]

    df_malo = df_ok.copy()
    df_malo.loc[0, "reg_Metropolitana"] = 1  # Suma 2 en la primera fila
    with pytest.raises(ValueError, match="exactamente una categoría activa"):
        reconstruir_categorias(df_malo, parametros)


def test_intervalo_wilson_limites_y_excepciones():
    """Comprueba que el intervalo de Wilson se mantiene en [0, 1] y rechaza entradas inválidas."""
    inf_0, sup_0 = intervalo_wilson(0, 50)
    inf_1, sup_1 = intervalo_wilson(50, 50)
    assert 0.0 <= inf_0 < sup_0 <= 1.0
    assert 0.0 <= inf_1 < sup_1 <= 1.0

    with pytest.raises(ValueError, match="total <= 0"):
        intervalo_wilson(0, 0)
    with pytest.raises(ValueError, match="entre 0 y total"):
        intervalo_wilson(12, 10)


def test_cargar_artefactos_lanza_error_claro_si_carpeta_vacia(tmp_path):
    """Comprueba que cargar_artefactos lanza FileNotFoundError explícito si faltan los CSV de F3."""
    with pytest.raises(FileNotFoundError, match="Faltan artefactos de la Fase 3"):
        cargar_artefactos(tmp_path)


def test_descomponer_cambio_interanual_identidad_exacta():
    """
    Prueba sobre una tabla pequeña de resultado conocido de antemano:
    - id_vu=101 (persistente): pasa de 10 t en 2023 a 15 t en 2024 -> variación = +5 t
    - id_vu=102 (saliente): declara 4 t en 2023 y no declara en 2024 -> salientes = 4 t
    - id_vu=103 (entrante): no declara en 2023 y declara 8 t en 2024 -> entrantes = 8 t
    Cambio total = (15 + 8) - (10 + 4) = 23 - 14 = +9 t == (+5) + (+8) - (4).
    """
    df_pequeno = pd.DataFrame({
        "id_vu": [101, 102, 101, 103],
        "año": [2023, 2023, 2024, 2024],
        "cantidad_ton": [10.0, 4.0, 15.0, 8.0],
    })
    res = descomponer_cambio_interanual(df_pequeno, 2023, 2024)
    assert res["vol_inicio_ton"] == 14.0
    assert res["vol_fin_ton"] == 23.0
    assert res["cambio_total_ton"] == 9.0
    assert res["variacion_persistentes_ton"] == 5.0
    assert res["volumen_entrantes_ton"] == 8.0
    assert res["volumen_salientes_ton"] == 4.0
    assert res["n_persistentes"] == 1
    assert res["n_entrantes"] == 1
    assert res["n_salientes"] == 1


def test_calcular_concentracion_y_lorenz_tabla_conocida():
    """
    Prueba con 10 establecimientos donde 1 concentra 90 t y los otros 9 suman 10 t (total = 100 t).
    El Top 10 % (1 establecimiento) debe concentrar exactamente el 90,0 % del volumen.
    """
    vols = pd.Series([90.0] + [10.0 / 9.0] * 9)
    res = calcular_concentracion_y_lorenz(vols)
    assert res["n_establecimientos"] == 10
    assert np.isclose(res["volumen_total"], 100.0)
    assert np.isclose(res["share_top10_pct"], 90.0)
    assert 0.70 < res["gini"] < 0.90
    assert res["x_lorenz"][0] == 0.0 and res["x_lorenz"][-1] == 1.0
    assert res["y_lorenz"][0] == 0.0 and np.isclose(res["y_lorenz"][-1], 1.0)


def test_resumir_por_establecimiento_independencia():
    """
    Comprueba que múltiples declaraciones de un mismo establecimiento en un año se suman
    antes de evaluar el umbral de Gran Generador (>= 12 t/año) y que cada id_vu queda en 1 fila.
    """
    df_decl = pd.DataFrame({
        "id_vu": [1, 1, 1, 2],
        "año": [2023, 2023, 2024, 2023],
        "cantidad_ton": [7.0, 6.0, 2.0, 5.0],  # id_vu=1 suma 13 t en 2023 (>=12 t/año)
        "n_anios_declarados_vu": [2, 2, 2, 1],
        "trayectoria_vu": ["Intermitente (2 años)"] * 3 + ["Ocasional: entra o sale (1 año)"],
        "region": ["Antofagasta", "Antofagasta", "Antofagasta", "Maule"],
        "rubro_nombre": ["Minería", "Minería", "Minería", "Construcción"],
        "id_rubro": [4, 4, 4, 16],
        "codigo_territorial": [2101, 2101, 2101, 7101],
        "es_gran_generador_bin": [0, 0, 0, 0],
    })
    est, est_anio = resumir_por_establecimiento(df_decl, umbral_ton_anual=12.0)
    assert len(est) == 2
    assert len(est_anio) == 3
    fila_1 = est[est["id_vu"] == 1].iloc[0]
    fila_2 = est[est["id_vu"] == 2].iloc[0]
    assert fila_1["es_gran_generador_planta"] == 1
    assert fila_2["es_gran_generador_planta"] == 0

