# Auditoría Automatizada de Góndolas mediante Visión Artificial (Walmart Chile)

## 📌 Descripción General del Proyecto

Este repositorio contiene el código fuente, la documentación técnica y la arquitectura del sistema desarrollado para la asignatura **Proyecto de Título (APT122 / Capstone)** en **Duoc UC**, en colaboración con **Walmart Chile**.

El proyecto aborda la automatización de la auditoría de espacios en salas de venta de supermercados mediante algoritmos de **Visión Artificial (Computer Vision)**. La solución analiza capturas fotográficas de cámaras de seguridad para detectar en tiempo real la disponibilidad de stock y cuantificar los espacios vacíos en góndola ("quiebres de stock" e "inventarios fantasmas").

---

## 🎯 Definición del Alcance

### 1. Dominio de Aplicación
* **Categoría Seleccionada**: Góndolas de **Alimentos No Perecibles** (cajas, latas, frascos, bolsas).
* **Actualización de Alcance**: Se descarta de forma definitiva el monitoreo de cestas de panadería, enfocando la arquitectura exclusivamente en la complejidad visual de los estantes de no perecibles.
* **Desafíos Visuales del Entorno**:
  * **Alto ruido visual**: Variaciones abruptas de iluminación, reflejos en empaques plásticos/metálicos y sombras al fondo del estante.
  * **Perspectiva y lentes**: Distorsión óptica por ángulos oblicuos de cámaras de seguridad y lentes tipo *fisheye*.
  * **La Trampa del Apilamiento**: Diferenciación entre espacio libre útil para reposición y espacio vertical vacío donde no es posible apilar productos por fragilidad o geometría.

### 2. Supuestos del Dominio
* **Segmentación automática de ROI**: El sistema detecta por sí solo la góndola y sus repisas en cada imagen. Ningún usuario dibuja ni configura zonas ROI por cámara.
* **Profundidad constante de góndola**: Las góndolas reales tienen entre 20 y 30 cm de profundidad; el sistema usa un valor fijo de **25 cm** para todos los casos. No estima profundidad: analiza la vista frontal 2D de la góndola, y en el Nivel 1 el volumen libre se obtiene del área frontal libre multiplicada por esos 25 cm.

---

## 💡 Objetivos y Niveles de Solución

El proyecto contempla una estructura de dos niveles de solución para garantizar la viabilidad técnica:

| Criterio | Solución Óptima (Nivel 1) | MVP Alternativo (Nivel 2) |
| :--- | :--- | :--- |
| **Objetivo Principal** | Medición espacial y volumétrica exacta del espacio libre (profundidad constante de 25 cm) | Alerta macro por umbral binario de stock |
| **Métrica de Salida** | Centímetros o porcentaje exacto de espacio vacío por repisa | ¿Espacio libre ≥ 30% del frente de la góndola? (Sí / No) |
| **Granularidad** | Segmentado nivel por nivel de la góndola (Nivel 1, 2, 3...), con repisas detectadas automáticamente | Análisis global de la góndola detectada automáticamente |
| **Complejidad** | Alta (Segmentación espacial + Visión Computacional) | Media (Detección por umbral de píxeles / parches) |

---

## 🛠️ Requerimientos Funcionales (RF)

* **RF01 - Ingesta de Imágenes**: Procesamiento estático de fotogramas en formato imagen (tiempo de inferencia objetivo: 2 a 5 segundos por imagen).
* **RF02 - Detección de Espacios Vacíos**: Identificación de regiones sin producto dentro de las regiones de interés (ROI) correspondientes a la góndola, que el sistema segmenta automáticamente.
* **RF03 - Cálculo de Disponibilidad**: Estimación cuantitativa del espacio libre (porcentaje/cm o alerta cuando el espacio libre llega al 30% del frente de la góndola), asumiendo profundidad de góndola constante (25 cm).
* **RF04 - Generación de Alertas**: Emisión de notificaciones prioritarias para el equipo de reposición cuando se detecte un quiebre de stock.
* **RF05 - Módulo de Reportería**: Exportación de datos analíticos auditados en formatos **Excel (.xlsx)**, **CSV** y **PDF**.

---

## 👥 Perfiles de Usuario

1. **Reponedor de Tienda**: Recibe alertas inmediatas en dispositivos móviles para acudir a los pasillos con quiebre crítico.
2. **Jefe de Salón / Supervisor**: Visualiza dashboards de disponibilidad por pasillo y exporta reportes periódicos de desempeño.
3. **Administrador de Sistema**: Configura planogramas, cámaras y umbrales de alerta, y gestiona usuarios. No define zonas ROI: el sistema segmenta la góndola automáticamente.

---

## 🏗️ Estrategia Algorítmica y Arquitectura

