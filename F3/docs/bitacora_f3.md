# Bitácora Técnica Automática (Generada por `BitacoraObserver` — Fase 3)

Esta bitácora se genera automáticamente en cada ejecución del `Pipeline` mediante el patrón de diseño **Observer**.

| Orden | Paso (`Transformador`) | Modo | Filas Entrada → Salida | Columnas Entrada → Salida | Nulos Entrada → Salida | Tiempo (s) | Resumen de Parámetros Aprendidos |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| 1 | `ImputadorPorGrupo` | `ajustar` | 118141 → 118141 | 27 → 35 | 5270 → 0 | 0.3545 s | 2 vars numéricas por región y 6 categóricas por rubro |
| 2 | `CodificadorCategorias` | `ajustar` | 118141 → 118141 | 35 → 70 | 0 → 0 | 0.4776 s | Top-10 comunas, 6777 RUTs, 16 regiones, 4 estados |
| 3 | `EscaladorRobusto` | `ajustar` | 118141 → 118141 | 70 → 61 | 0 → 0 | 0.0832 s | 5 variables escaladas con mediana y RIC |
