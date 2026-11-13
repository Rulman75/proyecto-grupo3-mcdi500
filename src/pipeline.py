""" 
Módulo de composición del Pipeline polimórfico y registro automático de trazabilidad 
mediante el patrón de diseño Observer (Fase 3 - MCDI500). 
""" 
 
from pathlib import Path 
import time 
import pandas as pd 
from src.transformadores import Transformador 
 
 
class ObservadorPipeline: 
    """Interfaz base para los observadores que escuchan la ejecución del Pipeline (Patrón 
Observer).""" 
 
    def actualizar(self, evento: dict) -> None: 
        raise NotImplementedError 
 
 
class BitacoraObserver(ObservadorPipeline): 
    """ 
    Observador concreto que registra automáticamente cada etapa ejecutada por el Pipeline 
    y exporta la bitácora técnica actualizada en formato Markdown. 
    """ 
 
    def __init__(self, ruta_salida: str | Path | None = None): 
        self.ruta_salida = Path(ruta_salida) if ruta_salida else None 
        self.registros: list[dict] = [] 
 
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
            "Esta bitácora se genera automáticamente en cada ejecución del `Pipeline` mediante el 
patrón de diseño **Observer**.", 
            "", 
            "| Orden | Paso (`Transformador`) | Modo | Filas Entrada → Salida | Columnas Entrada → 
Salida | Nulos Entrada → Salida | Tiempo (s) | Resumen de Parámetros Aprendidos |", 
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
 
 
class Pipeline: 
    """ 
    Composición secuencial de objetos Transformador que comparten la interfaz común 
    ajustar(df) y transformar(df) (Polimorfismo), con soporte para notificadores (Patrón 
Observer). 
    """ 
 
    def __init__(self, pasos: list[Transformador]): 
        if not pasos or not all(isinstance(p, Transformador) for p in pasos): 
            raise TypeError("El Pipeline requiere una lista no vacía de objetos que hereden de 
Transformador.") 
        self._pasos: list[Transformador] = list(pasos) 
        self._ajustado: bool = False 
        self._observadores: list[ObservadorPipeline] = [] 
 
    @property 
    def pasos(self) -> list[Transformador]: 
        return list(self._pasos) 
 
    @property 
    def ajustado(self) -> bool: 
        return self._ajustado 
 
    def suscribir(self, observador: ObservadorPipeline) -> "Pipeline": 
        """Suscribe un observador para recibir notificaciones al finalizar cada paso.""" 
        self._observadores.append(observador) 
        return self 
 
    def _notificar(self, evento: dict) -> None: 
        for obs in self._observadores: 
            obs.actualizar(evento) 
 
    @staticmethod 
    def _resumir_parametros(paso: Transformador) -> str: 
        params = paso.parametros 
        if "numericas" in params and "categoricas" in params: 
            return f"{len(params['numericas'])} vars numéricas por región y 
{len(params['categoricas'])} categóricas por rubro" 
        if "top_comunas" in params: 
            return ( 
                f"Top-{len(params['top_comunas'])} comunas, {len(params['frec_rut'])} RUTs, " 
                f"{len(params['cats_region'])} regiones, {len(params['cats_estado'])} estados" 
            ) 
        return f"{len(params)} variables escaladas con mediana y RIC" 
 
    def ajustar(self, df: pd.DataFrame) -> "Pipeline": 
        """Recorre polimórficamente todos los pasos ajustando y propagando el DataFrame 
intermedio.""" 
        intermedio = df.copy() 
        for idx, paso in enumerate(self._pasos, start=1): 
            filas_in, cols_in = intermedio.shape 
            nulos_in = int(intermedio.isna().sum().sum()) 
            t0 = time.perf_counter() 
 
            # Polimorfismo: se invoca la misma interfaz sin consultar el tipo concreto de 'paso' 
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
            raise RuntimeError("No se puede ejecutar transformar() en el Pipeline antes de llamar 
a ajustar().") 
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
