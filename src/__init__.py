"""Paquete compartido src del Proyecto Grupo 3 (MCDI500 - Fases 1 a 4)."""

from src.carga import COLUMNAS_ESPERADAS_RETC, cargar_datos_seguro, diagnosticar_variables
from src.limpieza import (
    MAPA_REGIONES_CHILE,
    agregar_atributos_deterministas,
    comparar_con_entregable_sumativa1,
    depurar_registros_base,
    estandarizar_regiones_y_peligrosidad,
    normalizar_peligrosidad_fila_a_fila,
    normalizar_peligrosidad_por_unicos,
    preprocesar_version_funcional,
    rescatar_coordenadas_chile,
    rescatar_serie_coordenada_bucle,
    rescatar_serie_coordenada_vectorizada,
)
from src.transformadores import (
    CodificadorCategorias,
    EscaladorRobusto,
    EstrategiaEliminarFilas,
    EstrategiaImputacion,
    EstrategiaMediaGlobal,
    EstrategiaMedianaGlobal,
    EstrategiaMedianaPorGrupo,
    ImputadorFlexible,
    ImputadorPorGrupo,
    Transformador,
)
from src.pipeline import (
    AuditoriaNulosObserver,
    BitacoraObserver,
    ObservadorPipeline,
    Pipeline,
)
from src.medicion import (
    aplanar_estructura_recursiva,
    comparar_implementaciones,
    construir_arbol_ciiu,
    medir_curva_crecimiento,
    medir_tiempo_y_memoria,
    obtener_info_entorno,
    persistencia_con_bucle,
    persistencia_vectorizada,
    sumar_volumen_recursivo,
)
from src.comunicacion import (
    ARTEFACTOS_F3,
    REGIONES_MACROZONA_NORTE,
    SHA256_BASE_MAESTRA_OFICIAL,
    auditar_rotacion_administrativa,
    calcular_concentracion_y_lorenz,
    cargar_artefactos,
    copia_interpretable,
    descomponer_cambio_interanual,
    exportar_artefactos_f3,
    fmt_dec,
    fmt_miles,
    fmt_pct,
    guardar_figura,
    intervalo_wilson,
    leer_parametros,
    reconstruir_categorias,
    resumir_por_establecimiento,
    revertir_escalamiento,
    tasa_por_grupo,
    verificar_sha256_origen,
)