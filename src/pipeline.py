"""
Módulo de composición del Pipeline polimórfico y registro automático de trazabilidad
mediante el patrón de diseño Observer con soporte para múltiples observadores (Fase 3 - MCDI500).
"""

from abc import ABC, abstractmethod
from pathlib import Path
import time
import pandas as pd
from src.transformadores import Transformador


class ObservadorPipeline(ABC):
    """Interfaz abstracta para los observadores que escuchan la ejecución del Pipeline (Patrón Observer)."""

    @abstractmethod
    def actualizar(self, evento: dict) -> None:
        """Recibe el diccionario de evento emitido tras cada paso del Pipeline."""


class BitacoraObserver(ObservadorPipeline):
    """
    Observador concreto 1: Registra automáticamente cada etapa ejecutada por el Pipeline
    y exporta la bitácora técnica actualizada en formato Markdown.
    """

    def __init__(self, ruta_salida: str | Path | None = None):
        self.ruta_salida = Path(ruta_salida) if ruta_salida else None
        self.registros: list[dict] = []

    def __repr__(self) -> str:
        ruta_str = self.ruta_salida.as_posix() if self.ruta_salida else None
        return f"BitacoraObserver(ruta_salida={ruta_str!r}, eventos_registrados={len(self.registros)})"

    def reiniciar(self) -> None:
        self.registros.clear()

    def actualizar(self, evento: dict) -> None:
        self.registros.append(evento)
        if self.ruta_salida is not None and evento.get("modo") == "ajustar":
            self.exportar_markdown(self.ruta_salida)

    def obtener_tabla(self) -> pd.DataFrame:
        return pd.DataFrame(self.registros)

    def exportar_markdown(self, ruta: str | Path) -> Path:
        ruta_dest = Path(ruta)
        ruta_dest.parent.mkdir(parents=True, exist_ok=True)
        lineas = [
            "# Bitácora Técnica Automática (Generada por `BitacoraObserver` — Fase 3)",
            "",
            "Esta bitácora se genera automáticamente en cada ejecución del `Pipeline` mediante el patrón de diseño **Observer**.",
            "",
            "| Orden | Paso (`Transformador`) | Modo | Filas Entrada → Salida | Columnas Entrada → Salida | Nulos Entrada → Salida | Tiempo (s) | Resumen de Parámetros Aprendidos |",
            "| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :--- |",
        ]
        for reg in self.registros:
            lineas.append(
                f"| {reg['orden']} | `{reg['paso']}` | `{reg['modo']}` | "
                f"{reg['filas_in']} → {reg['filas_out']} | "
                f"{reg['cols_in']} → {reg['cols_out']} | "
                f"{reg['nulos_in']} → {reg['nulos_out']} | "
                f"{reg['tiempo_s']:.4f} s | {reg['resumen_parametros']} |"
            )
        ruta_dest.write_text("\n".join(lineas) + "\n", encoding="utf-8")
        return ruta_dest


class AuditoriaNulosObserver(ObservadorPipeline):
    """
    Observador concreto 2: Puede suscribirse al mismo Pipeline sin modificar su código
    para contabilizar exclusivamente los valores faltantes resueltos por etapa y verificar
    que el conjunto de salida quede con cero nulos.
    """

    def __init__(self):
        self.historial_nulos: list[dict] = []

    def __repr__(self) -> str:
        return f"AuditoriaNulosObserver(etapas_auditadas={len(self.historial_nulos)})"

    def reiniciar(self) -> None:
        self.historial_nulos.clear()

    def actualizar(self, evento: dict) -> None:
        nulos_in = int(evento["nulos_in"])
        nulos_out = int(evento["nulos_out"])
        self.historial_nulos.append({
            "orden": evento["orden"],
            "paso": evento["paso"],
            "modo": evento["modo"],
            "nulos_entrada": nulos_in,
            "nulos_salida": nulos_out,
            "nulos_resueltos": nulos_in - nulos_out,
            "sin_nulos_pendientes": bool(nulos_out == 0),
        })

    def obtener_reporte(self) -> pd.DataFrame:
        return pd.DataFrame(self.historial_nulos)


