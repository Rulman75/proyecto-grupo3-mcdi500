# Informe de Validación del Dataset (Fase 1) — Grupo 3 MCDI500
- **Archivo evaluado:** `F1\data\raw\Base_Maestra_2023_2025.xlsx`
- **Dimensiones:** 118280 filas × 21 columnas
- **Filas duplicadas exactas:** 118
- **Porcentaje máximo de valores faltantes:** 4.03% (`id_lista_a`: 4.764 nulos)

## Diccionario y Perfil de Variables
| variable | dtype_pandas | rol_analitico | valores_unicos | nulos_n | nulos_pct | descripcion |
| --- | --- | --- | --- | --- | --- | --- |
| año | int64 | fecha | 3 | 0 | 0.0 | Año calendario de la declaración RETC (2023, 2024, 2025) |
| id_vu | int64 | identificador | 12192 | 0 | 0.0 | Identificador numérico del establecimiento en Ventanilla Única |
| rut_razon_social | str | alta cardinalidad | 6779 | 0 | 0.0 | RUT de la organización declarante (se anonimiza por frecuencia en F2/F3) |
| id_ciiu4 | str | alta cardinalidad | 546 | 1 | 0.0 | Código CIIU4 de actividad económica a 4 dígitos (546 códigos) |
| ciiu4 | str | texto libre | 335 | 1 | 0.0 | Glosa descriptiva de la actividad económica según CIIU4 |
| id_ciiu6 | str | alta cardinalidad | 388 | 1 | 0.0 | Código CIIU6 de actividad económica a 6 dígitos (388 códigos) |
| ciiu6 | str | texto libre | 388 | 1 | 0.0 | Glosa descriptiva detallada de la actividad económica según CIIU6 |
| id_rubro | int64 | discreta | 20 | 0 | 0.0 | Código entero del rubro económico RETC (0 a 20) |
| rubro | str | nominal | 19 | 1 | 0.0 | Categoría de rubro industrial o sector productivo (19 rubros) |
| codigo_territorial | int64 | discreta | 380 | 0 | 0.0 | Código Único Territorial (CUT) comunal entero (380 códigos) |
| comuna | str | alta cardinalidad | 344 | 0 | 0.0 | Nombre de la comuna del establecimiento generador (344 comunas) |
| provincia | str | nominal | 58 | 0 | 0.0 | Nombre de la provincia administrativa (58 provincias) |
| region | str | nominal | 19 | 0 | 0.0 | Región administrativa de Chile (16 regiones; 19 etiquetas en crudo) |
| latitud | float64 | continua | 20120 | 64 | 0.05 | Latitud geográfica del establecimiento en grados decimales |
| longitud | float64 | continua | 20112 | 64 | 0.05 | Longitud geográfica del establecimiento en grados decimales |
| cantidad_kg | float64 | continua | 13488 | 21 | 0.02 | Masa anual declarada de residuo peligroso en kilogramos (kg) |
| id_peligrosidad | str | nominal | 587 | 0 | 0.0 | Códigos de característica de peligrosidad D.S. N° 148/2003 |
| peligrosidad | str | texto libre | 812 | 0 | 0.0 | Glosa de característica(s) de peligrosidad declaradas |
| id_lista_a | str | alta cardinalidad | 59 | 4764 | 4.03 | Código Lista A D.S. 148/2003 (59 códigos; se imputa por moda de id_rubro y se codifica por frecuencia) |
| id_estado_materia | int64 | discreta | 4 | 0 | 0.0 | Código administrativo RETC de estado físico (1=sólido, 2=líquido, 3=gaseoso, 4=lodo) |
| estado_materia | str | nominal | 4 | 0 | 0.0 | Estado físico del residuo (sólido, líquido, lodo, gaseoso; se codifica con One-Hot) |
