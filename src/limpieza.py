"""
Módulo de funciones de limpieza interanual, rescate geográfico vectorizado y cálculo longitudinal
de persistencia para la Base Maestra RETC 2023-2025 (Funciones sin estado - Fase 2 y Fase 3).
"""
import re
import unicodedata
import numpy as np
import pandas as pd
MAPA_REGIONES_CHILE = {
 "Libertador Gral. Bernardo O'Higgins": "Libertador General Bernardo O'Higgins",
 "Araucanía": "La Araucanía",
 "Aysén del Gral. Carlos Ibañez del Campo": "Aysén del General Carlos Ibáñez del Campo",
}
def depurar_registros_base(df: pd.DataFrame) -> pd.DataFrame:
 """
 Elimina filas duplicadas exactas (118 registros) y descarta explícitamente las declaraciones
 sin masa declarada ('cantidad_kg' nulo: 21 registros), ya que la masa declarada es la variable
 analítica central y no debe inventarse mediante imputación.
 """
 if "cantidad_kg" not in df.columns:
 raise KeyError("La columna 'cantidad_kg' es obligatoria para depurar registros base.")
 df_sin_dup = df.drop_duplicates().copy()
 df_valido = df_sin_dup.dropna(subset=["cantidad_kg"]).copy().reset_index(drop=True)
 return df_valido
def normalizar_glosa_individual(valor: str) -> str:
 """Quita tildes, pasa a mayúsculas, unifica separadores ('##' y ';') y ordena componentes."""
 if pd.isna(valor):
 return "SIN CLASIFICAR"
 nfkd = unicodedata.normalize("NFKD", str(valor))
 sin_tildes = "".join(c for c in nfkd if not unicodedata.combining(c)).upper().strip()
 partes = [p.strip() for p in re.split(r"##|;", sin_tildes) if p.strip()]
 return " + ".join(sorted(set(partes))) if partes else "SIN CLASIFICAR"
def normalizar_peligrosidad_fila_a_fila(serie: pd.Series) -> pd.Series:
 """Versión base (Fase 2): aplica la normalización fila por fila sobre toda la serie."""
 return serie.apply(normalizar_glosa_individual)
def normalizar_peligrosidad_por_unicos(serie: pd.Series) -> pd.Series:
 """
 Versión optimizada (Fase 3): normaliza únicamente los valores únicos (812 glosas distintas)
 en un diccionario en memoria y los proyecta sobre las 118.141 filas mediante .map().
 """
 valores_unicos = serie.dropna().unique()
 mapa_canonico = {val: normalizar_glosa_individual(val) for val in valores_unicos}
 return serie.map(mapa_canonico).fillna("SIN CLASIFICAR")
def estandarizar_regiones_y_peligrosidad(df: pd.DataFrame, usar_optimizado: bool = True) ->
pd.DataFrame:
 """
 Homologa las etiquetas de 'region' (de 19 variantes a las 16 regiones oficiales de Chile),
 corrige el dígito extra de 'id_ciiu4' en 2024 (truncando a 5 caracteres alfanuméricos),
 limpia 'id_peligrosidad', estandariza 'peligrosidad' (de 812 a 93 categorías canónicas)
 y normaliza 'estado_materia'.
 """
 df_out = df.copy()
 if "region" in df_out.columns:
 df_out["region"] = df_out["region"].astype(str).str.strip().replace(MAPA_REGIONES_CHILE)
 if "id_ciiu4" in df_out.columns:
 mask_ciiu = df_out["id_ciiu4"].notna()
 df_out.loc[mask_ciiu, "id_ciiu4"] = (
 df_out.loc[mask_ciiu, "id_ciiu4"].astype(str).str.strip().str[:5]
 )
 if "id_peligrosidad" in df_out.columns:
 df_out["id_peligrosidad"] =
df_out["id_peligrosidad"].astype(str).str.strip().str.rstrip(",")
 if "peligrosidad" in df_out.columns:
 if usar_optimizado:
 df_out["peligrosidad"] = normalizar_peligrosidad_por_unicos(df_out["peligrosidad"])
 else:
 df_out["peligrosidad"] = normalizar_peligrosidad_fila_a_fila(df_out["peligrosidad"])
 if "estado_materia" in df_out.columns:
 df_out["estado_materia"] = df_out["estado_materia"].astype(str).str.strip().str.lower()
 return df_out
