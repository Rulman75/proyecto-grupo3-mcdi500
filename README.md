# Proyecto Grupo 3 — MCDI500

Caracterización computacional y análisis territorial-sectorial de las declaraciones de generación de residuos peligrosos en Chile durante el período 2023–2025 (Sistema de Declaración y Seguimiento de Residuos Peligrosos, SIDREP / RETC).

## Integrantes
- Madeleine Natalia Magdalena Aguilera Alvear (@Madiaguileraalvear)
- Victoria Álvarez Pinto (@victoria-eap)
- Ignacio Peña Pizarro (@Ignacio)
- Raúl Hormazábal Figueroa (@Rulman75)

## Datos
- **Fuente:** Registro de Emisiones y Transferencias de Contaminantes (RETC) — Ministerio del Medio Ambiente de Chile (`https://datosretc.mma.gob.cl`).
- **Licencia:** Datos Abiertos del Estado de Chile / CC BY 4.0.
- **Volumen y variables:** 118.280 registros anuales de declaración (2023–2025) y 21 variables que cubren los roles analíticos del curso (continuas, discretas, ordinales, nominales, fecha/tiempo, alta cardinalidad, texto libre e identificador), con 118 filas duplicadas exactas, inconsistencias de codificación interanual en regiones (19 etiquetas para 16 regiones) y peligrosidades (812 variantes), pérdida de punto decimal en coordenadas del año 2024 y hasta 4,03% de valores nulos en `id_lista_a`.
- **Ubicación:** El archivo original inmutable se ubica en `F1/data/raw/Base_Maestra_2023_2025.xlsx` y el conjunto limpio y transformado se exporta en la Fase 2 a `F2/data/processed/base_maestra_2023_2025_clean.csv`.

## Estructura del repositorio
- `F1/` Definición del problema y entorno reproducible (`data/raw`, `data/processed`, `notebooks`, `src`, `docs`)
- `F2/` Obtención, exploración, limpieza y transformación de datos (`data/processed`, `notebooks`, `src`, `docs`)
- `F3/` Núcleo algorítmico: programación estructurada, recursiva y POO
- `F4/` Análisis, visualización y comunicación de resultados

## Requisitos y ejecución
Python 3.14

```bash
python -m venv .venv
source .venv/Scripts/activate      # Windows, Git Bash
# .venv\Scripts\Activate.ps1       # Windows, PowerShell
# source .venv/bin/activate        # macOS y Linux
python -m pip install -r requirements.txt
nbstripout --install
python -m ipykernel install --user --name grupo3_mcdi500 --display-name "Python (grupo3-mcdi500)"
```

Ejecutar los notebooks en orden desde la raíz del proyecto:
```bash
python -m jupyter lab
```

## Convención de commits
Prefijos usados: `docs`, `data`, `feat`, `fix`, `test`. Ver Parte XVIII de la guía.

## Decisiones técnicas (Fases 1 y 2)
- **Aislamiento y reproducibilidad:** Se aísla el entorno en `.venv` (excluido en `.gitignore`) y se versiona `requirements.txt` (incluyendo `openpyxl` para lectura de `.xlsx`) para garantizar reproducibilidad entre equipos Windows y macOS.
- **Higiene de notebooks:** Se activa `nbstripout` para limpiar las salidas JSON de los notebooks antes de cada commit y evitar conflictos de merge, exportando copias ejecutadas en HTML/PDF como evidencia para el informe.
- **Inmutabilidad del dato crudo:** El archivo `F1/data/raw/Base_Maestra_2023_2025.xlsx` nunca se sobrescribe; el pipeline de la Fase 2 escribe sus salidas en `F2/data/processed/`.
- **Depuración interanual e imputación por grupo:** Al consolidar los períodos 2023, 2024 y 2025 se eliminan 118 duplicados exactos, se normalizan las 16 regiones de Chile y las categorías de peligrosidad (de 812 a 93 combinaciones canónicas), se rescata la escala decimal de las coordenadas geográficas del año 2024 y se imputan los valores faltantes mediante la mediana agrupada por `region` (numéricas) y moda por `id_rubro` (categóricas) con banderas binarias `_imputado`, evitando perder 5.037 declaraciones (4,26%) con `dropna()`.
