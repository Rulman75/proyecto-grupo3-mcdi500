# Bitácora Técnica de Decisiones — Fase 2 (Grupo 3 MCDI500)

- **Dataset de entrada (inmutable):** `F1\data\raw\Base_Maestra_2023_2025.xlsx` (`118.280 filas × 21 columnas`)
- **Dataset de salida (procesado):** `F2\data\processed\base_maestra_2023_2025_clean.csv` (`118162 filas × 63 columnas`)

## Registro de Decisiones Técnicas
| Etapa | Problema detectado | Alternativas evaluadas | Decisión adoptada y justificación |
| :--- | :--- | :--- | :--- |
| 1. Deduplicación | 118 registros duplicados exactos en la base 2023–2025 | Conservar o eliminar duplicados exactos | Se eliminan con `drop_duplicates()`, quedando `118.162` declaraciones únicas. |
| 2. Homologación regional y de peligrosidad | `region` tenía 19 etiquetas para 16 regiones y `peligrosidad` 812 variantes (`##` vs `;` en 2025) | Codificar en crudo vs normalizar diccionarios y cadenas | Se homologan las 16 regiones de Chile y se reducen las 812 variantes de `peligrosidad` a 93 categorías canónicas ordenadas. |
| 3. Rescate geográfico 2024 | En 2024 las 39.518 coordenadas perdieron el punto decimal (ej. `-33447301481283`) | Descartar año 2024 vs rescatar punto decimal y filtrar rango de Chile | Se recupera la escala decimal validando `latitud` en `[-57, -17]` y `longitud` en `[-110, -65]`, rescatando más de 39.300 coordenadas. |
| 4. Manejo de nulos | Nulos en `id_lista_a` (4,03%), coordenadas (0,24%) y `cantidad_kg` (0,02%) | `dropna()` (pierde 5.037 filas = 4,26%), media global o mediana/moda por grupo | Se imputa con mediana por `region` (numéricas) y moda por `id_rubro` (categóricas) más banderas `_imputado`, evitando sesgar `cantidad_kg` (media 16.422 kg vs mediana 234 kg). |
| 5. Transformación por rol | Variables heterogéneas (nominales, ordinales, alta cardinalidad, fecha, texto) | Codificación única vs codificación específica por rol | Se crean binarias regulatorias (`es_gran_generador_bin >= 12.000 kg`), ordinal de estado físico, One-Hot, Top-10 comunas, frecuencia de RUT, armónicas de año y métricas de texto. |
| 6. Escalamiento | `cantidad_kg` tiene 16,19% de outliers ($1,5 \times \text{RIC}$) | `StandardScaler`, `MinMaxScaler`, `RobustScaler` | Se selecciona `RobustScaler` (centra mediana en 0,0 y RIC en 1,0 sin aplastar el 75% de los datos como `MinMaxScaler`). |