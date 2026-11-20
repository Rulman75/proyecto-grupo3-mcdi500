"""
Pruebas unitarias con pytest para el módulo src/comunicacion.py (Fase 4 - Sumativa 3):
Verifica reversión exacta del escalamiento robusto, reconstrucción de categorías desde
One-Hot Encoding, intervalo de confianza de Wilson en casos límite y manejo de errores.
"""

import numpy as np
import pandas as pd
import pytest

from src.comunicacion import (
    cargar_artefactos,
    copia_interpretable,
    intervalo_wilson,
    reconstruir_categorias,
    revertir_escalamiento,
    tasa_por_grupo,
)


def test_revertir_escalamiento_recupera_unidades_originales():
    """Verifica que x_rob * ric + mediana recupere exactamente la magnitud original."""
    df_escalado = pd.DataFrame({
        "cantidad_kg": [100.0, 300.0, 1100.0],
        "cantidad_kg_rob": [-0.5, 0.0, 2.0],
    })
    params = {
        "EscaladorRobusto": {
            "cantidad_kg": {"mediana": 300.0, "ric": 400.0},
        }
    }
    res = revertir_escalamiento(df_escalado, params)
    assert np.allclose(res["cantidad_kg_revertida"], df_escalado["cantidad_kg"])


def test_reconstruir_categorias_desde_one_hot_y_error_suma_invalida():
    """Verifica la reconstrucción de categorías y que lance ValueError si una fila tiene suma != 1."""
    df_oh = pd.DataFrame({
        "reg_Antofagasta": [1, 0],
        "reg_Metropolitana": [0, 1],
        "estado_líquido": [1, 0],
        "estado_sólido": [0, 1],
        "comuna_top_SANTIAGO": [0, 1],
        "comuna_top_OTROS": [1, 0],
    })
    params = {
        "CodificadorCategorias": {
            "cats_region": ["Antofagasta", "Metropolitana"],
            "cats_estado": ["líquido", "sólido"],
            "cats_comuna_top": ["OTROS", "SANTIAGO"],
        }
    }
    rec = reconstruir_categorias(df_oh, params)
    assert list(rec["region"]) == ["Antofagasta", "Metropolitana"]
    assert list(rec["estado_materia"]) == ["líquido", "sólido"]
    assert list(rec["comuna_agrupada"]) == ["OTROS", "SANTIAGO"]

    # Caso de excepción: fila con dos categorías activas a la vez
    df_invalido = df_oh.copy()
    df_invalido.loc[0, "reg_Metropolitana"] = 1
    with pytest.raises(ValueError):
        reconstruir_categorias(df_invalido, params)


def test_intervalo_wilson_casos_borde_y_excepcion():
    """Verifica límites exactos en 0 éxitos, 100 % éxitos y ValueError con total=0."""
    inf_cero, sup_cero = intervalo_wilson(0, 100)
    assert inf_cero == 0.0 and 0.0 < sup_cero < 0.05

    inf_todo, sup_todo = intervalo_wilson(100, 100)
    assert 0.95 < inf_todo < 1.0 and sup_todo == 1.0

    with pytest.raises(ValueError):
        intervalo_wilson(0, 0)


def test_cargar_artefactos_carpeta_inexistente_lanza_file_not_found():
    """Verifica que cargar_artefactos lance FileNotFoundError cuando faltan los archivos de F3."""
    with pytest.raises(FileNotFoundError):
        cargar_artefactos("carpeta_que_no_existe_f4")
