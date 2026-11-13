"""
Puente de compatibilidad de la Fase 2 hacia el paquete compartido 'src/' en la raíz del proyecto.
Evita la duplicación de código entre Fase 2 y Fase 3 manteniendo alta cohesión y bajo acoplamiento.
"""

from src.carga import COLUMNAS_ESPERADAS_RETC, cargar_datos_seguro, diagnosticar_variables
from src.limpieza import (
    MAPA_REGIONES_CHILE,
    agregar_atributos_deterministas,
    depurar_registros_base,
    estandarizar_regiones_y_peligrosidad,
    rescatar_coordenadas_chile,
)
