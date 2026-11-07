# Proyecto Grupo 3 — MCDI500

Caracterización computacional de los factores meteorológicos y termodinámicos asociados a la ocurrencia diaria de precipitaciones y eventos de alerta térmica en estaciones meteorológicas de Chile (2021–2025).

## Integrantes
- Madeleine Natalia Magdalena Aguilera Alvear (@Madiaguileraalvear)
- Victoria Álvarez Pinto (@victoria-eap)
- Ignacio Peña Pizarro (@Ignacio)
- Raúl Hormazábal Figueroa (@Rulman75)

## Datos
- **Fuente:** Dirección Meteorológica de Chile (DMC) y Explorador Climático CR2 (`https://climatologia.meteochile.gob.cl` / `https://explorador.cr2.cl`).
- **Licencia:** Datos Abiertos del Estado de Chile / CC BY 4.0.
- **Volumen y variables:** 4.500 registros diarios (2021–2025) y 16 variables que cubren los 8 roles analíticos del curso (6 continuas, 2 discretas, 1 binaria, 1 ordinal, 2 nominales, 1 fecha, 2 de alta cardinalidad/texto libre y 1 identificador), con entre 4,5% y 14,2% de valores faltantes reales en sensores.
- **Ubicación:** El archivo original inmutable se ubica en `F1/data/raw/clima_estaciones_chile_raw.csv` y el conjunto limpio y transformado se exporta en la Fase 2 a `F2/data/processed/clima_estaciones_chile_clean.csv`.

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
- **Aislamiento y reproducibilidad:** Se aísla el entorno en `.venv` (excluido en `.gitignore`) y se versiona `requirements.txt` para garantizar reproducibilidad entre equipos Windows y macOS.
- **Higiene de notebooks:** Se activa `nbstripout` para limpiar las salidas JSON de los notebooks antes de cada commit y evitar conflictos de merge, exportando copias ejecutadas en HTML/PDF como evidencia para el informe.
- **Inmutabilidad del dato crudo:** El archivo `F1/data/raw/clima_estaciones_chile_raw.csv` nunca se sobrescribe; el pipeline de la Fase 2 escribe sus salidas en `F2/data/processed/`.
- **Descarte de `dropna()` e imputación por grupo:** Eliminar filas con valores faltantes descartaría 1.997 registros (44,4% de la muestra) y sesgaría los eventos de tormenta. Se opta por imputar variables continuas con la mediana agrupada por `macrozona` (dada la presencia de valores atípicos verificados por rango intercuartílico) y registrar banderas binarias de imputación (`_imputado`).