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
* **Profundidad constante de góndola**: Las góndolas reales tienen entre 20 y 30 cm de profundidad; el sistema usa un valor fijo de **25 cm** para todos los casos. No estima profundidad: analiza la vista frontal 2D de la góndola, y en el Nivel 1 el volumen libre se obtiene del área frontal libre multiplicada por esos 25 cm. Walmart confirmó que el análisis 2D basta y que la profundidad no es necesaria. También indicó que las góndolas tienen medidas estándar y quedó de enviarlas: si la profundidad estándar no es 25 cm, se cambia esta constante (sigue siendo una sola, global).
* **Fachada visible**: se mide solo lo que la cámara ve de frente. Si el frente de una repisa está lleno, se supone que detrás también hay producto: es lo que ve el cliente, y la cámara no da información del fondo.
* **Sin apilamiento**: no se mide la altura de los productos. Ningún producto se considera apilable, así que el espacio vertical sobre un producto no cuenta como hueco. Es la respuesta del sistema a "La Trampa del Apilamiento".
* **Una sola clase de producto**: basta saber si hay producto o no; no se identifica el SKU ni la categoría.
* **Quiebre por góndola completa** (cambio de alcance del 2026-10-19, indicado por el profesor): el quiebre de stock se determina sobre la góndola completa, no por nivel o repisa. El sistema entrega una sola alerta y un solo porcentaje de espacio libre por góndola. Internamente sigue midiendo repisa por repisa, porque así la medición funciona con la cámara en ángulo (las repisas se ven inclinadas, ítem #22), pero no informa alertas ni porcentajes por repisa. Código, casos de uso y diagramas adaptados en el ítem #40.
* **Qué se mide**: la góndola de venta que ve el cliente. Quedan fuera la bodega de reserva sobre la góndola y las islas centrales del pasillo (excluir la bodega superior está pendiente, #31).

### 3. Acuerdos con el Cliente (Walmart)

Resumen de lo acordado en las reuniones con Walmart Chile (las minutas no se versionan). Las preguntas por confirmar van en el ítem #24 de [PROGRESS.md](PROGRESS.md).

| Tema | Acuerdo | Reunión | Estado |
| :--- | :--- | :--- | :--- |
| Problema | Detectar espacios vacíos (quiebres de stock) en góndolas; la pregunta central es si hay quiebre o no | 2026-09-03, 2026-09-30 | Vigente |
| Alcance | La primera reunión propuso partir, en principio, con góndolas de pan y pollo. El equipo eligió no perecibles porque son los que tienen datasets públicos anotados, y después Walmart recomendó partir por la categoría con más datos | 2026-09-03, 2026-09-16 | Por confirmar (#24) |
| Métrica | Porcentaje de espacio libre de la góndola completa (Nivel 1); como mínimo, alerta por umbral del 30% (Nivel 2). El acta pedía además detalle por repisa: lo reemplaza el cambio del 2026-10-19 | 2026-09-03, 2026-10-19 (profesor) | Vigente |
| Sentido del umbral | El acta lo plantea como "menos del 30% de productos disponibles"; el sistema alerta con **espacio libre >= 30%** del frente (decidido 2026-09-30, #6). El umbral es configurable (`AvailabilityParams.critical_free_fraction`) y los reportes informan el % libre, así que sirven para cualquiera de las dos lecturas | 2026-09-03 | Por confirmar (#24) |
| Nivel de la alerta | **Góndola completa**, no por nivel o repisa (cambio de alcance indicado por el profesor; antes lo elegía el equipo y se mostraba también el detalle por repisa). Implementación: #40 | 2026-09-30, 2026-10-19 (profesor) | Vigente |
| Criterios | Todo criterio del equipo (fachada visible, sin apilamiento, hueco de al menos un ancho de producto) es válido si se justifica ante el negocio | 2026-09-16 | Vigente |
| Imágenes | Las fotos de Walmart son de muchos tipos (frontales, en ángulo, desde arriba) y no vienen recortadas a la góndola. Walmart no comparte fotogramas de sus cámaras (ver "Estrategia de Datos y Evaluación") | 2026-09-16, 2026-10-01 | Vigente |
| Fotos propias | El equipo debe tomar fotos reales de góndolas; sirven para entrenar si se clasifican por ángulo (#32) | 2026-09-03, 2026-09-16 | Pendiente |
| Evaluación de Walmart | Mide IoU contra una anotación hecha a mano y evalúa el criterio de la solución; no exige un resultado perfecto. La nota la ponen los docentes | 2026-09-16 | Vigente |
| Interfaz | Es opcional y debe justificarse: lo primero es que la lógica funcione | 2026-09-16 | Vigente |
| Modelo | Libre; se prefiere uno que el equipo pueda explicar a uno con más rendimiento | 2026-09-03, 2026-09-30 | Vigente |
| Repositorio | En GitHub, público y actualizado de forma continua | 2026-09-03 | Vigente |

---

## 💡 Objetivos y Niveles de Solución

El proyecto contempla una estructura de dos niveles de solución para garantizar la viabilidad técnica:

| Criterio | Solución Óptima (Nivel 1) | MVP Alternativo (Nivel 2) |
| :--- | :--- | :--- |
| **Objetivo Principal** | Medición espacial y volumétrica exacta del espacio libre (profundidad constante de 25 cm) | Alerta macro por umbral binario de stock |
| **Métrica de Salida** | Porcentaje exacto (o cm, con escala) de espacio vacío de la góndola completa | ¿Espacio libre ≥ 30% del frente de la góndola? (Sí / No) |
| **Granularidad** | Góndola completa (desde 2026-10-19). Las repisas, detectadas automáticamente, son solo el método interno de medición | Góndola completa, detectada automáticamente |
| **Complejidad** | Alta (Segmentación espacial + Visión Computacional) | Media (Detección por umbral de píxeles / parches) |

---

## 🛠️ Requerimientos Funcionales (RF)

* **RF01 - Ingesta de Imágenes**: Procesamiento estático de fotogramas en formato imagen, de una cámara de sala o de un lote de fotos (frontales, en ángulo o desde arriba). Tiempo de inferencia objetivo: 2 a 5 segundos por imagen.
* **RF02 - Detección de Espacios Vacíos**: Identificación de regiones sin producto dentro de las regiones de interés (ROI) correspondientes a la góndola, que el sistema segmenta automáticamente.
* **RF03 - Cálculo de Disponibilidad**: Estimación cuantitativa del espacio libre (porcentaje/cm o alerta cuando el espacio libre llega al 30% del frente de la góndola), asumiendo profundidad de góndola constante (25 cm).
* **RF04 - Generación de Alertas**: Emisión de notificaciones prioritarias para el equipo de reposición cuando se detecte un quiebre de stock (una alerta por góndola completa, sin alertas por repisa). Opcional: alerta de cámara defectuosa cuando la imagen tiene colores imposibles.
* **RF05 - Módulo de Reportería**: Exportación de datos analíticos auditados en formatos **Excel (.xlsx)**, **CSV** y **PDF**. Contenido mínimo: % libre de la góndola completa y alerta sí/no. Walmart no pide un formato: los tres son decisión del equipo.
* **RF06 - Evaluación por Lotes**: Ejecutar el sistema sobre un lote de imágenes anotadas a mano y entregar métricas (IoU de detección y acierto de la alerta) sin que las imágenes salgan de la máquina donde corre. Es la forma en que Walmart puede evaluar con su Dataset Oculto.

---

## 👥 Perfiles de Usuario

La interfaz (dashboard y alertas) va después del pipeline: Walmart pidió priorizar que la lógica funcione. Los casos de uso CU00-CU07 están en `Anexos/Diseño/`.

1. **Reponedor de Tienda**: Recibe alertas inmediatas en dispositivos móviles para acudir a los pasillos con quiebre crítico.
2. **Jefe de Salón / Supervisor**: Visualiza dashboards de disponibilidad por pasillo y exporta reportes periódicos de desempeño.
3. **Administrador de Sistema**: Configura planogramas, cámaras y umbrales de alerta, y gestiona usuarios. No define zonas ROI: el sistema segmenta la góndola automáticamente.

---

## 🏗️ Estrategia Algorítmica y Arquitectura

* **Enfoque Híbrido**: Evaluación de modelos de extracción de características (**YOLO26** de Ultralytics, con cabeza sin NMS para góndolas densas) combinados obligatoriamente con **Visión Computacional Clásica** (detección de bordes, transformaciones matriciales y filtros morfológicos) para mantener control matemático sobre el ruido visual. La segmentación automática de la góndola y sus repisas es parte de este pre-procesamiento clásico: se ejecuta sobre la imagen ya corregida (dewarping de lente y luego CLAHE) y antes de la inferencia. Después de la inferencia, los niveles de repisa que se miden combinan las repisas de la segmentación con las filas de productos detectados, como franjas inclinadas: así el cálculo sigue funcionando con la cámara en ángulo (vista oblicua o cámara de sala), donde las repisas se ven inclinadas.
* **Pipeline Modular**: Separación física de los componentes de *Pre-procesamiento*, *Inferencia de Modelo* y *Post-procesamiento*.
* **Código de Producción**: Desarrollo exclusivo en scripts modulares de Python (`.py`), descartando notebooks para la ejecución core.

---

## 📊 Estrategia de Datos y Evaluación

* **Dataset de Entrenamiento**: Curaduría propia mediante fuentes públicas open-source (ej. *SKU-110K*, *Hugging Face Grocery Shelves*, *Kaggle Supermarket Shelves*) con estandarización estricta de coordenadas de anotación (`[x_min, y_min, x_max, y_max]`).
* **Sin imágenes reales de Walmart**: por privacidad, Walmart Chile no puede compartir imágenes de sus cámaras de seguridad (informado el 2026-10-01). Las condiciones de cámara de sala (vista alta y oblicua, lente gran angular/*fisheye*, baja resolución, compresión) se simulan generando imágenes sintéticas desde los datasets públicos, transformando también sus anotaciones (ver [docs/datasets.md](docs/datasets.md)).
* **Prueba Ciega (Dataset Oculto)**: la evaluación contra el **Dataset Oculto** de Walmart Chile (imágenes reales de sala con condiciones complejas) solo es posible si Walmart ejecuta el sistema en sus instalaciones (imagen Docker) y entrega las métricas, sin que las imágenes salgan de la empresa (RF06, CU07). Modalidad por confirmar con Walmart. Sus imágenes no son solo de cámaras de sala: hay fotos frontales, en ángulo y desde arriba.
* **Cómo evalúa Walmart**: IoU contra una anotación hecha a mano, más una evaluación cualitativa del criterio de la solución. Para medirnos igual, el plan de pruebas debe incluir un set propio anotado a mano (#32).
* **Fotos propias**: el equipo debe tomar fotos reales de góndolas (con permiso de la tienda), clasificadas por ángulo (frontal, lateral, desde arriba, gran angular). Sirven para entrenar, como control de vistas en ángulo y como material de demo que no es SKU-110K (#32).

---

## 📁 Estructura del Repositorio

```text
.
├── docs/                   # Documentación de diseño, especificaciones y requisitos del curso (curso.md)
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
python scripts/run_pipeline.py FOTOS_O_CARPETAS... [--device cpu] [--out data/processed/pipeline]
```

`run_pipeline.py` corre el pipeline completo (corrección, segmentación,
YOLO26 y disponibilidad) sobre fotos o carpetas. Por foto escribe la
vista limpia (`<nombre>.jpg`: huecos en rojo, contorno de las repisas
medidas y un cartel con la alerta y el % libre de la góndola completa) y
el resultado completo (`<nombre>.json`), e imprime el % libre, la alerta y
los segundos por etapa. En el JSON, `free_fraction` y `critical` son los
de la góndola completa; `shelves` solo trae la geometría de cada repisa
medida (contorno, huecos y número de productos), sin % ni alerta por
repisa: las repisas son el método para medir, no una salida. Usa por defecto los pesos de
`data/processed/training/yolo26s/weights/best.pt` (no se versionan: se
comparten dentro del equipo, ver `docs/training.md`).

Evaluación por lotes (CU07, RF06): con
`--annotations data/processed/annotations/<dataset>.csv` compara las
detecciones con la anotación hecha a mano por IoU (`--iou`, 0.5 por
defecto) y la alerta con la que da la misma anotación, y escribe
`metrics.csv` (una fila por foto anotada y el total). Las imágenes no
salen de la máquina: solo se escriben métricas.

Las etapas también se prueban por separado:
`python scripts/visualize_segmentation.py` (segmentación, requiere
datasets en `data/raw/`) y los scripts `evaluate_*.py`.

El CI ([.github/workflows/ci.yml](.github/workflows/ci.yml)) corre `pytest` y el `docker build` (con los tests dentro de la imagen) en cada Pull Request hacia `main` y en cada push a `main`; un PR solo se puede mergear con ambos checks en verde.

### Ejecución con Docker

```bash
docker build -t shelfvision-ai .
# run_pipeline.py con las fotos y los pesos montados (sin argumentos, muestra el uso):
docker run --rm -v "$(pwd)/fotos:/app/fotos" -v "$(pwd)/data/processed/training:/app/data/processed/training" \
  -v "$(pwd)/salida:/app/salida" shelfvision-ai python scripts/run_pipeline.py fotos --out salida
# Pruebas dentro del contenedor (tests/ no se copia a la imagen, se monta):
docker run --rm -v "$(pwd)/tests:/app/tests" shelfvision-ai python -m pytest tests/
```

---

## 📅 Planificación y Cronograma (Carta Gantt)

Hitos, plazos y requisitos al día según los mensajes del profesor: [docs/curso.md](docs/curso.md).

* **Fase 1 (Semanas 1 - 4 / 20%)**: Inscripción, reunión con cliente, levantamiento de RF y definición de arquitectura.
* **Fase 2 (Semanas 5 - 16 / 50%)**: Desarrollo modular, integración, pruebas continuas con imágenes sintéticas tipo cámara de sala (y con el Dataset Oculto, si Walmart lo ejecuta en sus instalaciones) y Pre-examen. Informe intermedio de avance y video de demostración (5 a 10 min): 2026-10-21. Evidencias de avance de la Fase 2: a más tardar 2026-10-26. Evaluación 2 (Avance): semana del 2026-10-28, con el 50% de los C.U de la fase resueltos y la demo del Sprint 1. Primer demo operativo ante el cliente: a más tardar 2026-10-31. Entrega final de la Fase 2: semana 15 (fechas por confirmar).
* **Fase 3 (Semanas 17 - 18 / 30%)**: Ajustes finales, manuales de usuario/instalación y Exposición ante Comisión Evaluadora. Fecha: por definir.

---

## 👨‍💻 Equipo de Desarrollo

* **Asignatura**: Proyecto de Título (APT122 / Capstone) - Duoc UC
* **Integrantes**: Mariana Ramirez, Nicko Cortes, Francisco Sandoval
* **Cliente**: Walmart Chile (Área de Inteligencia Artificial)
