# Proyecto Grupo 3 — MCDI500: Programación para la Ciencia de Datos

**Universidad Andrés Bello — Magíster en Ciencia de Datos e Inteligencia Artificial**  
**Asignatura:** MCDI500 — Programación para la Ciencia de Datos  
**Docente:** Dr. Omar Iván Salinas Silva  
**Integrantes (Grupo 3):**
- Madeleine Aguilera Alvear (`@Madiaguileraalvear`)
- Victoria Álvarez Pinto (`@victoria-eap`)
- Raúl Hormazábal Figueroa (`@Rulman75`)
- Ignacio Peña Pizarro (`@ignaciopenap`)

---

## 1. Pregunta y Objetivo Analítico del Proyecto

- **Pregunta analítica:** *¿Qué establecimientos (`id_vu`) se mantienen como generadores de residuos peligrosos entre 2023, 2024 y 2025, cuánto varía su volumen (`cantidad_kg`) año a año, y qué parte del cambio total se explica por establecimientos que entran o salen del registro?*
- **Objetivo general:** Determinar la persistencia interanual de los establecimientos generadores de residuos peligrosos en Chile durante el trienio 2023–2025 y cuantificar el peso relativo del núcleo persistente frente a la entrada y salida de establecimientos en la variación del volumen total declarado, según región y rubro productivo.

---

## 2. Arquitectura del Repositorio (`F1`, `F2`, `F3`, `src/` y `tests/`)

```text
proyecto-grupo3-mcdi500/
├── .gitignore                                         # Excluye .venv/, cachés y archivos crudos con RUT
├── .mailmap                                           # Unifica identidades de autor de los 4 integrantes
├── README.md                                          # Documentación e instrucciones de ejecución y pruebas
├── requirements.txt                                   # 10 dependencias estrictas del proyecto (incluye pytest)
├── src/                                               # Paquete compartido (Alta cohesión y bajo acoplamiento)
│   ├── __init__.py
│   ├── carga.py                                       # Ingesta segura y diagnóstico estadístico de variables
│   ├── limpieza.py                                    # Funciones deterministas, versión funcional F2 y comparación S1
│   ├── transformadores.py                             # Transformador(ABC), 3 clases hijas y patrón Strategy
│   ├── pipeline.py                                    # Pipeline polimórfico, BitacoraObserver y AuditoriaNulosObserver
│   └── medicion.py                                    # Benchmarks timeit/tracemalloc y recursividad CIIU
├── tests/                                             # Suite de pruebas unitarias automatizadas con pytest
│   ├── test_transformadores_pipeline.py               # Pruebas de ABC, encapsulamiento, inmutabilidad y Pipeline
│   └── test_recursividad_limpieza.py                  # Pruebas de recursividad (vacío, 1 nivel, nulos) y equivalencia
├── F1/
│   ├── data/raw/.gitkeep                              # Destino local de Base_Maestra_2023_2025.xlsx (no versionado)
│   ├── notebooks/F1_Definicion.ipynb                  # Cuaderno ejecutable de Fase 1
│   └── docs/ (informe_dataset.md, F1_Definicion.html)
├── F2/
│   ├── data/processed/base_maestra_2023_2025_clean.csv# Único dataset procesado canónico (118.141 × 61, 0 nulos)
│   ├── notebooks/F2_Preprocesamiento.ipynb            # Cuaderno ejecutable de Fase 2
│   └── docs/ (bitacora_f2.md, F2_Preprocesamiento.html)
└── F3/
    ├── notebooks/F3_NucleoAlgoritmico_POO.ipynb       # Cuaderno ejecutable central de Fase 3 (18 celdas)
    └── docs/ (bitacora_f3.md, F3_NucleoAlgoritmico_POO.html)
```

---

## 3. Instrucciones de Instalación, Descarga de Datos y Ejecución Desde Cero

### Paso 1: Clonar el repositorio y crear el entorno virtual
```powershell
git clone https://github.com/Rulman75/proyecto-grupo3-mcdi500.git
cd proyecto-grupo3-mcdi500
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Paso 2: Ubicar el archivo de datos crudos (Protección de RUT)
Por cumplimiento ético y de protección de datos personales (el campo `rut_razon_social` del registro original contiene 398 RUT de personas naturales), el archivo crudo **no se almacena en GitHub** y está excluido en `.gitignore`.
1. Descargue los datos abiertos de generación de residuos peligrosos (SIDREP 2023–2025) desde el Portal de Datos Abiertos del Gobierno de Chile: https://datos.gob.cl/dataset/generacion-de-residuos-peligrosos
2. Ubique el archivo consolidado en la ruta local:
   ```text
   F1/data/raw/Base_Maestra_2023_2025.xlsx
   ```

### Paso 3: Ejecutar la suite de pruebas automatizadas (`pytest`)
Desde la raíz del repositorio con el entorno `.venv` activo, ejecute:
```powershell
pytest tests -v
```
Se ejecutarán las 10 pruebas unitarias sobre tablas pequeñas construidas a mano verificando clases abstractas (`ABC`), encapsulamiento (`deepcopy`), no mutación del `DataFrame` de entrada, consistencia de columnas entre entrenamiento y prueba, observadores múltiples, casos borde de recursividad (árbol vacío, de un nivel y con nulos) y equivalencia funcional vs POO.

### Paso 4: Ejecutar los notebooks de las Fases 1, 2 y 3
Puede abrirlos interactivamente en JupyterLab / VS Code (`Kernel -> Restart Kernel and Run All Cells`) o ejecutarlos por línea de comandos desde la raíz del repositorio:
```powershell
python -m nbconvert --to notebook --execute --inplace F1/notebooks/F1_Definicion.ipynb
python -m nbconvert --to notebook --execute --inplace F2/notebooks/F2_Preprocesamiento.ipynb
python -m nbconvert --to notebook --execute --inplace F3/notebooks/F3_NucleoAlgoritmico_POO.ipynb
```

---

## 4. Declaración de Uso Ético de IA Generativa
Durante el desarrollo de las Fases 1, 2 y 3 se utilizó asistencia de herramientas de inteligencia artificial generativa como apoyo para la estructuración de docstrings, refactorización modular bajo estándares PEP 8 y diseño de pruebas unitarias con `pytest`. Todas las decisiones metodológicas, reglas de negocio del dominio RETC/SIDREP (D.S. N.° 148/2003), validaciones estadísticas y verificaciones de resultados fueron revisadas, ejecutadas y contrastadas íntegramente por los cuatro integrantes del Grupo 3.
