"""Paquete compartido src del Proyecto Grupo 3 (MCDI500 - Fases 2 y 3)."""
from src.carga import COLUMNAS_ESPERADAS_RETC, cargar_datos_seguro, diagnosticar_variables
from src.limpieza import (
 MAPA_REGIONES_CHILE,
 agregar_atributos_deterministas,
 depurar_registros_base,
 estandarizar_regiones_y_peligrosidad,
 normalizar_peligrosidad_fila_a_fila,
 normalizar_peligrosidad_por_unicos,
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
from src.pipeline import BitacoraObserver, ObservadorPipeline, Pipeline
from src.medicion import (
 aplanar_estructura_recursiva,
 comparar_implementaciones,
 construir_arbol_ciiu,
 medir_curva_crecimiento,
 medir_tiempo_y_memoria,
 persistencia_con_bucle,
 persistencia_vectorizada,
 sumar_volumen_recursivo,
)