def _rescatar_valor_coordenada(val, min_val: float, max_val: float) -> float:
 """Versión escalar (Fase 2): recupera el punto decimal valor por valor con bucle while."""
 if pd.isna(val):
 return np.nan
 v = float(val)
 if min_val <= v <= max_val:
 return round(v, 6)
 if v < 0:
 while v < min_val and abs(v) > 100.0:
 v /= 10.0
 if min_val <= v <= max_val:
 return round(v, 6)
 return np.nan
def rescatar_serie_coordenada_bucle(serie: pd.Series, min_val: float, max_val: float) ->
pd.Series:
 """Aplica el rescate de coordenadas valor por valor mediante .apply()."""
 return serie.apply(lambda x: _rescatar_valor_coordenada(x, min_val, max_val))
def rescatar_serie_coordenada_vectorizada(serie: pd.Series, min_val: float, max_val: float) ->
pd.Series:
 """
 Versión vectorizada (Fase 3): divide en bloque todas las coordenadas fuera de escala
 operando sobre arreglos de punto flotante de pandas/NumPy y filtra el rango de Chile.
 """
 s = serie.astype(float).copy()
 mask_escala = (s < min_val) & (s.abs() > 100.0)
 while mask_escala.any():
 s.loc[mask_escala] = s.loc[mask_escala] / 10.0
 mask_escala = (s < min_val) & (s.abs() > 100.0)
 s = s.where((s >= min_val) & (s <= max_val), np.nan)
 return s.round(6)
def rescatar_coordenadas_chile(df: pd.DataFrame, usar_vectorizado: bool = True) -> pd.DataFrame:
 """
 Corrige la pérdida del punto decimal en latitud/longitud del año 2024 y convierte en NaN
 cualquier coordenada fuera de Chile Continental e Insular:
 latitud en [-57.0, -17.0] y longitud en [-110.0, -65.0].
 """
 df_out = df.copy()
 if "latitud" in df_out.columns:
 if usar_vectorizado:
 df_out["latitud"] = rescatar_serie_coordenada_vectorizada(df_out["latitud"], -57.0, -
17.0)
 else:
 df_out["latitud"] = rescatar_serie_coordenada_bucle(df_out["latitud"], -57.0, -17.0)
 if "longitud" in df_out.columns:
 if usar_vectorizado:
 df_out["longitud"] = rescatar_serie_coordenada_vectorizada(df_out["longitud"], -110.0,
-65.0)
 else:
 df_out["longitud"] = rescatar_serie_coordenada_bucle(df_out["longitud"], -110.0, -
65.0)
 return df_out
def agregar_atributos_deterministas(df: pd.DataFrame) -> pd.DataFrame:
 """
 Agrega las variables derivadas que no dependen de parámetros estadísticos aprendidos:
 - Persistencia longitudinal del establecimiento ('n_anios_declarados_vu' y
'es_generador_persistente_bin').
 - Complejidad de peligrosidad ('n_peligrosidades' y 'multi_peligrosidad_bin').
 - Umbral regulatorio D.S. 148 Art. 25 ('es_gran_generador_bin' >= 12.000 kg/año).
 - Índice temporal trianual ('anio_indice' = año - 2023).
 """
 df_out = df.copy()
 df_out["n_anios_declarados_vu"] =
df_out.groupby("id_vu")["año"].transform("nunique").astype(int)
 df_out["es_generador_persistente_bin"] = (df_out["n_anios_declarados_vu"] == 3).astype(int)
 df_out["n_peligrosidades"] = df_out["peligrosidad"].astype(str).str.count(r" \+ ") + 1
 df_out["multi_peligrosidad_bin"] = (df_out["n_peligrosidades"] > 1).astype(int)
 df_out["es_gran_generador_bin"] = (df_out["cantidad_kg"] >= 12000.0).astype(int)
 df_out["anio_indice"] = (df_out["año"] - 2023).astype(int)
 return df_out
