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
- **Profundidad constante**: toda góndola se asume de **25 cm** de
  profundidad (valor fijo, dentro del rango real de 20-30 cm). No se
  estima profundidad (sin modelos de profundidad ni visión estéreo): el
  análisis es 2D sobre la vista frontal. Si un cálculo necesita la
  profundidad (volumen del Nivel 1), usa esa única constante global de
  25 cm, nunca un valor por góndola o por cámara.
- **Detector YOLO26** (`ultralytics>=8.4.0`, pesos `yolo26*.pt`). En
  góndolas densas/apiladas inferir con `nms=False` (activa la cabeza sin
  NMS; por defecto Ultralytics aplica NMS igual), `max_det` >= 1000 (el
  default 300 trunca góndolas llenas) e `imgsz=1280`.
- **Pipeline modular**: `preprocessing -> models -> postprocessing ->
  reporting`. Cada etapa vive en su propio paquete y no debe importar
  directamente detalles internos de otra etapa; se comunican mediante
  estructuras de datos simples (arrays, dicts, dataclasses).
- **Umbral de disponibilidad crítica**: `< 30%` de espacio disponible en
  la góndola dispara alerta (MVP Nivel 2, ver README).

## Estructura relevante

```
src/preprocessing/   # Filtros CLAHE, dewarping, segmentación automática y recorte de ROI
src/models/           # Inferencia YOLO26 (Ultralytics)
src/postprocessing/    # Cálculo de disponibilidad y umbral <30%
src/reporting/         # Reportes en Excel, CSV y PDF
src/evaluation/        # Métricas de evaluación (no es etapa del pipeline)
scripts/               # CLI de ejecución del pipeline
tests/                 # Pruebas unitarias con pytest
data/raw/              # Imágenes de entrada (no versionadas)
data/processed/        # Salidas intermedias/procesadas (no versionadas)
```

## Comandos frecuentes

```bash
pytest tests/
python scripts/run_pipeline.py
python scripts/visualize_segmentation.py   # revisar la segmentación a ojo
```

## Notas

- La carpeta `Fase 1/` contiene entregables académicos ya evaluados y no
  debe modificarse.
- Los pesos de modelos (`*.pt`, `*.onnx`) y las imágenes de datos no se
  versionan (ver `.gitignore`).

## Continuidad entre sesiones / chats

Este repositorio externaliza su estado a archivos, no a la memoria de una
conversación. Al empezar una sesión o chat nuevo (por compactación de
contexto o porque se abrió aparte), leer primero, en este orden:

1. `CLAUDE.md` (este archivo) - reglas de código y estructura.
2. `PROGRESS.md` - qué está hecho y qué es lo pendiente priorizado.
3. `docs/datasets.md` - estado y ubicación de los datasets descargados.

Con eso se recupera casi todo el contexto relevante sin necesitar el
historial de la conversación anterior.

Buen momento para compactar/cambiar de chat: justo después de cerrar un
hito (no a mitad de una tarea), especialmente antes de empezar un bloque
de trabajo grande y autocontenido (ej. implementar un módulo nuevo con
sus tests). Señal adicional: cuando las respuestas se sientan más lentas
o se repita contexto que ya debería estar resuelto.

Al terminar una tarea de esta bitácora, actualizar `PROGRESS.md` (marcar
lo hecho, agregar lo nuevo pendiente) antes de cerrar la sesión.

## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

Rules:
- For codebase questions, first run `graphify query "<question>"` when graphify-out/graph.json exists. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).
