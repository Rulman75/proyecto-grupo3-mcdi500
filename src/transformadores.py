"""
Jerarquía de clases orientadas a objetos para el preprocesamiento reproducible (Fase 3 - MCDI500).
Incluye la clase base Transformador (Encapsulamiento y Contrato Plantilla), las clases derivadas
(Herencia y Polimorfismo) y las estrategias intercambiables de imputación (Patrón Strategy).
"""
import numpy as np
import pandas as pd
class Transformador:
 """
 Clase base abstracta que define el contrato común de todos los transformadores del pipeline.
 Aplica el método plantilla: centraliza la validación de entrada, el control de estado interno
 (_ajustado y _parametros) y la copia defensiva, delegando aprender() y aplicar() a las
subclases.
 """
 etiqueta_componente = "transformador_pipeline"
 def __init__(self, columnas: str | list[str]):
 if isinstance(columnas, str):
 self.columnas = [columnas]
 elif isinstance(columnas, list) and len(columnas) > 0:
 self.columnas = list(columnas)
 else:
 raise ValueError("El parámetro 'columnas' debe ser un nombre de columna o una lista no
vacía.")
 # Encapsulamiento: atributos internos protegidos con guion bajo
 self._parametros: dict = {}
 self._ajustado: bool = False
 @property
 def ajustado(self) -> bool:
 """Indica si el transformador ya aprendió sus parámetros desde los datos."""
 return self._ajustado
 @property
 def parametros(self) -> dict:
 """Devuelve una copia de solo lectura de los parámetros aprendidos."""
 return dict(self._parametros)
 @property
 def nombre(self) -> str:
 """Nombre identificador de la clase del transformador."""
 return self.__class__.__name__
 def _validar_columnas(self, df: pd.DataFrame) -> None:
 if not isinstance(df, pd.DataFrame):
 raise TypeError(f"{self.nombre} esperaba un pandas.DataFrame, recibió
{type(df).__name__}.")
 if df.empty:
 raise ValueError(f"{self.nombre} recibió un DataFrame vacío (0 filas).")
 faltantes = [c for c in self.columnas if c not in df.columns]
 if faltantes:
 raise KeyError(f"{self.nombre}: las siguientes columnas no existen en el DataFrame:
{faltantes}")
 def ajustar(self, df: pd.DataFrame) -> "Transformador":
 """Verifica las columnas, invoca aprender(df) y activa el estado _ajustado."""
 self._validar_columnas(df)
 self._parametros = self.aprender(df)
 self._ajustado = True
 return self
 def transformar(self, df: pd.DataFrame) -> pd.DataFrame:
 """Verifica que el objeto esté ajustado y aplica la transformación sobre una copia."""
 if not self._ajustado:
 raise RuntimeError(
 f"No se puede ejecutar transformar() en '{self.nombre}' antes de llamar a
ajustar()."
 )
 self._validar_columnas(df)
 return self.aplicar(df.copy())
 def ajustar_transformar(self, df: pd.DataFrame) -> pd.DataFrame:
 """Ajusta los parámetros con df y devuelve el DataFrame transformado."""
 return self.ajustar(df).transformar(df)
 def aprender(self, df: pd.DataFrame) -> dict:
 """Método gancho que cada clase hija debe sobrescribir para calcular sus parámetros."""
 raise NotImplementedError(f"La subclase '{self.nombre}' debe implementar el método
aprender(df).")
 def aplicar(self, df: pd.DataFrame) -> pd.DataFrame:
 """Método gancho que cada clase hija debe sobrescribir para transformar la copia del
DataFrame."""
 raise NotImplementedError(f"La subclase '{self.nombre}' debe implementar el método
aplicar(df).")
