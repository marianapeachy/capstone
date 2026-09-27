# Bitácora de Sprint 1 - ShelfVision AI

## Estado

Estructura inicial del repositorio creada (directorios `src/`, `tests/`,
`docs/`, `data/`, `scripts/`, más `.gitignore`, `requirements.txt`,
`Dockerfile`, `CLAUDE.md`).

## Pendientes (priorizados)

1. [x] Implementar `src/preprocessing/roi_filter.py`: recortador de
       región de interés (ROI) sobre la góndola detectada, incluyendo
       normalización de coordenadas `[x_min, y_min, x_max, y_max]`.
       API: `normalize_roi()` (ordena, redondea hacia afuera, recorta a
       la imagen), `crop_roi()` -> `RoiCrop` (copia del recorte + ROI
       usada) y `RoiCrop.to_original()` para devolver detecciones del
       recorte a coordenadas de la imagen original. ROI parcialmente
       fuera se recorta; totalmente fuera, imagen None o vacía ->
       `ValueError`. La ROI llega como parámetro; la entregará la
       segmentación automática de la góndola (ítem 4).
2. [x] Implementar pruebas unitarias en `tests/test_preprocessing.py`
       para `roi_filter.py` (casos: ROI dentro de límites, ROI fuera de
       límites, imagen vacía/None) — 16 tests, suite completa 24/24 OK.
3. [ ] Implementar filtros CLAHE y dewarping en `src/preprocessing/`.
4. [ ] Implementar la segmentación automática de la góndola y sus
       repisas en `src/preprocessing/` (cambio de alcance 2026-09-27:
       ningún usuario define la ROI). Visión clásica, antes de YOLO26.
       Debe entregar la ROI de la góndola (entrada de `crop_roi()`) y,
       para el Nivel 1, los límites de cada repisa. Corre después de
       CLAHE/dewarping, sobre la imagen corregida (decidido 2026-09-27:
       con lente fisheye las líneas de repisa se ven curvas). Ningún dataset descargado anota
       góndolas ni repisas (solo productos, espacios vacíos y precios):
       para medirla hay que etiquetar a mano un set chico de validación.
       Incluir un script visor que dibuje la segmentación sobre imágenes
       de los datasets para revisarla a ojo.
5. [ ] Integrar inferencia YOLO26 en `src/models/` (se decidió YOLO26
       sobre YOLOv8/YOLO11 por su cabeza sin NMS y mejor manejo de
       objetos chicos, clave en productos apilados). Validado en local:
       `ultralytics` 8.4.164 + `yolo26n.pt` corre sobre SKU-110K y se
       encadena con `crop_roi()`/`to_original()`; `tests/test_models.py`
       fija el contrato (versión >= 8.4.0, `nms=False` activa el modo
       end-to-end y respeta `max_det`). Pendiente: fine-tuning sobre
       SKU-110K (los pesos COCO no tienen clase "producto") y comparar
       `yolo26s` vs la variante `yolo26-p2.yaml` (cabeza extra para
       objetos chicos) en la validación de SKU-110K.
6. [ ] Implementar cálculo de disponibilidad y evaluación de umbral
       `<30%` en `src/postprocessing/`. La profundidad de góndola es
       una constante global fija de 25 cm (decidido 2026-09-27, ver
       CLAUDE.md) y no se estima: el cálculo es 2D sobre la vista
       frontal, y el volumen del Nivel 1 = área frontal libre x 25 cm.
7. [ ] Implementar generación de reportes (Excel, CSV, PDF) en
       `src/reporting/`.
8. [ ] Implementar `scripts/run_pipeline.py` como CLI que orquesta el
       pipeline completo.
9. [ ] Documentar especificaciones técnicas y diagramas en `docs/`.
10. [x] Descargar datasets candidatos (ver `docs/datasets.md`):
       SKU-110K, grocery-shelves (UniDataPro), supermarket-shelves
       (Kaggle), Out Of Stock detection y Empty Shelf Detector
       (Roboflow) — los 5 ya están en `data/raw/`.
11. [x] Escribir conversores de anotaciones a nuestro estándar
       `[x_min, y_min, x_max, y_max]`: lógica pura en
       `src/datasets/converters.py` (probada en
       `tests/test_dataset_converters.py`, 8/8 tests OK) + CLI
       `scripts/prepare_datasets.py` que recorre `data/raw/` y escribe
       `data/processed/annotations/<dataset>.csv` +
       `all_annotations.csv` (1,760,633 anotaciones combinadas de los 5
       datasets). No versionado (`data/processed/*` en `.gitignore`).
12. [ ] Falta script de *descarga* reproducible (hoy la descarga se
       hizo manualmente); ver Notas.

## Notas

- Cambio de alcance (2026-09-27): la ROI de la góndola la segmenta el
  sistema automáticamente (antes el Administrador la definía a mano) y la
  profundidad de góndola es constante, de 20-30 cm. Ya están actualizados
  README, CLAUDE.md, `docs/datasets.md` y `roi_filter.py`. Siguen
  desactualizados estos anexos de diseño, que no se modificaron:
  `Anexos/Diseño/Mockups/Mockup Admin-1.jpg` (pantalla "Editor de Región de Interés (ROI)" con el botón
  "Guardar Máscara ROI"), `Mockup Admin-4.jpg` (log "Actualizó máscara
  ROI") y `Plantilla de C.U 01.docx` (menciona YOLOv8 en vez de YOLO26).
  Actualizarlos quedó postergado para más adelante (decidido 2026-09-27).
- Riesgos de Docker resueltos y verificados con `docker build` real
  (2026-09-27, Docker Desktop 4.92): imagen de 2.49 GB, 27/27 tests OK
  dentro del contenedor. El build real destapó un cuarto problema: el pip
  23.0.1 de la imagen base rechazaba wheels del índice de PyTorch, así que
  el Dockerfile ahora actualiza pip antes de instalar. Detalle de los
  otros tres:
  - OpenCV: se usa solo `opencv-python>=4.8,<5` (ultralytics lo exige; el
    `-headless` duplicaba `cv2`). Tope `<5` porque pip ya resolvía
    OpenCV 5.0 sin validar.
  - Base fijada a `python:3.10-slim-trixie` (Debian 13): `libgl1-mesa-glx`
    y `libglib2.0-0` no existen ahí. Paquetes de sistema derivados de las
    dependencias ELF reales del wheel de OpenCV 4.14 (`readelf` en WSL) y
    verificados en el archivo de Debian trixie.
  - PyTorch CPU desde `download.pytorch.org/whl/cpu`: desde PyPI en Linux
    arrastraba CUDA 13 + cuDNN (varios GB). Resolución final verificada
    con `uv pip compile` para Linux/py3.10: `torch 2.14.0+cpu`,
    `ultralytics 8.4.164`, `opencv-python 4.14.0.94`, sin paquetes CUDA.
- Python 3.10 llega a fin de soporte en octubre de 2026 (el entorno local
  usa 3.14). Pendiente decidir si se sube la imagen a 3.12+.
- La carpeta `Fase 1/` (entregables de la Fase 1 académica) no se toca.
- README.md se actualizará incrementalmente a medida que se implementen
  los módulos.
- Los 2 datasets de Roboflow se descargaron manualmente (export ZIP en
  formato COCO) porque la descarga programática requiere API key de
  Roboflow, que el equipo no tenía configurada. Pendiente decidir si se
  gestiona una API key para automatizar esto en `scripts/prepare_datasets.py`
  (hoy asume que los datos ya están en `data/raw/`).
