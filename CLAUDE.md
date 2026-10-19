# ShelfVision AI - Walmart Chile

Sistema de auditoría automatizada de disponibilidad de stock en góndolas de
alimentos no perecibles, desarrollado para el Proyecto de Título (APT122 /
Capstone) de Duoc UC en colaboración con Walmart Chile.

## Reglas de código

- **Solo scripts `.py`**: no se usan notebooks (`.ipynb`) para el código
  core del pipeline. Notebooks solo se permiten como exploración puntual
  fuera de `src/`, nunca versionados.
- **Bounding boxes estandarizados**: toda coordenada de detección o
  anotación se representa como `[x_min, y_min, x_max, y_max]` en píxeles
  absolutos de la imagen original.
- **Enfoque híbrido obligatorio**: `src/preprocessing/` (OpenCV) siempre
  precede a `src/models/` (YOLO26), en este orden: corrección de imagen
  (dewarping y luego CLAHE, `correct_image()`) -> segmentación automática
  de góndola/repisas ->
  recorte de ROI. La segmentación trabaja sobre la imagen ya corregida.
  No se reemplaza el pre-procesamiento clásico por el modelo de inferencia.
- **ROI automática**: el sistema segmenta la góndola y sus repisas en
  `src/preprocessing/`, antes de YOLO26. Ningún usuario dibuja ni configura
  ROI por cámara, así que el código no debe depender de una ROI cargada de
  configuración. Flujo: `correct_image()` -> `segment_gondola()` ->
  `crop_roi(imagen_corregida, segmentacion.roi)`. Las detecciones vuelven
  a la imagen original con `RoiCrop.to_original()` y luego
  `CorrectedImage.to_original()`.
