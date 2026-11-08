# Evolución de volúmenes de Residuos generados en Chile 2023-2025

Proyecto del curso **MCDI500 – Programación para la Ciencia de Datos** (Magíster en Ciencia de Datos e Inteligencia Artificial, Universidad Andrés Bello). Grupo 3.

## Integrantes

| Nombre | Usuario GitHub |
|---|---|
| Madeleine Natalia Magdalena Aguilera Alvear (@Madiaguileraalvear)
| Victoria Álvarez Pinto (@victoria-eap)
| Ignacio Peña Pizarro (@ignaciopenap)
| Raúl Hormazábal Figueroa (@Rulman75)

Docente: Dr. Omar Salinas Silva.

## Situación problematizadora

Los establecimientos que generan residuos peligrosos sobre los umbrales de la normativa deben declararlos cada año en el Sistema de Declaración y Seguimiento de Residuos Peligrosos (SIDREP). Cuando un establecimiento deja de aparecer en el registro, no es posible saber, solo con el registro, si cerró, si bajó del umbral de declaración o si dejó de declarar. Esta incertidumbre afecta a:

- **La fiscalización** (Superintendencia del Medio Ambiente y Seremis de Salud), que necesita priorizar qué establecimientos verificar.
- **La planificación de la capacidad de tratamiento y disposición** (empresas del sector y gobiernos regionales), que es distinta si el volumen proviene de un núcleo estable de generadores o de establecimientos que cambian cada año.

## Pregunta del proyecto

> ¿Qué establecimientos se mantienen como generadores de residuos peligrosos entre 2023, 2024 y 2025, cuánto varía su volumen año a año, y qué parte del cambio total se explica por establecimientos que entran o salen del registro?

**Unidad de observación:** cada fila de la base corresponde a un establecimiento × año × residuo declarado (con su peligrosidad y estado físico), no a un establecimiento. Para seguir a cada establecimiento entre años se usa `id_vu`.

## Datos

### Fuente

Declaraciones de generación de residuos peligrosos (SIDREP), publicadas por el Ministerio del Medio Ambiente a través del Registro de Emisiones y Transferencias de Contaminantes (RETC) y del portal de datos abiertos del Estado:

- Página del conjunto: https://datos.gob.cl/dataset/generacion-de-residuos-peligrosos
- Fecha de descarga: 08-11-2026
- Licencia: Creative Commons Attribution

### Archivos originales (`F1/data/raw/`, no se modifican)

| Año | Archivo | Formato | Filas |
|---|---|---|---|
| 2023 | `gen-sidrep-2023-ckan.csv` | CSV separado por `;`, UTF-8 | 38.433 |
| 2024 | `gen-sidrep-2024-ckan.xlsx` | Excel | 39.518 |
| 2025 | `ckan_respel_gen_2025.xlsx` | Excel | 40.329 |

### Base maestra (`F1/data/processed/base_maestra_2023_2025.csv`)

Se genera desde los tres archivos originales con el notebook de la Fase 1: **118.280 filas × 22 columnas**. Cada año publica las mismas variables con nombres distintos (por ejemplo, la cantidad se llama `cantidad_kg` en 2023, `cantidad_kilos` en 2024 y `cantidad_transferencia` en 2025), por lo que se homologan los nombres antes de unir.

| Variable | Descripción |
|---|---|
| `año` | Año de la declaración |
| `id_vu` | Identificador del establecimiento (clave para seguirlo entre años) |
| `rut_razon_social` | RUT de la empresa titular |
| `id_ciiu4`, `ciiu4` | Código y nombre de actividad económica CIIU (4 dígitos) |
| `id_ciiu6`, `ciiu6` | Código y nombre de actividad económica CIIU (6 dígitos) |
| `id_rubro`, `rubro` | Código y nombre del rubro |
| `codigo_territorial`, `comuna`, `provincia`, `region` | Ubicación administrativa |
| `latitud`, `longitud` | Coordenadas del establecimiento |
| `cantidad_kg` | Cantidad declarada del residuo, en kilogramos |
| `id_peligrosidad`, `peligrosidad` | Característica(s) de peligrosidad; puede tener varias por residuo |
| `id_lista_a` | Código del residuo según la Lista A |
| `id_estado_materia`, `estado_materia` | Estado físico: sólido, líquido, lodo o gaseoso |

### Problemas de calidad identificados (a tratar en la Fase 2)

- **Formatos distintos entre años:** nombres de región (3 regiones escritas distinto en 2025), formato del texto de `peligrosidad` (se usará `id_peligrosidad`, que es consistente), dígito extra en `id_ciiu4` en 2024 y mezcla de códigos de comuna antiguos y vigentes en `codigo_territorial`.
- **Faltantes estructurales:** `id_lista_a` falta en el 6,1% de las filas de 2023 y 2024, y en ninguna de 2025.
- **118 filas duplicadas exactas:** se revisarán antes de decidir si se eliminan.

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
│   ├── F1_creacion_base_maestra.ipynb
│   └── data/
│       ├── raw/          # archivos originales, sin modificar
│       └── processed/    # base maestra generada por el notebook
├── F2/                   # limpieza y transformación
├── F3/
├── F4/
└── docs/                 # mapa conceptual e informes
```

## Requisitos y ejecución

Requiere **Python 3.14** y **Git**. Todos los comandos se ejecutan desde la raíz del repositorio.

```bash
python -m venv .venv                       # 1. crea el entorno virtual del proyecto
source .venv/Scripts/activate              # 2. lo activa (Windows, Git Bash)
# source .venv/bin/activate                #    macOS y Linux
python -m pip install -r requirements.txt  # 3. instala las versiones exactas de las librerías
nbstripout --install                       # 4. limpia las salidas de los notebooks al hacer commit (cada integrante, una vez)
python -m ipykernel install --user --name grupo3_mcdi500 --display-name "Python (grupo3-mcdi500)"  # 5. registra el kernel
python -m jupyter lab                      # 6. abre JupyterLab
```

Al abrir un notebook, seleccione el kernel **Python (grupo3-mcdi500)**. Los notebooks usan rutas relativas desde la raíz del repositorio y se ejecutan en orden (F1, luego F2).

## Decisiones técnicas

- Los archivos originales se conservan intactos en `F1/data/raw/`; la base maestra se regenera siempre desde ellos con código, nunca se edita a mano.
- Se seleccionan 22 columnas comunes a los tres años. Se excluyen :
- La base maestra pasa los requisitos obligatorios del validador del curso.

## Convención de commits

Prefijos semánticos: `docs:`, `data:`, `feat:`, `fix:`. Ciclo de trabajo: `git pull` → trabajar → `git add` → `git commit` → `git pull` → `git push`.

## Referencias

