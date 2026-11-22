# Proyecto Grupo 3 — MCDI500: Programación para la Ciencia de Datos (Fases 1 a 4)

**Universidad Andrés Bello — Magíster en Ciencia de Datos e Inteligencia Artificial**  
**Asignatura:** MCDI500 — Programación para la Ciencia de Datos  
**Docente:** Dr. Omar Iván Salinas Silva  
**Integrantes activos (Grupo 3):**
- Victoria Álvarez Pinto (`@victoria-eap`)
- Ignacio Peña Pizarro (`@ignaciopenap`)
- Raúl Hormazábal Figueroa (`@Rulman75`)

*(Nota sobre composición del equipo: En las Fases 1 a 3 participó también Madeleine Aguilera, quien se retiró del programa de Magíster antes del inicio de la Semana 3 / Fase 4).*

---

## 1. Pregunta y Objetivos Analíticos del Proyecto

- **Pregunta analítica:** *¿Qué establecimientos (`id_vu`) se mantienen como generadores de residuos peligrosos entre 2023, 2024 y 2025, cuánto varía su volumen (`cantidad_kg`) año a año, y qué parte del cambio total se explica por establecimientos que entran o salen del registro?*
- **Objetivo general:** Determinar la persistencia interanual de los establecimientos generadores de residuos peligrosos en Chile durante el trienio 2023–2025 y cuantificar el peso relativo del núcleo persistente frente a la entrada y salida de establecimientos en la variación del volumen total declarado, según región y rubro productivo.
- **Objetivos específicos (definidos en Fase 1 y respondidos en Fase 4):**
  - **OE1:** Cuantificar la proporción de establecimientos únicos (`id_vu`) que conforman el núcleo persistente (3 años) frente a los declarantes intermitentes (2 años) u ocasionales (1 año), evaluando su participación en el volumen total declarado y el grado de concentración en el 1 % y 10 % superior de los establecimientos.
  - **OE2:** Descomponer la variación interanual del volumen declarado entre 2023, 2024 y 2025 en el aporte de los establecimientos persistentes, entrantes y salientes, identificando los rubros productivos que concentran la masa del padrón.
  - **OE3:** Caracterizar por establecimiento la proporción regional de Grandes Generadores (`>= 12 toneladas/año`, D.S. N° 148 Art. 25) con intervalos de confianza de Wilson al 95 %, evaluando si la asociación entre persistencia trienal y gran generación se mantiene al controlar por el rubro minero y la macrozona geográfica.

---

## 2. Procedencia del Dataset y Verificación Criptográfica (`SHA-256`)

- **Fuente oficial:** Portal de Datos Abiertos del **Registro de Emisiones y Transferencias de Contaminantes (RETC)** — Subsistema **SIDREP** (Ministerio del Medio Ambiente de Chile): https://datosretc.mma.gob.cl/dataset/generacion-de-residuos-peligrosos
- **Fecha de descarga y consolidación:** 3 de noviembre de 2026 (consolidación en `F1/data/raw/Base_Maestra_2023_2025.xlsx` de los registros anuales 2023, 2024 y 2025 con `118.280 filas × 21 columnas`).
- **Huella criptográfica `SHA-256` oficial de `Base_Maestra_2023_2025.xlsx`:**
  ```text
  7de8ff0ed46488dcc52a551788d12bc3e9c6599a7b9afd1c30eb1139c60dc44b
  ```
- **Verificación automática:** La función `verificar_sha256_origen()` en `src/comunicacion.py` comprueba automáticamente esta huella al ejecutar `F4/notebooks/F4_Visualizacion_Comunicacion.ipynb` (`Celda In[3]`). El archivo bruto no se versiona en Git por contener `398` RUT de personas naturales (anonimizados con `SHA-256` en `src/limpieza.py`).

---

## 3. Entorno de Ejecución y Versiones Fijadas (`requirements.txt`)

- **Versión de Python validada:** `Python 3.14.10` (64 bits).
- **Dependencias fijadas con igualdad estricta (`==`) en `requirements.txt`** (sin `nbstripout` para preservar las salidas ejecutadas de los cuadernos `.ipynb`):
  - `pandas==3.0.6`, `numpy==2.5.4`, `openpyxl==3.1.5`, `matplotlib==3.11.2`, `seaborn==0.13.2`, `pytest==9.2.0`, `jupyter==1.1.1`, `notebook==7.5.5`, `ipykernel==7.2.0`.
- **Tolerancia declarada en la prueba de equivalencia Funcional vs. POO (Fase 3):** Se utiliza `pd.testing.assert_frame_equal(..., check_exact=False, rtol=1e-5, atol=1e-8)` para contemplar posibles diferencias de redondeo IEEE 754 en punto flotante de 64 bits (`float64`), verificándose empíricamente una diferencia numérica máxima observada de **`0,0`** entre ambas matrices (`118.141 × 61`).

