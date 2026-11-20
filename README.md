# Proyecto Grupo 3 — MCDI500: Programación para la Ciencia de Datos (Fases 1 a 4)

**Universidad Andrés Bello — Magíster en Ciencia de Datos e Inteligencia Artificial**  
**Asignatura:** MCDI500 — Programación para la Ciencia de Datos  
**Docente:** Dr. Omar Iván Salinas Silva  
**Integrantes (Grupo 3):**
- Victoria Álvarez Pinto (`@victoria-eap`)
- Raúl Hormazábal Figueroa (`@Rulman75`)
- Ignacio Peña Pizarro (`@ignaciopenap`)S

---

## 1. Pregunta y Objetivos Analíticos del Proyecto

- **Pregunta analítica:** *¿Qué establecimientos (`id_vu`) se mantienen como generadores de residuos peligrosos entre 2023, 2024 y 2025, cuánto varía su volumen (`cantidad_kg`) año a año, y qué parte del cambio total se explica por establecimientos que entran o salen del registro?*
- **Objetivo general:** Determinar la persistencia interanual de los establecimientos generadores de residuos peligrosos en Chile durante el trienio 2023–2025 y cuantificar el peso relativo del núcleo persistente frente a la entrada y salida de establecimientos en la variación del volumen total declarado, según región y rubro productivo.
- **Objetivos específicos:**
  - **OE1:** Cuantificar la proporción de establecimientos del núcleo persistente (3 años) frente a intermitentes (2 años) y ocasionales (1 año) y su participación en el volumen nacional (`F4/figuras/fig1_persistencia_vs_rotacion.png`).
  - **OE2:** Descomponer la variación interanual 2023–2025 por grupo de persistencia y determinar la concentración por rubro productivo (`F4/figuras/fig2_evolucion_y_concentracion_rubros.png`).
  - **OE3:** Caracterizar la tasa regional de Gran Generador (`>= 12 t/año`) con intervalos de Wilson al 95 % y controlar la asociación por el rubro minero como variable de confusión (`F4/figuras/fig3_gradiente_regional_gran_generador.png` y `fig4_control_confusion_y_factor_mentira.png`).

---

## 2. Arquitectura del Repositorio Consolidado (`F1`, `F2`, `F3`, `F4`, `src/` y `tests/`)

```text
proyecto-grupo3-mcdi500/
├── .gitignore                                         # Excluye .venv/, cachés y archivos crudos con RUT
├── .mailmap                                           # Unifica identidades de autor en el historial Git
├── CHANGELOG.md                                       # Registro cronológico de mejoras con commits vinculados (Apartado 27)
├── README.md                                          # Documentación general e instrucciones de ejecución F1-F4
├── requirements.txt                                   # 10 dependencias estrictas del proyecto (incluye pytest>=8.0)
├── src/                                               # Paquete compartido único (Alta cohesión y bajo acoplamiento)
│   ├── __init__.py
│   ├── carga.py                                       # Ingesta segura y diagnóstico estadístico de variables
│   ├── limpieza.py                                    # Limpieza determinista, versión funcional F2 y comparación S1
│   ├── transformadores.py                             # Transformador(ABC), deepcopy, 3 clases hijas y Strategy
│   ├── pipeline.py                                    # Pipeline polimórfico, BitacoraObserver y AuditoriaNulosObserver
│   ├── medicion.py                                    # Entorno hardware, benchmarks timeit/tracemalloc y recursividad
│   └── comunicacion.py                                # Fase 4: carga de artefactos F3, copia interpretable e IC Wilson
├── tests/                                             # Suite de 18 pruebas unitarias ejecutables con pytest
│   ├── conftest.py
│   ├── test_transformadores_pipeline.py               # Pruebas de ABC, deepcopy, inmutabilidad y train/test
│   ├── test_recursividad_limpieza.py                  # Pruebas de árbol vacío, 1 nivel, nulos y equivalencia POO
│   └── test_comunicacion_f4.py                        # Pruebas de reversión de escalamiento, categorías e IC Wilson
├── F1/
│   ├── data/raw/.gitkeep                              # Destino local de Base_Maestra_2023_2025.xlsx (no versionado)
│   ├── notebooks/F1_Definicion.ipynb                  # Cuaderno ejecutable de Fase 1 (10 celdas [1..5])
│   └── docs/ (informe_dataset.md, F1_Definicion.html)
├── F2/
│   ├── data/processed/                                # Matriz procesada única y los 4 artefactos formales de F3
│   ├── notebooks/F2_Preprocesamiento.ipynb            # Cuaderno ejecutable de Fase 2 (12 celdas [1..6])
│   └── docs/ (bitacora_f2.md, F2_Preprocesamiento.html)
├── F3/
│   ├── notebooks/F3_NucleoAlgoritmico_POO.ipynb       # Cuaderno ejecutable de Fase 3 (18 celdas [1..9])
│   └── docs/ (bitacora_f3.md, F3_NucleoAlgoritmico_POO.html)
└── F4/
    ├── figuras/                                       # 4 figuras explicativas exportadas a 200 dpi (.png)
    ├── notebooks/F4_Visualizacion_Comunicacion.ipynb  # Cuaderno integrador de Fase 4 (14 celdas [1..7])
    └── docs/ (hallazgos_f4.csv, metadatos_f4.json, F4_Visualizacion_Comunicacion.html)
```

---

## 3. Instrucciones de Ejecución Completa Desde Cero (`F1 → F2 → F3 → F4` y `pytest`)

```bash
git clone https://github.com/Rulman75/proyecto-grupo3-mcdi500.git
cd proyecto-grupo3-mcdi500
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt

# 1. Ejecutar las 18 pruebas unitarias automatizadas:
python -m pytest tests -v

# 2. Ejecutar los 4 cuadernos en orden (F3 exporta los 4 artefactos que consume F4):
python -m nbconvert --to notebook --execute --inplace F1/notebooks/F1_Definicion.ipynb
python -m nbconvert --to notebook --execute --inplace F2/notebooks/F2_Preprocesamiento.ipynb
python -m nbconvert --to notebook --execute --inplace F3/notebooks/F3_NucleoAlgoritmico_POO.ipynb
python -m nbconvert --to notebook --execute --inplace F4/notebooks/F4_Visualizacion_Comunicacion.ipynb
```