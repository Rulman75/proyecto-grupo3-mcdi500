# Registro Cronológico de Cambios y Trazabilidad de Mejoras (`CHANGELOG.md`)

Este documento consigna en orden cronológico las observaciones formativas recibidas en las Fases 1, 2 y 3, las acciones correctivas implementadas, su impacto técnico en modularidad, rendimiento y documentación, y los commits verificables en el historial de Git (`https://github.com/Rulman75/proyecto-grupo3-mcdi500`).

---

## [Fase 4 — Semana 3] — 2026-11-17 (Consolidación, Visualización y Comunicación de Resultados)

### Agregado
- **Módulo de comunicación e inversión de transformaciones (`src/comunicacion.py`):** Implementa `exportar_artefactos_f3`, `cargar_artefactos`, `leer_parametros`, `revertir_escalamiento` (`x = x_rob * ric + mediana`), `reconstruir_categorias` (desde columnas indicadoras One-Hot), `copia_interpretable`, `intervalo_wilson`, `tasa_por_grupo` y `guardar_figura` a `200 dpi`.
- **Cuaderno ejecutable de cierre (`F4/notebooks/F4_Visualizacion_Comunicacion.ipynb` y `F4/docs/F4_Visualizacion_Comunicacion.html`):** Construye la copia interpretable, verifica su fidelidad contra el archivo original con `np.allclose`, genera las figuras explicativas en `F4/figuras/` respondiendo cada objetivo específico bajo la secuencia narrativa *Contexto → Contraste → Resolución*, controla la variable de confusión sectorial (Minería vs. Otros rubros), ejemplifica el Factor de Mentira de Tufte y exporta `F4/docs/hallazgos_f4.csv` y `F4/docs/metadatos_f4.json`.
- **Pruebas unitarias de Fase 4 (`tests/test_comunicacion_f4.py`):** Amplía la suite automatizada de `pytest` a **18 pruebas unitarias** cubriendo la reversión del escalamiento robusto, la reconstrucción categórica, los límites `[0, 1]` del intervalo de Wilson y la captura de `FileNotFoundError`.

---

## [Fase 3 — Semana 2 (Cierre de Retroalimentación)] — 2026-11-16

### Cambiado
- **Clases base abstractas (`abc.ABC`), encapsulamiento con `deepcopy`, `__repr__` y 2.º observador (commit `4d4ae5a` / PR `#9` `f29dd75`):** Convierte `Transformador`, `EstrategiaImputacion` y `ObservadorPipeline` en clases abstractas con `@abstractmethod`, protege `parametros` con `deepcopy`, anonimiza los `6.777` RUT con hash `SHA-256` dentro de `_parametros` y suscribe un segundo observador (`AuditoriaNulosObserver`) junto a `BitacoraObserver` sin modificar `Pipeline`.
- **Equivalencia no circular contra versión funcional sin clases y tabla comparativa contra Sumativa 1 (commit `06332e7` / PR `#10` `98acbf7`):** Agrega `preprocesar_version_funcional(df_raw)` (100 % sin clases) y `comparar_con_entregable_sumativa1()`, actualiza `F2/docs/bitacora_f2.md` y elimina el puente `F2/src/` y el CSV duplicado en `F3`.
- **Suite de pruebas `pytest` en `tests/` y corrección de caso borde en `ImputadorPorGrupo` (commits `dcf408c`..`ab5bb6a` / PR `#11` `5c760de`):** Crea `tests/test_transformadores_pipeline.py` y `tests/test_recursividad_limpieza.py` con tablas pequeñas hechas a mano, corrige la generación uniforme de banderas `_imputado` entre entrenamiento y prueba, y agrega casos borde de recursividad (árbol vacío, 1 nivel y con nulos), complejidad esperada y declaración de hardware (`obtener_info_entorno`).
- **Limpieza de historial con `git filter-repo` y notebooks sin rutas absolutas (commits `1cf7435`, `2ffe268` / PRs `#12` `da2e455` y `#13` `5cdb7a4`):** Purga definitivamente `F1/data/raw/Base_Maestra_2023_2025.xlsx` de toda la historia de Git y reejecuta `F1`, `F2` y `F3` mostrando solo rutas relativas `./`.

---

## [Fase 3 — Semana 2 (Arquitectura Inicial)] — 2026-11-12 a 2026-11-13

### Agregado y Corregido (Observaciones Sumativa 1)
- **Saneamiento del repositorio y protección de datos personales (commit `4085869` / PR `#1` `0cd4dc8`):** Retira archivo Excel crudo con 398 RUT de personas naturales, configura `.gitignore` y `.mailmap` y depura `requirements.txt` de 168 paquetes del sistema a las librerías estrictas del proyecto.
- **Funciones puras sin estado y correcciones de Fase 2 (commit `888fa69` / PR `#2` `f98a293`):** Descarta las 21 declaraciones sin `cantidad_kg` (evitando imputar la variable objetivo), elimina la doble codificación de `estado_materia`, elimina `anio_sin`/`anio_cos` y largos de texto CIIU, e imputa `id_lista_a` por moda de `id_rubro`.
- **Jerarquía POO, patrones `Strategy` y `Observer`, benchmarks y recursividad CIIU (commits `d6d09fd`, `c0c20dd`, `ccfb91a` / PRs `#3` a `#8`):** Implementa `ImputadorPorGrupo`, `CodificadorCategorias`, `EscaladorRobusto`, `Pipeline`, mediciones con `timeit` (mínimo) y `tracemalloc` (aceleración de `15,7×` en normalización de glosas) y suma recursiva sobre la jerarquía CIIU de 3 niveles (`1.942.051.189,00 kg`).