---

## 4. Arquitectura del Repositorio y Salidas de la Fase 4

```text
proyecto-grupo3-mcdi500/
├── .gitignore                                         # Excluye .venv/, cachés y archivos crudos con RUT
├── .mailmap                                           # Unifica identidades de autor en el historial Git
├── CHANGELOG.md                                       # Registro cronológico de mejoras con commits vinculados (Apartado 27)
├── README.md                                          # Documentación general, SHA-256 e instrucciones F1-F4
├── requirements.txt                                   # Versiones exactas fijadas con == (validado en Python 3.14.10)
├── src/                                               # Paquete compartido único (Alta cohesión y bajo acoplamiento)
│   ├── __init__.py
│   ├── carga.py                                       # Ingesta segura y diagnóstico estadístico de variables
│   ├── limpieza.py                                    # Limpieza determinista, SHA-256 de RUT y versión funcional F2
│   ├── transformadores.py                             # Transformador(ABC), deepcopy, 3 clases hijas y Strategy
│   ├── pipeline.py                                    # Pipeline polimórfico, BitacoraObserver y AuditoriaNulosObserver
│   ├── medicion.py                                    # Entorno hardware, benchmarks timeit/tracemalloc y recursividad
│   └── comunicacion.py                                # Fase 4: artefactos F3, copia interpretable, unidad por planta, descomposición y Lorenz
├── tests/                                             # Suite de 21 pruebas unitarias ejecutables con pytest
│   ├── conftest.py
│   ├── test_transformadores_pipeline.py               # Pruebas de ABC, deepcopy, inmutabilidad y train/test
│   ├── test_recursividad_limpieza.py                  # Pruebas de árbol vacío, 1 nivel, nulos y equivalencia POO
│   └── test_comunicacion_f4.py                        # 7 pruebas de reversión, categorías, Wilson, descomposición, Lorenz e id_vu
├── F1/ (notebooks/F1_Definicion.ipynb, docs/informe_dataset.md, docs/F1_Definicion.html)
├── F2/ (data/processed/ con los 4 artefactos formales de F3, notebooks/F2_Preprocesamiento.ipynb, docs/)
├── F3/ (notebooks/F3_NucleoAlgoritmico_POO.ipynb, docs/bitacora_f3.md, docs/F3_NucleoAlgoritmico_POO.html)
└── F4/
    ├── notebooks/F4_Visualizacion_Comunicacion.ipynb  # Cuaderno integrador de Fase 4 ejecutado (14 celdas [1..7])
    ├── figuras/                                       # 4 figuras explicativas exportadas a 200 dpi (.png):
    │   ├── fig1_persistencia_vs_rotacion.png          # OE1: Persistencia vs masa y Curva de Lorenz / Top 1% y 10% del núcleo
    │   ├── fig2_evolucion_y_concentracion_rubros.png  # OE2: Evolución + descomposición interanual y Minería vs Otras actividades (CIIU4)
    │   ├── fig3_gradiente_regional_gran_generador.png # OE3: Gradiente regional por planta (N=12.189) con/sin Minería y persistencia
    │   └── fig4_control_confusion_y_factor_mentira.png# OE3: Doble control de confusión (Persistencia x Minería x Macrozona Norte)
    └── docs/
        ├── hallazgos_f4.csv                           # Tabla maestra con cifra, ic_wilson_95, mediana_y_ric y celda_notebook
        ├── metadatos_f4.json                          # Resumen JSON verificable de la ejecución de Fase 4
        └── F4_Visualizacion_Comunicacion.html         # Exportación HTML completa con salidas visibles
```

---

## 5. Instrucciones de Ejecución Completa Desde un Clon Limpio (`F1 → F2 → F3 → F4` y `pytest`)

```bash
git clone https://github.com/Rulman75/proyecto-grupo3-mcdi500.git
cd proyecto-grupo3-mcdi500
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt

# 1. Ejecutar las 21 pruebas unitarias automatizadas:
python -m pytest tests -v

# 2. Ejecutar los 4 cuadernos en orden (F3 exporta los 4 artefactos que consume F4):
python -m nbconvert --to notebook --execute --inplace F1/notebooks/F1_Definicion.ipynb
python -m nbconvert --to notebook --execute --inplace F2/notebooks/F2_Preprocesamiento.ipynb
python -m nbconvert --to notebook --execute --inplace F3/notebooks/F3_NucleoAlgoritmico_POO.ipynb
python -m nbconvert --to notebook --execute --inplace F4/notebooks/F4_Visualizacion_Comunicacion.ipynb
```