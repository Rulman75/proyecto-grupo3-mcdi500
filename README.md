# Evolución de volúmenes de Residuos generados en Chile 2023-2025

Proyecto del curso **MCDI500 – Programación para la Ciencia de Datos** (Magíster en Ciencia de Datos e Inteligencia Artificial, Universidad Andrés Bello). Grupo 3.

## Integrantes

| Nombre | Usuario GitHub |
|---|---|
| Madeleine Natalia Magdalena Aguilera Alvear | `@Madiaguileraalvear` |
| Victoria Álvarez Pinto | `@victoria-eap` |
| Ignacio Peña Pizarro | `@ignaciopenap` |
| Raúl Hormazábal Figueroa | `@Rulman75` |

Docente: Dr. Omar Salinas Silva.

## Situación problematizadora

Los establecimientos que generan residuos peligrosos sobre los umbrales de la normativa deben declararlos cada año en el Sistema de Declaración y Seguimiento de Residuos Peligrosos (SIDREP). Cuando un establecimiento deja de aparecer en el registro, no es posible saber, solo con el registro, si cerró, si bajó del umbral de declaración o si dejó de declarar. Esta incertidumbre afecta a:

- **La fiscalización** (Superintendencia del Medio Ambiente y Seremis de Salud), que necesita priorizar qué establecimientos verificar.
- **La planificación de la capacidad de tratamiento y disposición** (empresas del sector y gobiernos regionales), que es distinta si el volumen proviene de un núcleo estable de generadores o de establecimientos que cambian cada año.

## Declaración de Integridad Académica y Asistencia de IA

En cumplimiento con las normas de honestidad y rigor académico, se declara que para el desarrollo de este proyecto se utilizó asistencia de Inteligencia Artificial generativa, como Antigravity y Claude, aplicada a las siguientes tareas:

- *Construcción de la Base_Maestra_2023_2025:* asistencia técnica para consolidar tres bases de datos correspondientes a tres periodos anuales distintos. La IA apoyó en la lógica de homologación y estandarización de nombres y formatos de columnas, así como en el filtrado para conservar exclusivamente aquellas variables consistentes y comparables a lo largo de los tres años.
  
- *Guía de indagación analítica:* asistencia interactiva en el planteamiento y estructuración de preguntas de análisis exploratorio sobre el dataset unificado.
- *Desarrollo del notebook:* sugerencia de sintaxis para la incorporación progresiva de celdas de código de procesamiento, cálculo estadístico y visualización.

Su intervención se limitó a:

- Actuar como guía interactiva en la propuesta y formulación de preguntas analíticas exploratorias.
- Apoyar en la sugerencia inicial de sintaxis y bloques de código para el tratamiento de datos.

La autoría intelectual, el criterio metodológico, la validación de la veracidad de los datos, la eliminación de sesgos y las conclusiones interpretativas corresponden íntegramente a los miembros del equipo, quienes asumen total responsabilidad por el contenido presentado.

## Pregunta del proyecto

> ¿Qué establecimientos se mantienen como generadores de residuos peligrosos entre 2023, 2024 y 2025, cuánto varía su volumen año a año, y qué parte del cambio total se explica por establecimientos que entran o salen del registro?

**Unidad de observación:** cada fila de la base corresponde a un establecimiento × año × residuo declarado (con su peligrosidad y estado físico), no a un establecimiento. Para seguir a cada establecimiento entre años se usa `id_vu`.

## Datos

### Fuente

Declaraciones de generación de residuos peligrosos (SIDREP), publicadas por el Ministerio del Medio Ambiente a través del Registro de Emisiones y Transferencias de Contaminantes (RETC) y del portal de datos abiertos del Estado:

- Página del conjunto: https://datos.gob.cl/dataset/generacion-de-residuos-peligrosos
- Fecha de descarga: 08-11-2026
- Licencia: Creative Commons Attribution (CC BY 4.0)

### Archivos originales y Base Maestra (`F1/data/raw/Base_Maestra_2023_2025.xlsx`)

