"""
Pruebas unitarias con pytest para la jerarquía POO (Transformador ABC, clases hijas,
patrón Strategy, Pipeline polimórfico y patrón Observer con dos observadores).
"""

import numpy as np
import pandas as pd
import pytest

from src import (
    AuditoriaNulosObserver,
    BitacoraObserver,
    CodificadorCategorias,
    EscaladorRobusto,
    EstrategiaImputacion,
    EstrategiaMedianaGlobal,
    EstrategiaMedianaPorGrupo,
    ImputadorFlexible,
    ImputadorPorGrupo,
    Pipeline,
    Transformador,
)


@pytest.fixture
def df_pequeno_retc() -> pd.DataFrame:
    """Construye a mano una tabla pequeña representativa del esquema RETC para pruebas unitarias."""
    return pd.DataFrame({
        "año": [2023, 2024, 2025, 2023, 2024, 2025],
        "id_vu": [10, 10, 10, 20, 20, 30],
        "rut_razon_social": ["EMP_A", "EMP_A", "EMP_A", "EMP_B", "EMP_B", "EMP_C"],
        "id_ciiu4": ["C2011", "C2011", "C2011", "B0400", None, "G4730"],
        "ciiu4": ["Química", "Química", "Química", "Minería", None, "Comercio"],
        "id_ciiu6": [201101.0, 201101.0, 201101.0, 40001.0, np.nan, 473001.0],
        "ciiu6": ["Química base", "Química base", "Química base", "Cobre", None, "Combustibles"],
        "id_rubro": [5, 5, 5, 1, 1, 12],
        "rubro": ["Industria Química", "Industria Química", "Industria Química", "Minería", None, "Comercio"],
        "codigo_territorial": [13101, 13101, 13101, 2101, 2101, 8101],
        "comuna": ["SANTIAGO", "SANTIAGO", "SANTIAGO", "ANTOFAGASTA", "ANTOFAGASTA", "CONCEPCION"],
        "provincia": ["Santiago", "Santiago", "Santiago", "Antofagasta", "Antofagasta", "Concepción"],
        "region": ["Metropolitana", "Metropolitana", "Metropolitana", "Antofagasta", "Antofagasta", "Biobío"],
        "latitud": [-33.45, -33.46, np.nan, -23.65, -23.66, -36.82],
        "longitud": [-70.66, -70.67, -70.65, -70.40, np.nan, -73.05],
        "cantidad_kg": [15000.0, 14000.0, 16000.0, 500.0, 600.0, 120.0],
        "id_peligrosidad": ["08", "08", "08", "06", "06", "05"],
        "peligrosidad": ["TOXICO EXTRINSECO", "TOXICO EXTRINSECO", "TOXICO EXTRINSECO", "CORROSIVO", "CORROSIVO", "INFLAMABLE"],
        "id_lista_a": ["A3020", None, "A3020", "A1010", "A1010", "A4060"],
        "id_estado_materia": [1, 1, 1, 3, 3, 1],
        "estado_materia": ["líquido", "líquido", "líquido", "sólido", "sólido", "líquido"],
        "n_peligrosidades": [1, 1, 1, 1, 1, 1],
    })


def test_clases_base_abstractas_no_instanciables():
    """Verifica que Transformador y EstrategiaImputacion sean clases abstractas (ABC)."""
    with pytest.raises(TypeError):
        Transformador("latitud")  # type: ignore[abstract]
    with pytest.raises(TypeError):
        EstrategiaImputacion()  # type: ignore[abstract]


@pytest.mark.parametrize(
    "instancia",
    [
        ImputadorPorGrupo(cols_numericas=["latitud"], cols_categoricas=["id_lista_a"]),
        CodificadorCategorias(top_n_comunas=2),
        EscaladorRobusto(columnas=["cantidad_kg"]),
        ImputadorFlexible("latitud", estrategia=EstrategiaMedianaGlobal()),
        Pipeline([EscaladorRobusto(columnas=["cantidad_kg"])]),
    ],
)
def test_transformar_sin_ajustar_lanza_runtime_error(instancia, df_pequeno_retc):
    """Cada clase y el Pipeline deben lanzar RuntimeError si se llama a transformar() antes de ajustar()."""
    with pytest.raises(RuntimeError):
        instancia.transformar(df_pequeno_retc)