* **Enfoque Híbrido**: Evaluación de modelos de extracción de características (**YOLO26** de Ultralytics, con cabeza sin NMS para góndolas densas) combinados obligatoriamente con **Visión Computacional Clásica** (detección de bordes, transformaciones matriciales y filtros morfológicos) para mantener control matemático sobre el ruido visual. La segmentación automática de la góndola y sus repisas es parte de este pre-procesamiento clásico: se ejecuta sobre la imagen ya corregida (dewarping de lente y luego CLAHE) y antes de la inferencia.
* **Pipeline Modular**: Separación física de los componentes de *Pre-procesamiento*, *Inferencia de Modelo* y *Post-procesamiento*.
* **Código de Producción**: Desarrollo exclusivo en scripts modulares de Python (`.py`), descartando notebooks para la ejecución core.

---

## 📊 Estrategia de Datos y Evaluación

* **Dataset de Entrenamiento**: Curaduría propia mediante fuentes públicas open-source (ej. *SKU-110K*, *Hugging Face Grocery Shelves*, *Kaggle Supermarket Shelves*) con estandarización estricta de coordenadas de anotación (`[x_min, y_min, x_max, y_max]`).
* **Sin imágenes reales de Walmart**: por privacidad, Walmart Chile no puede compartir imágenes de sus cámaras de seguridad (informado el 2026-10-01). Las condiciones de cámara de sala (vista alta y oblicua, lente gran angular/*fisheye*, baja resolución, compresión) se simulan generando imágenes sintéticas desde los datasets públicos, transformando también sus anotaciones (ver [docs/datasets.md](docs/datasets.md)).
* **Prueba Ciega (Dataset Oculto)**: la evaluación contra el **Dataset Oculto** de Walmart Chile (imágenes reales de sala con condiciones complejas) solo es posible si Walmart ejecuta el sistema en sus instalaciones (imagen Docker) y entrega las métricas, sin que las imágenes salgan de la empresa. Modalidad por confirmar con Walmart.

---

## 📁 Estructura del Repositorio

```text
.
├── docs/                   # Documentación de diseño, minutas y especificaciones
├── src/                    # Código fuente en scripts Python modulares
│   ├── preprocessing/      # Filtros de imagen, segmentación automática y recorte de ROI
│   ├── models/             # Módulos de inferencia (YOLO26 / CV Clásico)
│   ├── postprocessing/     # Cálculo de disponibilidad y alerta (libre ≥ 30%)
│   ├── reporting/          # Generadores de reportes (Excel, CSV, PDF)
│   └── evaluation/         # Métricas de evaluación (fuera del pipeline)
├── scripts/                # CLI del pipeline y visor de segmentación
├── data/                   # Datasets (data/raw y data/processed, no versionados)
├── tests/                  # Pruebas unitarias e integración (pytest)
├── Fase 1/                 # Entregables académicos de la Fase 1 (no modificar)
├── Dockerfile              # Imagen de ejecución del pipeline (python:3.10-slim-trixie)
├── CLAUDE.md               # Memoria de proyecto y reglas de código para IA
├── PROGRESS.md             # Bitácora de tareas por sprint
├── README.md               # Documentación principal del repositorio
└── requirements.txt        # Dependencias del proyecto
```

### Configuración de un entorno nuevo

Requisitos: git, Python 3.10 o superior (el CI y la imagen Docker usan
3.10; también se usa 3.14 en local) y acceso de escritura al repositorio
(invitación de GitHub aceptada).

**1. graphify, una vez por PC y fuera del venv.** Los hooks de Claude Code
(`.claude/settings.json`) llaman a `graphify` en cada búsqueda o lectura
sin activar el venv, así que tiene que estar en el `PATH` del sistema.
Se instala con [uv](https://docs.astral.sh/uv/), sin el venv activado:

```bash
winget install astral-sh.uv        # o: python -m pip install uv
uv tool install graphifyy==0.9.70
uv tool update-shell               # agrega ~/.local/bin al PATH; cerrar y reabrir la terminal y VS Code
graphify --version                 # debe decir 0.9.70
```

**2. Proyecto:**

```bash
git clone https://github.com/marianapeachy/capstone.git && cd capstone
python -m venv .venv            # activar: .venv\Scripts\activate (Windows) / source .venv/bin/activate
pip install -r requirements.txt
graphify update .               # genera graphify-out/ (no se versiona)
cp .env.example .env            # opcional: API key de Roboflow (Windows: copy .env.example .env)
pytest tests/
```

`pytest tests/` no necesita datasets, pesos ni GPU: construye YOLO26 desde
su YAML, sin conexión. Si todo pasa, el entorno quedó listo.

**3. Claude Code:** crear `CLAUDE.local.md` en la raíz (no se versiona)
con la línea `Integrante: <nombre>` (el mismo nombre que se usa en
`(dueño: <nombre>)` de `PROGRESS.md`). Con eso Claude sabe qué ítems son
de cada uno y cuál proponer después (ver "Trabajo en equipo" en
`CLAUDE.md`).

- **PowerShell no deja activar el venv** ("la ejecución de scripts está
  deshabilitada"): correr una vez
  `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` y volver a
  activar.
- **`graphify --version` no da 0.9.70**: otra copia de `graphify` tapa
  la de `uv tool` en el `PATH` (p. ej. una instalada con `pip` en el
  Python global o en un venv). `where.exe graphify` (Windows) o
  `which -a graphify` (bash) lista todas en orden; la primera debe ser
  la de `%USERPROFILE%\.local\bin`. Quitar las otras con
  `pip uninstall graphifyy` en el Python donde estén.
- **Datos** (no se versionan): `python scripts/download_datasets.py` los
  descarga a `data/raw/` (Roboflow pide `ROBOFLOW_API_KEY`; ver
  [docs/datasets.md](docs/datasets.md)) y luego `python scripts/prepare_datasets.py`.
  `python scripts/evaluate_shard.py` mide la segmentación de repisas contra
  SHARD (`--dataset shard`, 3.6 GB). SKU-110K (12.2 GB) y SHARD (3.6 GB)
  son descargas grandes y pueden cortarse por timeout o reinicio de
  conexión; el script reanuda desde donde quedó, así que basta con
  volver a correr `python scripts/download_datasets.py` las veces que
  haga falta hasta que termine.
- **Claude Code**: instalar la extensión "Claude Code" de Anthropic en VS Code
  e iniciar sesión con la cuenta propia. Claude lee `CLAUDE.md` al empezar, que
  incluye el flujo de trabajo en equipo (ramas, PR y dueños de ítems). Al abrir
  el proyecto, aceptar la instalación de los plugins compartidos
  (`yolo@ultralytics` y `superpowers`, declarados en `.claude/settings.json`).
- **GitHub CLI** (`gh auth login`) para abrir Pull Requests desde la terminal.
- **Docker Desktop** para construir y probar la imagen (ver abajo).
- **Entrenamiento del detector** (PC con GPU NVIDIA): ver
  [docs/training.md](docs/training.md). En Windows, `pip install -r
  requirements.txt` instala PyTorch sin CUDA; para usar la GPU hay que
  reinstalarlo como indica esa guía (paso 1). Para el resto del proyecto
  basta el PyTorch sin CUDA.
- **Antes de tomar trabajo**: leer la sección "Trabajo en equipo" de
  `CLAUDE.md` y elegir un ítem sin dueño de [PROGRESS.md](PROGRESS.md).

### Ejecución local

```bash
pip install -r requirements.txt
pytest tests/
python scripts/run_pipeline.py   # aún sin implementar (ítem #8): termina con NotImplementedError
```

Mientras el ítem #8 esté pendiente, las etapas se prueban por separado:
`python scripts/visualize_segmentation.py` (segmentación, requiere
datasets en `data/raw/`) y los scripts `evaluate_*.py`.

El CI ([.github/workflows/ci.yml](.github/workflows/ci.yml)) corre `pytest` y el `docker build` (con los tests dentro de la imagen) en cada Pull Request hacia `main` y en cada push a `main`; un PR solo se puede mergear con ambos checks en verde.

### Ejecución con Docker

```bash
docker build -t shelfvision-ai .
docker run --rm shelfvision-ai   # corre run_pipeline.py: NotImplementedError hasta el ítem #8
# Pruebas dentro del contenedor (tests/ no se copia a la imagen, se monta):
docker run --rm -v "$(pwd)/tests:/app/tests" shelfvision-ai python -m pytest tests/
```

---

## 📅 Planificación y Cronograma (Carta Gantt)

* **Fase 1 (Semanas 1 - 4 / 20%)**: Inscripción, reunión con cliente, levantamiento de RF y definición de arquitectura.
* **Fase 2 (Semanas 5 - 16 / 50%)**: Desarrollo modular, integración, pruebas continuas con imágenes sintéticas tipo cámara de sala (y con el Dataset Oculto, si Walmart lo ejecuta en sus instalaciones) y Pre-examen.
* **Fase 3 (Semanas 17 - 18 / 30%)**: Ajustes finales, manuales de usuario/instalación y Exposición ante Comisión Evaluadora.

---

## 👨‍💻 Equipo de Desarrollo

* **Asignatura**: Proyecto de Título (APT122 / Capstone) - Duoc UC
* **Integrantes**: Mariana Ramirez, Nicko Cortes, Francisco Sandoval
* **Cliente**: Walmart Chile (Área de Inteligencia Artificial)