| Año | Archivo origen RETC | Formato original | Filas |
|---|---|---|---|
| 2023 | `gen-sidrep-2023-ckan.csv` | CSV separado por `;`, UTF-8 | 38.433 |
| 2024 | `gen-sidrep-2024-ckan.xlsx` | Excel | 39.518 |
| 2025 | `ckan_respel_gen_2025.xlsx` | Excel | 40.329 |
| **Total consolidado** | **`F1/data/raw/Base_Maestra_2023_2025.xlsx`** | **Excel (`.xlsx`)** | **118.280** |

La base maestra consolidada cuenta con **118.280 filas × 21 columnas** comunes homologadas entre los tres años (por ejemplo, la cantidad se llama `cantidad_kg` en 2023, `cantidad_kilos` en 2024 y `cantidad_transferencia` en 2025).

| Variable | Descripción |
|---|---|
| `año` | Año de la declaración (`2023`, `2024`, `2025`) |
| `id_vu` | Identificador del establecimiento en Ventanilla Única (clave para seguirlo entre años) |
| `rut_razon_social` | RUT de la empresa titular |
| `id_ciiu4`, `ciiu4` | Código y nombre de actividad económica CIIU (4 dígitos) |
| `id_ciiu6`, `ciiu6` | Código y nombre de actividad económica CIIU (6 dígitos) |
| `id_rubro`, `rubro` | Código y nombre del rubro productivo |
| `codigo_territorial`, `comuna`, `provincia`, `region` | Ubicación administrativa |
| `latitud`, `longitud` | Coordenadas geográficas del establecimiento |
| `cantidad_kg` | Cantidad declarada del residuo, en kilogramos (`kg`) |
| `id_peligrosidad`, `peligrosidad` | Característica(s) de peligrosidad; puede tener varias por residuo |
| `id_lista_a` | Código del residuo según la Lista A (D.S. N° 148/2003 MINSAL) |
| `id_estado_materia`, `estado_materia` | Estado físico: sólido, líquido, lodo o gaseoso |

### Problemas de calidad identificados (a tratar en la Fase 2)

- **Formatos distintos entre años:** nombres de región (3 regiones escritas distinto en 2025, generando 19 etiquetas para 16 regiones), formato del texto de `peligrosidad` (812 variantes entre 2023–2024 y 2025), dígito extra en `id_ciiu4` en 2024 (`546` códigos que se reducen al truncar a 5 caracteres alfanuméricos), pérdida de separador decimal en las coordenadas `latitud` y `longitud` de 2024, y mezcla de códigos de comuna antiguos y vigentes en `codigo_territorial`.
- **Faltantes estructurales:** `id_lista_a` falta en el 6,1% de las filas de 2023 y 2024 (`4.764` nulos = `4,03%` del total), y en ninguna de 2025; además existen nulos puntuales en `latitud`/`longitud` (`64`), `cantidad_kg` (`21`) y `rubro`/`ciiu` (`1`).
- **118 filas duplicadas exactas:** se depuran en la Fase 2 dejando `118.162` declaraciones únicas.

### Limitaciones

- El registro incluye solo a los establecimientos obligados a declarar, no a todos los generadores del país.
- Que un establecimiento deje de aparecer no implica que haya dejado de generar residuos.

## Estructura del repositorio

```
proyecto-grupo3-mcdi500/
├── README.md
├── requirements.txt
├── .gitignore
├── F1/
│   ├── notebooks/
│   │   └── F1_Definicion.ipynb
│   ├── docs/
│   │   ├── informe_dataset.md
│   │   └── F1_Definicion.html
│   └── data/
│       ├── raw/          # Base_Maestra_2023_2025.xlsx (intacto, sin modificar)
│       └── processed/
├── F2/                   # limpieza, rescate interanual, imputación y transformación
│   ├── notebooks/
│   │   └── F2_Preprocesamiento.ipynb
│   ├── src/
│   │   └── preprocesamiento.py
│   ├── docs/
│   │   └── bitacora_f2.md
│   └── data/
│       └── processed/    # base_maestra_2023_2025_clean.csv
├── F3/
└── F4/
```

## Requisitos y ejecución
## Requisitos y ejecución