class Pipeline:
    """
    Composición secuencial de objetos Transformador que comparten la interfaz común
    ajustar(df) y transformar(df) (Polimorfismo), con soporte para múltiples observadores (Patrón Observer).
    """

    def __init__(self, pasos: list[Transformador]):
        if not pasos or not all(isinstance(p, Transformador) for p in pasos):
            raise TypeError("El Pipeline requiere una lista no vacía de objetos que hereden de Transformador.")
        self._pasos: list[Transformador] = list(pasos)
        self._ajustado: bool = False
        self._observadores: list[ObservadorPipeline] = []

    def __repr__(self) -> str:
        nombres_pasos = [p.nombre for p in self._pasos]
        return (
            f"Pipeline(pasos={nombres_pasos}, ajustado={self._ajustado}, "
            f"n_observadores={len(self._observadores)})"
        )

    @property
    def pasos(self) -> list[Transformador]:
        return list(self._pasos)

    @property
    def ajustado(self) -> bool:
        return self._ajustado

    def suscribir(self, observador: ObservadorPipeline) -> "Pipeline":
        """Suscribe un observador para recibir notificaciones al finalizar cada paso."""
        if not isinstance(observador, ObservadorPipeline):
            raise TypeError("El observador debe heredar de ObservadorPipeline.")
        self._observadores.append(observador)
        return self

    def _notificar(self, evento: dict) -> None:
        for obs in self._observadores:
            obs.actualizar(evento)

    @staticmethod
    def _resumir_parametros(paso: Transformador) -> str:
        params = paso.parametros
        if "numericas" in params and "categoricas" in params:
            return f"{len(params['numericas'])} vars numéricas por región y {len(params['categoricas'])} categóricas por rubro"
        if "top_comunas" in params:
            n_ruts = params.get("n_ruts_unicos", len(params.get("frec_rut_anon", {})))
            return (
                f"Top-{len(params['top_comunas'])} comunas, {n_ruts} RUTs (anonimizados), "
                f"{len(params['cats_region'])} regiones, {len(params['cats_estado'])} estados"
            )
        return f"{len(params)} variables escaladas con mediana y RIC"

    def ajustar(self, df: pd.DataFrame) -> "Pipeline":
        """Recorre polimórficamente todos los pasos ajustando y propagando el DataFrame intermedio."""
        intermedio = df.copy()
        for idx, paso in enumerate(self._pasos, start=1):
            filas_in, cols_in = intermedio.shape
            nulos_in = int(intermedio.isna().sum().sum())
            t0 = time.perf_counter()

            # Polimorfismo: se invoca la misma interfaz común sin preguntar el tipo concreto de 'paso'
            intermedio = paso.ajustar(intermedio).transformar(intermedio)

            duracion = time.perf_counter() - t0
            self._notificar({
                "orden": idx,
                "paso": paso.nombre,
                "modo": "ajustar",
                "filas_in": filas_in,
                "filas_out": intermedio.shape[0],
                "cols_in": cols_in,
                "cols_out": intermedio.shape[1],
                "nulos_in": nulos_in,
                "nulos_out": int(intermedio.isna().sum().sum()),
                "tiempo_s": round(duracion, 4),
                "resumen_parametros": self._resumir_parametros(paso),
            })

        self._ajustado = True
        return self

    def transformar(self, df: pd.DataFrame) -> pd.DataFrame:
        """Aplica la secuencia de pasos ya ajustados sobre un nuevo conjunto de datos."""
        if not self._ajustado:
            raise RuntimeError("No se puede ejecutar transformar() en el Pipeline antes de llamar a ajustar().")
        resultado = df.copy()
        for idx, paso in enumerate(self._pasos, start=1):
            filas_in, cols_in = resultado.shape
            nulos_in = int(resultado.isna().sum().sum())
            t0 = time.perf_counter()

            resultado = paso.transformar(resultado)

            duracion = time.perf_counter() - t0
            self._notificar({
                "orden": idx,
                "paso": paso.nombre,
                "modo": "transformar",
                "filas_in": filas_in,
                "filas_out": resultado.shape[0],
                "cols_in": cols_in,
                "cols_out": resultado.shape[1],
                "nulos_in": nulos_in,
                "nulos_out": int(resultado.isna().sum().sum()),
                "tiempo_s": round(duracion, 4),
                "resumen_parametros": self._resumir_parametros(paso),
            })
        return resultado

    def ajustar_transformar(self, df: pd.DataFrame) -> pd.DataFrame:
        """Ajusta todos los pasos con df y devuelve el DataFrame final transformado."""
        intermedio = df.copy()
        for idx, paso in enumerate(self._pasos, start=1):
            filas_in, cols_in = intermedio.shape
            nulos_in = int(intermedio.isna().sum().sum())
            t0 = time.perf_counter()

            intermedio = paso.ajustar(intermedio).transformar(intermedio)

            duracion = time.perf_counter() - t0
            self._notificar({
                "orden": idx,
                "paso": paso.nombre,
                "modo": "ajustar",
                "filas_in": filas_in,
                "filas_out": intermedio.shape[0],
                "cols_in": cols_in,
                "cols_out": intermedio.shape[1],
                "nulos_in": nulos_in,
                "nulos_out": int(intermedio.isna().sum().sum()),
                "tiempo_s": round(duracion, 4),
                "resumen_parametros": self._resumir_parametros(paso),
            })
        self._ajustado = True
        return intermedio
