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
    (_ajustado y _parametros) y la copia defensiva, delegando aprender() y aplicar() a las subclases.
    """

    etiqueta_componente = "transformador_pipeline"

    def __init__(self, columnas: str | list[str]):
        if isinstance(columnas, str):
            self.columnas = [columnas]
        elif isinstance(columnas, list) and len(columnas) > 0:
            self.columnas = list(columnas)
        else:
            raise ValueError("El parámetro 'columnas' debe ser un nombre de columna o una lista no vacía.")

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
            raise TypeError(f"{self.nombre} esperaba un pandas.DataFrame, recibió {type(df).__name__}.")
        if df.empty:
            raise ValueError(f"{self.nombre} recibió un DataFrame vacío (0 filas).")
        faltantes = [c for c in self.columnas if c not in df.columns]
        if faltantes:
            raise KeyError(f"{self.nombre}: las siguientes columnas no existen en el DataFrame: {faltantes}")

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
                f"No se puede ejecutar transformar() en '{self.nombre}' antes de llamar a ajustar()."
            )
        self._validar_columnas(df)
        return self.aplicar(df.copy())

    def ajustar_transformar(self, df: pd.DataFrame) -> pd.DataFrame:
        """Ajusta los parámetros con df y devuelve el DataFrame transformado."""
        return self.ajustar(df).transformar(df)

    def aprender(self, df: pd.DataFrame) -> dict:
        """Método gancho que cada clase hija debe sobrescribir para calcular sus parámetros."""
        raise NotImplementedError(f"La subclase '{self.nombre}' debe implementar el método aprender(df).")

    def aplicar(self, df: pd.DataFrame) -> pd.DataFrame:
        """Método gancho que cada clase hija debe sobrescribir para transformar la copia del DataFrame."""
        raise NotImplementedError(f"La subclase '{self.nombre}' debe implementar el método aplicar(df).")



# =====================================================================
# PATRÓN STRATEGY: Estrategias intercambiables para imputación numérica
# =====================================================================

class EstrategiaImputacion:
    """Contrato común para las estrategias de manejo de valores faltantes (Patrón Strategy)."""
    nombre = "estrategia_base"

    def aprender_parametros(self, df: pd.DataFrame, columna: str) -> dict:
        raise NotImplementedError

    def aplicar_estrategia(self, df: pd.DataFrame, columna: str, params: dict) -> pd.DataFrame:
        raise NotImplementedError


class EstrategiaEliminarFilas(EstrategiaImputacion):
    """Estrategia 1: Eliminación por lista (dropna) sobre el DataFrame."""
    nombre = "1. Eliminación por lista (dropna)"

    def aprender_parametros(self, df: pd.DataFrame, columna: str) -> dict:
        return {"metodo": "dropna"}

    def aplicar_estrategia(self, df: pd.DataFrame, columna: str, params: dict) -> pd.DataFrame:
        return df.dropna().copy()


class EstrategiaMediaGlobal(EstrategiaImputacion):
    """Estrategia 2: Imputación por media aritmética global."""
    nombre = "2. Media global"

    def aprender_parametros(self, df: pd.DataFrame, columna: str) -> dict:
        return {"valor": float(df[columna].mean())}

    def aplicar_estrategia(self, df: pd.DataFrame, columna: str, params: dict) -> pd.DataFrame:
        df[columna] = df[columna].fillna(params["valor"])
        return df


class EstrategiaMedianaGlobal(EstrategiaImputacion):
    """Estrategia 3: Imputación por mediana global."""
    nombre = "3. Mediana global"

    def aprender_parametros(self, df: pd.DataFrame, columna: str) -> dict:
        return {"valor": float(df[columna].median())}

    def aplicar_estrategia(self, df: pd.DataFrame, columna: str, params: dict) -> pd.DataFrame:
        df[columna] = df[columna].fillna(params["valor"])
        return df


class EstrategiaMedianaPorGrupo(EstrategiaImputacion):
    """Estrategia 4: Imputación por mediana condicionada al grupo (ej. región)."""

    def __init__(self, col_grupo: str = "region"):
        self.col_grupo = col_grupo
        self.nombre = f"4. Mediana agrupada por '{col_grupo}' (Elegida)"

    def aprender_parametros(self, df: pd.DataFrame, columna: str) -> dict:
        medianas_grp = df.groupby(self.col_grupo)[columna].median().to_dict()
        mediana_global = float(df[columna].median())
        return {"por_grupo": medianas_grp, "respaldo_global": mediana_global}

    def aplicar_estrategia(self, df: pd.DataFrame, columna: str, params: dict) -> pd.DataFrame:
        valores_grupo = df[self.col_grupo].map(params["por_grupo"])
        df[columna] = df[columna].fillna(valores_grupo).fillna(params["respaldo_global"])
        return df


class ImputadorFlexible(Transformador):
    """
    Transformador que delega el cálculo y relleno de nulos a un objeto EstrategiaImputacion.
    Materializa el patrón de diseño Strategy: permite cambiar el algoritmo sin modificar la clase.
    """

    def __init__(self, columna: str, estrategia: EstrategiaImputacion):
        super().__init__(columna)
        self.columna = columna
        self.estrategia = estrategia

    def aprender(self, df: pd.DataFrame) -> dict:
        return self.estrategia.aprender_parametros(df, self.columna)

    def aplicar(self, df: pd.DataFrame) -> pd.DataFrame:
        return self.estrategia.aplicar_estrategia(df, self.columna, self._parametros)


# =====================================================================
# CLASES HIJAS DEL PIPELINE DEFINITIVO (HERENCIA Y POLIMORFISMO)
# =====================================================================

class ImputadorPorGrupo(Transformador):
    """
    Clase Hija 1: Aprende las medianas por región para variables numéricas con nulos ('latitud', 'longitud')
    y las modas por rubro ('id_rubro') para variables categóricas con nulos ('id_lista_a', 'id_ciiu4', etc.),
    creando banderas binarias '<col>_imputado' (0/1) para preservar la trazabilidad.
    """

    def __init__(
        self,
        cols_numericas: list[str],
        cols_categoricas: list[str],
        col_grupo_num: str = "region",
        col_grupo_cat: str = "id_rubro",
    ):
        todas = list(cols_numericas) + list(cols_categoricas) + [col_grupo_num, col_grupo_cat]
        super().__init__( list(dict.fromkeys(todas)) )
        self.cols_numericas = list(cols_numericas)
        self.cols_categoricas = list(cols_categoricas)
        self.col_grupo_num = col_grupo_num
        self.col_grupo_cat = col_grupo_cat

    def aprender(self, df: pd.DataFrame) -> dict:
        params_num = {}
        for col in self.cols_numericas:
            por_grupo = df.groupby(self.col_grupo_num)[col].median().to_dict()
            respaldo = float(df[col].median()) if pd.notna(df[col].median()) else 0.0
            params_num[col] = {
                "por_grupo": por_grupo,
                "respaldo": respaldo,
                "tenia_nulos": bool(df[col].isna().sum() > 0),
            }

        params_cat = {}
        for col in self.cols_categoricas:
            modas_grp = (
                df.groupby(self.col_grupo_cat)[col]
                .apply(lambda s: s.mode().iloc[0] if not s.mode().empty else np.nan)
                .to_dict()
            )
            moda_gl = df[col].mode().iloc[0] if not df[col].mode().empty else "SIN_DATO"
            params_cat[col] = {
                "por_grupo": modas_grp,
                "respaldo": moda_gl,
                "tenia_nulos": bool(df[col].isna().sum() > 0),
            }

        return {"numericas": params_num, "categoricas": params_cat}

    def aplicar(self, df: pd.DataFrame) -> pd.DataFrame:
        for col, info in self._parametros["numericas"].items():
            if info["tenia_nulos"] or df[col].isna().sum() > 0:
                df[f"{col}_imputado"] = df[col].isna().astype(int)
                relleno_grp = df[self.col_grupo_num].map(info["por_grupo"])
                df[col] = df[col].fillna(relleno_grp).fillna(info["respaldo"])

        for col, info in self._parametros["categoricas"].items():
            if info["tenia_nulos"] or df[col].isna().sum() > 0:
                df[f"{col}_imputado"] = df[col].isna().astype(int)
                relleno_grp = df[self.col_grupo_cat].map(info["por_grupo"])
                df[col] = df[col].fillna(relleno_grp).fillna(info["respaldo"])

        return df


class CodificadorCategorias(Transformador):
    """
    Clase Hija 2: Aprende el ranking de las Top-10 comunas, los mapas de frecuencia de alta
    cardinalidad ('rut_razon_social', 'id_ciiu4', 'id_lista_a') y los vocabularios canónicos
    para la codificación One-Hot de 'region', 'estado_materia' y 'comuna_agrupada'.
    """

    def __init__(self, top_n_comunas: int = 10):
        columnas_req = ["comuna", "rut_razon_social", "id_ciiu4", "id_lista_a", "region", "estado_materia"]
        super().__init__(columnas_req)
        self.top_n_comunas = top_n_comunas

    def aprender(self, df: pd.DataFrame) -> dict:
        top_comunas = df["comuna"].value_counts().nlargest(self.top_n_comunas).index.tolist()
        comuna_agrupada = df["comuna"].where(df["comuna"].isin(top_comunas), "OTROS")

        return {
            "top_comunas": top_comunas,
            "frec_rut": df["rut_razon_social"].value_counts().to_dict(),
            "frec_ciiu4": df["id_ciiu4"].value_counts().to_dict(),
            "frec_lista_a": df["id_lista_a"].value_counts().to_dict(),
            "cats_region": sorted(df["region"].dropna().unique().tolist()),
            "cats_estado": sorted(df["estado_materia"].dropna().unique().tolist()),
            "cats_comuna_top": sorted(comuna_agrupada.dropna().unique().tolist()),
        }

    def aplicar(self, df: pd.DataFrame) -> pd.DataFrame:
        p = self._parametros
        df["comuna_agrupada"] = df["comuna"].where(df["comuna"].isin(p["top_comunas"]), "OTROS")

        # Codificación por frecuencia (anonimiza rut_razon_social reemplazándolo por su frecuencia)
        df["frecuencia_declaraciones_rut"] = df["rut_razon_social"].map(p["frec_rut"]).fillna(0).astype(int)
        df["frecuencia_ciiu4"] = df["id_ciiu4"].map(p["frec_ciiu4"]).fillna(0).astype(int)
        df["frecuencia_lista_a"] = df["id_lista_a"].map(p["frec_lista_a"]).fillna(0).astype(int)

        # Codificación One-Hot garantizando exactamente las columnas aprendidas en entrenamiento
        for cat in p["cats_region"]:
            df[f"reg_{cat}"] = (df["region"] == cat).astype(int)
        for cat in p["cats_estado"]:
            df[f"estado_{cat}"] = (df["estado_materia"] == cat).astype(int)
        for cat in p["cats_comuna_top"]:
            df[f"comuna_top_{cat}"] = (df["comuna_agrupada"] == cat).astype(int)

        return df


class EscaladorRobusto(Transformador):
    """
    Clase Hija 3: Aprende la mediana (Q2) y el rango intercuartílico (RIC = Q3 - Q1) de cada
    variable numérica seleccionada y genera las columnas escaladas con sufijo '_rob'.
    Finalmente descarta las columnas de texto ya codificadas para entregar una matriz 100% numérica.
    """

    def __init__(self, columnas: list[str], descartar_texto: bool = True):
        super().__init__(columnas)
        self.descartar_texto = descartar_texto

    def aprender(self, df: pd.DataFrame) -> dict:
        estadisticos = {}
        for col in self.columnas:
            serie = df[col].dropna()
            mediana = float(serie.median())
            q1 = float(serie.quantile(0.25))
            q3 = float(serie.quantile(0.75))
            ric = q3 - q1
            estadisticos[col] = {
                "mediana": mediana,
                "ric": ric if ric != 0.0 else 1.0,
            }
        return estadisticos

    def aplicar(self, df: pd.DataFrame) -> pd.DataFrame:
        for col, stats in self._parametros.items():
            df[f"{col}_rob"] = (df[col] - stats["mediana"]) / stats["ric"]

        if self.descartar_texto:
            cols_texto = df.select_dtypes(exclude=["number"]).columns.tolist()
            df = df.drop(columns=cols_texto)

        return df