Requiere **Python 3.14** y **Git**. Todos los comandos se ejecutan en una terminal
(Git Bash en Windows, Terminal en macOS/Linux) **desde la raíz del repositorio**.

### 1. Crear el entorno virtual

python -m venv .venv
Crea la carpeta .venv/ con un intérprete de Python propio del proyecto. Las librerías
que se instalen ahí no afectan al resto del computador, y cada integrante trabaja con las
mismas versiones. La carpeta está en .gitignore, por lo que cada persona la crea en su equipo.

### 2. Activar el entorno

source .venv/Scripts/activate      # Windows, Git Bash
# .venv\Scripts\Activate.ps1       # Windows, PowerShell
# source .venv/bin/activate        # macOS y Linux
Ejecute **solo la línea de su sistema** (las que empiezan con # son alternativas).
Activar el entorno hace que python y pip apunten al intérprete de .venv. Se nota
porque la terminal muestra (.venv) al inicio. Hay que activarlo cada vez que se abre
una terminal nueva.

### 3. Instalar las dependencias

python -m pip install -r requirements.txt
Instala las librerías del proyecto con las versiones exactas declaradas en
requirements.txt, lo que permite reconstruir el mismo entorno en cualquier equipo.
Usar python -m pip en vez de pip garantiza que se instale en el Python del entorno activo.

### 4. Activar nbstripout en el repositorio

nbstripout --install
Configura Git para que, al hacer git commit, se eliminen las salidas de los notebooks
(tablas, gráficos, contadores de ejecución). El notebook en pantalla no cambia; solo se
limpia lo que se guarda en el historial. Esto evita conflictos y diferencias ilegibles
entre integrantes. **Cada integrante debe ejecutarlo una vez**, porque la configuración
queda en .git/config, que no se comparte por GitHub.

### 5. Registrar el kernel de Jupyter

python -m ipykernel install --user --name grupo3_mcdi500 --display-name "Python (grupo3-mcdi500)"
Registra el entorno .venv como un kernel para Jupyter y VS Code.
- --user: lo instala solo para su usuario, sin permisos de administrador.
- --name: identificador interno del kernel.
- --display-name: el nombre que aparece en el menú para elegir kernel.

Al abrir un notebook, seleccione el kernel **Python (grupo3-mcdi500)**. Si se usa otro
(por ejemplo, base de Anaconda), el código puede fallar con ModuleNotFoundError
aunque las librerías estén instaladas en .venv.

### 6. Ejecutar los notebooks

python -m jupyter lab

Al abrir un notebook, seleccione el kernel **Python (grupo3-mcdi500)**. Los notebooks usan rutas relativas desde la raíz del repositorio y se ejecutan en orden (`F1/notebooks/F1_Definicion.ipynb`, luego `F2/notebooks/F2_Preprocesamiento.ipynb`).

## Decisiones técnicas

- Los datos originales se conservan intactos en `F1/data/raw/Base_Maestra_2023_2025.xlsx`; el dataset procesado se exporta en `F2/data/processed/base_maestra_2023_2025_clean.csv`.
- Se seleccionan las 21 columnas comunes homologadas entre los tres años (excluyendo columnas administrativas no transversales como razón social textual o folios internos).
- La base maestra pasa todos los requisitos obligatorios del validador del curso (`118.280 filas`, `21 columnas`, múltiples roles analíticos y presencia real de valores faltantes y atípicos).

## Convención de commits

Prefijos semánticos: `docs:`, `data:`, `feat:`, `fix:`, `test:`. Ciclo de trabajo: `git pull` → trabajar → `git add` → `git commit` → `git pull` → `git push`.

## Referencias

- Ministerio del Medio Ambiente de Chile (MMA). (2026). *Registro de Emisiones y Transferencias de Contaminantes (RETC) — Generación de Residuos Peligrosos SIDREP 2023–2025*. Portal de Datos Abiertos del Estado de Chile (`https://datos.gob.cl/dataset/generacion-de-residuos-peligrosos`).
- Ministerio de Salud de Chile (MINSAL). (2003). *Decreto Supremo N° 148/2003: Reglamento Sanitario sobre Manejo de Residuos Peligrosos*.
