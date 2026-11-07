# Informe de Validación del Dataset (Fase 1) — Grupo 3 MCDI500
- **Archivo evaluado:** `F1\data\raw\clima_estaciones_chile_raw.csv`
- **Dimensiones:** 4500 filas × 16 columnas
- **Filas duplicadas exactas:** 0
- **Rango de valores faltantes en columnas con nulos:** 4,5% a 14.2%

## Diccionario y Perfil de Variables
| variable | dtype_pandas | rol_analitico | valores_unicos | nulos_n | nulos_pct | descripcion |
| --- | --- | --- | --- | --- | --- | --- |
| id_registro | str | identificador | 4500 | 0 | 0.0 | Código único de estación y fecha (DMC-XXXXXX-YYYYMMDD) |
| fecha_observacion | str | fecha | 1628 | 0 | 0.0 | Fecha diaria de medición (YYYY-MM-DD, período 2021-2025) |
| codigo_estacion_comuna | str | alta cardinalidad | 30 | 0 | 0.0 | Código DMC y nombre de la estación/comuna (30 estaciones) |
| macrozona | str | nominal | 12 | 0 | 0.0 | Macrozona climática de Chile (Norte, Centro, Sur, Austral) |
| temp_max_c | float64 | continua | 344 | 234 | 5.2 | Temperatura máxima diaria del aire (°C) |
| temp_min_c | float64 | continua | 265 | 216 | 4.8 | Temperatura mínima diaria del aire (°C) |
| humedad_relativa_pct | float64 | continua | 731 | 378 | 8.4 | Humedad relativa media diaria (%) |
| presion_hpa | float64 | continua | 947 | 522 | 11.6 | Presión atmosférica media a nivel de estación (hPa) |
| velocidad_viento_kmh | float64 | continua | 636 | 638 | 14.2 | Velocidad máxima diaria del viento (km/h) |
| precipitacion_mm | float64 | continua | 414 | 288 | 6.4 | Precipitación acumulada en 24 horas (mm) |
| nubosidad_octas | int64 | discreta | 9 | 0 | 0.0 | Cobertura nubosa diaria medida en octavos de cielo (0 a 8 octas) |
| dias_consecutivos_secos | int64 | discreta | 65 | 0 | 0.0 | Recuento entero de días seguidos sin precipitación significativa |
| direccion_viento_predominante | str | nominal | 8 | 202 | 4.5 | Punto cardinal de dirección predominante del viento (N, S, SW, etc.) |
| ocurrencia_lluvia | str | binaria | 2 | 0 | 0.0 | Indicador dicotómico de día lluvioso (Si / No) |
| nivel_alerta_termica | str | ordinal | 4 | 0 | 0.0 | Escala ordenada de severidad térmica: Normal < Alerta Temprana < Alerta < Alarma |
| observacion_sinoptica | str | texto libre | 34 | 0 | 0.0 | Reporte descriptivo de la condición sinóptica diaria |