- **Niveles de repisa híbridos** (decidido 2026-10-01, ítem #22): los
  niveles que mide la disponibilidad salen de `shelf_levels()`
  (`src/postprocessing/shelf_levels.py`), que combina las filas de
  productos detectados (sus bases marcan la repisa aunque esté inclinada)
  con `segmentacion.shelf_lines` (aportan las repisas vacías), como
  franjas inclinadas. Flujo: detecciones en coordenadas de la imagen
  corregida (`RoiCrop.to_original()`) -> `shelf_levels(cajas,
  [astuple(l) for l in segmentacion.shelf_lines], segmentacion.roi)` ->
  `compute_availability(cajas, niveles)`. `GondolaSegmentation.shelves`
  (rectángulos horizontales) queda para recortar la ROI, no para medir:
  con la cámara en ángulo mezcla repisas vecinas.
- **Profundidad constante**: toda góndola se asume de **25 cm** de
  profundidad (valor fijo, dentro del rango real de 20-30 cm). No se
  estima profundidad (sin modelos de profundidad ni visión estéreo): el
  análisis es 2D sobre la vista frontal. Si un cálculo necesita la
  profundidad (volumen del Nivel 1), usa esa única constante global de
  25 cm, nunca un valor por góndola o por cámara.
- **Detector YOLO26** (`ultralytics>=8.4.0`, pesos `yolo26*.pt`). En
  góndolas densas/apiladas inferir con `nms=False` (activa la cabeza sin
  NMS; por defecto Ultralytics aplica NMS igual), `max_det` >= 1000 (el
  default 300 trunca góndolas llenas) e `imgsz=1280`. Lo mismo al entrenar
  y validar (`nms=False`, `max_det=1000`): si no, Ultralytics mide la
  cabeza con NMS y elige `best.pt` con otro modelo. La inferencia pasa por
  `ProductDetector` (`src/models/detector.py`), que ya fija estos valores;
  el entrenamiento, por `scripts/train_detector.py` (ver
  `docs/training.md`).
- **Pipeline modular**: `preprocessing -> models -> postprocessing ->
  reporting`. Cada etapa vive en su propio paquete y no debe importar
  directamente detalles internos de otra etapa; se comunican mediante
  estructuras de datos simples (arrays, dicts, dataclasses).
- **Umbral de quiebre de stock**: se alerta cuando el espacio **libre** es
  `>= 30%` del frente de la góndola (disponibilidad `<= 70%`; MVP Nivel
  2, ver README). El espacio libre se mide como cobertura a lo largo de
  cada repisa (en X, sobre las franjas de `shelf_levels()`): huecos de
  al menos un ancho de producto, sin medir la altura de los productos,
  en la góndola acotada a los productos detectados
  (`src/postprocessing/availability.py`, decidido 2026-09-30).
- **Quiebre por góndola completa** (cambio de alcance del 2026-10-19,
  indicado por el profesor): la alerta y el % de espacio libre que el
  sistema **informa** (JSON, vista, reportes, alertas, app web) son solo
  los de la góndola completa. Las repisas de `shelf_levels()` siguen
  siendo el método interno para medir (sumar la cobertura a lo largo de
  cada repisa), pero no se informa alerta ni porcentaje por repisa. Ver
  ítem #40 de `PROGRESS.md`.
- **Licencias de datos**: SKU-110K es solo para uso académico y no
  comercial, y su licencia prohíbe distribuir, mostrar a terceros o
  **modificar** sus fotos (crear obras derivadas). Se usa para entrenar
  y evaluar (confirmado por el profesor el 2026-10-19), nunca para
  generar imágenes sintéticas (vistas en ángulo,
  distorsión de lente) ni para demos ante Walmart u otros externos: para
  eso, datasets que lo permitan (Kaggle supermarket-shelves CC0, SHARD y
  Roboflow CC BY 4.0). Ver `src/datasets/sources.py` y
  `docs/datasets.md`.

## Estructura relevante

```
src/preprocessing/   # Filtros CLAHE, dewarping, segmentación automática y recorte de ROI
src/models/           # Inferencia YOLO26 (Ultralytics)
src/postprocessing/    # Cálculo de disponibilidad y alerta (libre >= 30%)
src/reporting/         # Vista anotada (annotate.py) y reportes en Excel, CSV y PDF
src/evaluation/        # Métricas de evaluación, ej. IoU de detección (no es etapa del pipeline)
src/pipeline.py        # Encadena las etapas para una foto (run_image); no es una etapa
scripts/               # CLI de ejecución del pipeline (run_pipeline.py) y de evaluación
tests/                 # Pruebas unitarias con pytest
data/raw/              # Imágenes de entrada (no versionadas)
data/processed/        # Salidas intermedias/procesadas (no versionadas)
```

## Comandos frecuentes

```bash
pytest tests/
python scripts/run_pipeline.py FOTOS_O_CARPETAS... [--annotations CSV]   # vista limpia + JSON (+ métricas IoU)
python scripts/visualize_segmentation.py   # revisar la segmentación a ojo
```

## Notas

- La carpeta `Fase 1/` contiene entregables académicos ya evaluados y no
  debe modificarse.
- Los pesos de modelos (`*.pt`, `*.onnx`) y las imágenes de datos no se
  versionan (ver `.gitignore`).

## Trabajo en equipo (flujo obligatorio)

Tres integrantes trabajan en paralelo, cada uno con su propio Claude
Code. Estas reglas aplican a todas las sesiones, para no pisarse commits
ni trabajo:

1. **Antes de empezar**: `git switch main && git pull`, y regenerar el
   grafo (`graphify update .`, ver sección graphify). Si la tarea depende
   de un PR aún no mergeado, partir desde esa rama en vez de `main`.
2. **Tomar un ítem de `PROGRESS.md`** agregando `(dueño: <nombre>)` al
   ítem, antes de escribir código. No tomar ítems que ya tienen dueño. Si
   la tarea no está en el backlog, agregarla primero como ítem nuevo.
3. **Una rama por ítem**: `feat/<tema>`, `fix/<tema>`, `docs/<tema>`,
   `build/<tema>` o `chore/<tema>`. **Nunca** commit ni push directo a
   `main`.
4. **Commits solo cuando la persona lo pide**, separados por tema y en
   estilo Conventional Commits en inglés (`feat: ...`, `fix: ...`,
   `docs: ...`). Antes de cada commit, `pytest tests/` debe pasar; si se
   tocó `Dockerfile` o `requirements.txt`, también `docker build`.
5. **Nunca reescribir historia publicada**: nada de `git push --force`,
   `git reset` ni `rebase` sobre ramas ya subidas. Para deshacer algo
   publicado se usa `git revert`.
6. **Todo entra a `main` por Pull Request** (`gh pr create`), con qué
   cambia y cómo se verificó. Requiere revisión de otro integrante y CI
   en verde. Preferir PR independientes contra `main`. Si hay PR
   encadenados (uno con base en la rama de otro), se mergean de a uno y
   en orden, con "Create a merge commit" (no squash), y **después de
   cada merge se borra la rama mergeada** ("Delete branch"): solo así
   GitHub cambia la base del PR siguiente a `main`. Antes de mergear un
   PR, confirmar que su base diga `main`; si no, el cambio queda en otra
   rama y no llega a `main`.
7. **Al terminar el ítem**, marcarlo `[x]` en `PROGRESS.md` dentro del
   mismo PR, editando solo las líneas de ese ítem (es el archivo que más
   conflictos genera).
8. **Configuración personal** en `CLAUDE.local.md` y
   `.claude/settings.local.json` (no se versionan). La compartida es este
   archivo y `.claude/settings.json`.
9. **Plugins compartidos** (`.claude/settings.json`): `yolo@ultralytics`
   y `superpowers`. Si una skill ofrece mergear localmente a `main` (ej.
   `finishing-a-development-branch` de superpowers), elegir siempre la
   opción de Pull Request: estas reglas tienen prioridad.

### `PROGRESS.md` guía el trabajo de cada integrante

Cada sesión de Claude trabaja sobre un ítem de `PROGRESS.md`, para que
cada integrante sepa siempre qué le toca y no se pierda:

- **Quién es la persona**: la línea `Integrante: <nombre>` de
  `CLAUDE.local.md`. Si falta, preguntarle el nombre y agregarla.
- **Al empezar la sesión**, después de leer `PROGRESS.md`, decirle a la
  persona en qué está: su ítem en curso (con `(dueño: <nombre>)` y sin
  `[x]`), o, si no tiene ninguno, proponerle el primer ítem sin dueño de
  "Pendientes (priorizados)" (van en orden de prioridad). Se toma solo
  cuando la persona confirma.
- **Nada fuera del backlog**: si la persona pide algo que no es un ítem,
  agregarlo primero como ítem nuevo (número siguiente al mayor que
  exista), con su dueño, y recién ahí escribir código.
- **Si el ítem queda a medias** al cerrar la sesión, anotar en el ítem
  qué está hecho y qué falta, para retomarlo (o que lo retome otro).
- **Al terminarlo** (regla 7), proponer el siguiente ítem sin dueño.

Setup de un entorno nuevo: ver "Configuración de un entorno nuevo" en el
README.

## Continuidad entre sesiones / chats

Este repositorio externaliza su estado a archivos, no a la memoria de una
conversación. Al empezar una sesión o chat nuevo (por compactación de
contexto o porque se abrió aparte), leer primero, en este orden:

1. `CLAUDE.md` (este archivo) - reglas de código y estructura.
2. `PROGRESS.md` - qué está hecho y qué es lo pendiente priorizado.
3. `docs/datasets.md` - estado y ubicación de los datasets descargados.
4. `docs/curso.md` - hitos, plazos y requisitos del curso según los
   mensajes del profesor.
5. `minutas-walmart/INDEX.md`, si existe (no se versiona, ver "Minutas
   de reuniones con Walmart").

Con eso se recupera casi todo el contexto relevante sin necesitar el
historial de la conversación anterior.

Buen momento para compactar/cambiar de chat: justo después de cerrar un
hito (no a mitad de una tarea), especialmente antes de empezar un bloque
de trabajo grande y autocontenido (ej. implementar un módulo nuevo con
sus tests). Señal adicional: cuando las respuestas se sientan más lentas
o se repita contexto que ya debería estar resuelto.

Al terminar una tarea de esta bitácora, actualizar `PROGRESS.md` (marcar
lo hecho, agregar lo nuevo pendiente) antes de cerrar la sesión.

## Mensajes del profesor (`docs/curso.md`)

`docs/curso.md` reúne lo que pide el curso: próximos hitos con fecha,
requisitos vigentes, lo que el profesor anunció que enviará, preguntas
abiertas y un registro por semana. Es la fuente de los plazos
académicos; `README.md` y `PROGRESS.md` copian de ahí las fechas que
les tocan.

- Cuando alguien pega un mensaje del profesor (o dice "mensaje del
  profesor"), usar la skill `/mensaje-profesor`
  (`.claude/skills/mensaje-profesor/SKILL.md`): normaliza el mensaje en
  `docs/curso.md` y lleva las fechas a `README.md` y `PROGRESS.md`.
- Registrar un mensaje no necesita ítem en `PROGRESS.md`, pero sí rama
  propia (`docs/curso-<YYYY-MM-DD>`) y PR, como todo cambio.
- Fechas en formato YYYY-MM-DD; nunca inventarlas: lo que no se sabe
  queda "Por definir" y va a "Preguntas abiertas para el profesor".
- El repositorio es público: los enlaces que comparte el profesor
  (Drive, formularios) no se escriben en archivos versionados. En su
  lugar se anota la fecha del mensaje que trae el enlace, para buscarlo
  ahí; cada integrante puede guardarlo en su `CLAUDE.local.md`.
- Antes de proponer el siguiente ítem del backlog, mirar "Próximos
  hitos": un requisito con fecha cercana puede cambiar la prioridad.

## Minutas de reuniones con Walmart (`minutas-walmart/`, no versionada)

Las minutas de las reuniones con Walmart son **confidenciales** (nombres
de personas, transcripciones de reuniones privadas) y el repositorio es
público: **nunca se versionan ni se suben a servicios externos** (ni
`git add -f`, ni Artifacts, gists o conectores). `minutas-walmart/` está
en `.gitignore`. Se comparten en una carpeta privada de Google Drive del
equipo; el enlace no va en archivos versionados: cada integrante lo
guarda en su `CLAUDE.local.md`.

- **Instalar**: descargar los `.md` de la carpeta de Drive a
  `minutas-walmart/` en la raíz del repo (`INDEX.md` y una minuta por
  reunión, `AAAA-MM-DD_reunion-N.md`). Volver a descargarlos cuando
  alguien avise de una minuta nueva.
- **Usar**: antes de responder sobre requisitos o acuerdos con Walmart,
  buscar con Grep en `minutas-walmart/*.md` (por `temas:` del encabezado
  o por palabra clave). graphify no indexa la carpeta (está ignorada).
  Si no existe en el PC, decir que faltan y usar el resumen público de
  "Acuerdos con el Cliente (Walmart)" del README.
- **Nueva reunión**: la minuta se escribe con las mismas secciones
  (encabezado YAML con `temas:`, Resumen, Decisiones y acuerdos,
  Requisitos o restricciones de Walmart, Tareas, Preguntas abiertas,
  Transcripción limpia completa), se sube a la carpeta de Drive y se
  actualiza `INDEX.md`. Lo que cambie requisitos va resumido, sin citas
  ni nombres, a la tabla de acuerdos del README, por rama y PR.

## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

**El grafo no se versiona** (`graphify-out/` está en `.gitignore`): cada
integrante lo regenera en su máquina. Requiere graphify instalado fuera
del venv (`uv tool install graphifyy==0.9.70`, ver README): los hooks de
`.claude/settings.json` lo llaman sin activar el venv, y sin él fallan en
cada búsqueda o lectura de Claude.
Regenerarlo con `graphify update .` al clonar, después de cada
`git pull` o cambio de rama, y después de modificar código. Si
`graphify-out/graph.json` no existe, crearlo con `graphify update .`
antes de usar las reglas de abajo.

Rules:
- For codebase questions, first run `graphify query "<question>"` when graphify-out/graph.json exists. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).