def test_inmutabilidad_dataframe_entrada_y_encapsulamiento_parametros(df_pequeno_retc):
    """
    Verifica que:
    1) ajustar() y transformar() nunca modifiquen el DataFrame de entrada.
    2) El usuario no pueda alterar los parámetros aprendidos desde fuera (deepcopy y solo lectura).
    """
    copia_original = df_pequeno_retc.copy(deep=True)
    imputador = ImputadorPorGrupo(
        cols_numericas=["latitud", "longitud"],
        cols_categoricas=["id_lista_a", "id_ciiu4", "ciiu4", "id_ciiu6", "ciiu6", "rubro"],
    )
    salida = imputador.ajustar_transformar(df_pequeno_retc)

    # El DataFrame original conserva exactamente sus nulos intactos
    pd.testing.assert_frame_equal(df_pequeno_retc, copia_original)
    assert int(salida.isna().sum().sum()) == 0

    # Intentar sobrescribir la propiedad parametros lanza AttributeError
    with pytest.raises(AttributeError):
        imputador.parametros = {}  # type: ignore[misc]

    # Intentar mutar el diccionario devuelto no altera la mediana interna aprendida
    mediana_real = imputador.parametros["numericas"]["latitud"]["por_grupo"]["Metropolitana"]
    vista_externa = imputador.parametros
    vista_externa["numericas"]["latitud"]["por_grupo"]["Metropolitana"] = 99999.0
    assert imputador.parametros["numericas"]["latitud"]["por_grupo"]["Metropolitana"] == mediana_real


def test_pipeline_columnas_identicas_entrenamiento_y_prueba_con_dos_observadores(df_pequeno_retc):
    """
    Verifica que las columnas de salida sean idénticas en entrenamiento y prueba (incluso cuando
    prueba no contiene todas las regiones de entrenamiento) y que dos observadores funcionen a la vez.
    """
    obs_bitacora = BitacoraObserver()
    obs_nulos = AuditoriaNulosObserver()

    pipe = (
        Pipeline([
            ImputadorPorGrupo(
                cols_numericas=["latitud", "longitud"],
                cols_categoricas=["id_lista_a", "id_ciiu4", "ciiu4", "id_ciiu6", "ciiu6", "rubro"],
            ),
            CodificadorCategorias(top_n_comunas=2),
            EscaladorRobusto(
                columnas=["cantidad_kg", "latitud", "longitud", "frecuencia_declaraciones_rut", "n_peligrosidades"],
                descartar_texto=True,
            ),
        ])
        .suscribir(obs_bitacora)
        .suscribir(obs_nulos)
    )

    df_train = df_pequeno_retc.iloc[:4].copy()
    df_test = df_pequeno_retc.iloc[4:].copy()

    out_train = pipe.ajustar_transformar(df_train)
    out_test = pipe.transformar(df_test)

    assert list(out_train.columns) == list(out_test.columns)
    assert int(out_train.isna().sum().sum()) == 0
    assert int(out_test.isna().sum().sum()) == 0
    assert len(obs_bitacora.registros) == 6  # 3 pasos en ajustar + 3 pasos en transformar
    assert len(obs_nulos.historial_nulos) == 6
    assert "Pipeline(" in repr(pipe)


def test_escalador_robusto_caso_borde_ric_cero(df_pequeno_retc):
    """Si una columna tiene RIC = 0, EscaladorRobusto usa denominador 1.0 y evita NaN/Inf."""
    esc = EscaladorRobusto(columnas=["n_peligrosidades"], descartar_texto=False)
    res = esc.ajustar_transformar(df_pequeno_retc)
    assert not res["n_peligrosidades_rob"].isna().any()
    assert not np.isinf(res["n_peligrosidades_rob"]).any()
