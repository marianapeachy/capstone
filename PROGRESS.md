# Bitácora de Sprint 1 - ShelfVision AI

Cada ítem tiene un número fijo (**#N**) que no cambia al reordenar: los
PR y otros documentos lo citan. Para tomar un ítem, agregar
`(dueño: <nombre>)` antes de empezar; al terminarlo, marcarlo `[x]` y
moverlo a "Hecho" en el mismo PR, editando solo las líneas de ese ítem
(ver "Trabajo en equipo" en `CLAUDE.md`).

## Estado actual

| Etapa | Estado | Ítems |
| --- | --- | --- |
| `src/preprocessing/` | Hecho: corrección de imagen, segmentación de góndola y recorte de ROI | #1, #2, #3, #4 |
| `src/models/` | En curso: YOLO26 integrado y validado; falta el fine-tuning | #5 |
| `src/postprocessing/` | Pendiente | #6 |
| `src/reporting/` | Pendiente | #7 |
| `scripts/run_pipeline.py` | Pendiente | #8 |
| Datasets | 5 descargados y convertidos al estándar, con descarga reproducible | #10, #11, #12 |
| CI | Hecho: pytest + `docker build` en cada PR, `main` protegida | #13 |

## Plan de trabajo por fases (2026-09-27)

1. [x] (dueño: Francisco) Terreno común: subir las ramas y abrir los PR
       #3, #4 y #5 (encadenados); flujo de trabajo en equipo en
       `CLAUDE.md`; `graphify-out/` fuera de git y regenerado
       localmente; setup de entorno nuevo en el README.
2. [x] (dueño: Mariana) CI con GitHub Actions (pytest + `docker build`)
       y protección de `main` (PR + revisión + CI en verde). Ítem #13.
3. [x] (dueño: Francisco) Buscar datasets que simulen cámaras de
       seguridad de sala. Candidatos registrados en `docs/datasets.md`
       (sección "Candidatos tipo cámara de sala"); descargarlos y
       evaluarlos sigue en el ítem #14.
4. [x] (dueño: Francisco) Recomendar skills de Claude Code aplicables
       al proyecto (`/skill-finder`). Recomendadas: plugins
       `yolo@ultralytics` (entrenamiento, tuning e inferencia de YOLO26)
       y `superpowers@superpowers-marketplace` (TDD, depuración
       sistemática, verificación antes de cerrar), más las ya incluidas
       `/code-review`, `/security-review`, `/simplify`, `xlsx`, `pdf` y
       `dataviz` (reportes, ítem #7). Los dos plugins quedan
       compartidos en `.claude/settings.json` (`extraKnownMarketplaces`
       + `enabledPlugins`): Claude Code los ofrece instalar al abrir el
       proyecto. Ojo: la skill
       `finishing-a-development-branch` de superpowers ofrece mergear
       localmente a `main`; elegir siempre la opción de Pull Request.
5. [ ] Resolver limitaciones de la segmentación. Ítem #15.

## Pendientes (priorizados)

- [ ] **#5** Integrar inferencia YOLO26 en `src/models/` (se decidió
      YOLO26 sobre YOLOv8/YOLO11 por su cabeza sin NMS y mejor manejo de
      objetos chicos, clave en productos apilados). Validado en local:
      `ultralytics` 8.4.164 + `yolo26n.pt` corre sobre SKU-110K y se
      encadena con `crop_roi()`/`to_original()`; `tests/test_models.py`
      fija el contrato (versión >= 8.4.0, `nms=False` activa el modo
      end-to-end y respeta `max_det`). Pendiente: fine-tuning sobre
      SKU-110K (los pesos COCO no tienen clase "producto") y comparar
      `yolo26s` vs la variante `yolo26-p2.yaml` (cabeza extra para
      objetos chicos) en la validación de SKU-110K.
- [ ] **#6** Implementar cálculo de disponibilidad y evaluación de umbral
      `<30%` en `src/postprocessing/`. La profundidad de góndola es una
      constante global fija de 25 cm (decidido 2026-09-27, ver
      CLAUDE.md) y no se estima: el cálculo es 2D sobre la vista
      frontal, y el volumen del Nivel 1 = área frontal libre x 25 cm.
- [ ] **#7** Implementar generación de reportes (Excel, CSV, PDF) en
      `src/reporting/`.
- [ ] **#8** Implementar `scripts/run_pipeline.py` como CLI que orquesta
      el pipeline completo.
- [ ] **#9** Documentar especificaciones técnicas y diagramas en `docs/`.
- [ ] **#14** Datasets con imágenes tipo cámara de seguridad (vista alta,
      oblicua, gran angular/fisheye, pasillo completo) para validar
      dewarping y segmentación en condiciones parecidas a Walmart.
      Candidatos en `docs/datasets.md` ("Candidatos tipo cámara de
      sala"): ninguno público combina cámara de sala real con anotación
      de productos. Siguientes pasos: (1) descargar SHARD; (2) pedir
      MMPTrack (entorno *retail*, cámaras fijas calibradas); (3) generar
      imágenes "tipo CCTV" sintéticas a partir de SKU-110K y SHARD
      (distorsión fisheye con `LensCalibration`, homografía oblicua,
      baja resolución, compresión JPEG, ruido), transformando también
      sus anotaciones. Pedir también a Walmart una muestra de fotogramas
      reales.
- [ ] **#15** Limitaciones de la segmentación (ítem #4) y cómo atacarlas:
      - Diagonales falsas (cadenas que saltan entre repisas): exigir
        soporte de borde a lo largo de toda la recta ajustada, no solo
        en los centros de franja, y que la pendiente de cada repisa sea
        coherente con las vecinas (por perspectiva, varía suavemente
        con la altura).
      - Líneas extra en cajas apiladas: una repisa real tiene una franja
        delgada y uniforme (con etiquetas de precio) entre dos bordes
        cercanos; verificar ese patrón. Además, cuando exista el
        detector, refinar los niveles en `src/postprocessing/`: una
        línea que cruza por el medio de productos detectados no es
        repisa.
      - ROI casi igual a la imagen en primeros planos: esperable; se
        valida con imágenes de cámaras de sala (ítem #14).
      - Medición real: SHARD anota la altura de cada repisa en ~22K
        fotos (CC BY 4.0) y puede reemplazar buena parte del etiquetado
        a mano. Para lo que no cubre (repisas inclinadas, contorno de
        la góndola), set chico etiquetado a mano (polilíneas, ej. en
        CVAT o Label Studio).

## Hecho

- [x] **#1** (dueño: Francisco) Implementar
      `src/preprocessing/roi_filter.py`: recortador de región de interés
      (ROI) sobre la góndola detectada, incluyendo normalización de
      coordenadas `[x_min, y_min, x_max, y_max]`. API: `normalize_roi()`
      (ordena, redondea hacia afuera, recorta a la imagen), `crop_roi()`
      -> `RoiCrop` (copia del recorte + ROI usada) y
      `RoiCrop.to_original()` para devolver detecciones del recorte a
      coordenadas de la imagen original. ROI parcialmente fuera se
      recorta; totalmente fuera, imagen None o vacía -> `ValueError`. La
      ROI llega como parámetro; la entrega la segmentación automática de
      la góndola (ítem #4).
- [x] **#2** (dueño: Francisco) Implementar pruebas unitarias en
      `tests/test_preprocessing.py` para `roi_filter.py` (casos: ROI
      dentro de límites, ROI fuera de límites, imagen vacía/None) — 16
      tests, suite completa 24/24 OK.
- [x] **#3** (dueño: Francisco) Implementar filtros CLAHE y dewarping en
      `src/preprocessing/`: `image_correction.py` con `correct_image()`
      (dewarping y luego CLAHE) -> `CorrectedImage` (imagen +
      calibración usada, con `to_original()`/`to_original_points()` para
      devolver detecciones a coordenadas de la imagen original).
      `dewarp()` corrige solo la distorsión de lente (modelo pinhole o
      fisheye de OpenCV) y conserva el tamaño y la matriz de cámara.
      `apply_clahe()` ecualiza solo la luminancia (Lab) para no alterar
      colores. `LensCalibration.approximate(k1)` da una calibración
      genérica mientras no existan las reales. 21 tests en
      `tests/test_image_correction.py` (entre ellos, una repisa curvada
      con distorsión sintética que vuelve a quedar recta). Validaciones
      de imagen compartidas en `_validation.py`. Pendiente: pedir a
      Walmart el modelo y la calibración de sus cámaras (o fotos de un
      tablero de ajedrez para calibrar). Los datasets públicos no traen
      distorsión de lente: con ellos se usa solo CLAHE (sin
      calibración).
- [x] **#4** (dueño: Francisco) Implementar la segmentación automática
      de la góndola y sus repisas en `src/preprocessing/` (cambio de
      alcance 2026-09-27: ningún usuario define la ROI). Visión clásica,
      antes de YOLO26. Hecho: `gondola_segmentation.py` con
      `segment_gondola()` -> `GondolaSegmentation` (ROI, `ShelfLine` por
      repisa, bbox por nivel y `found`). Método: saltos del brillo
      promedio por fila en franjas verticales, enlazados entre franjas
      (permite repisas inclinadas por perspectiva). Se descartó Canny +
      Hough: el texto de las etiquetas dominaba y cada fila de cajas
      salía como repisa. Sin repisas detectadas -> imagen completa con
      `found=False` (contingencia de análisis global). Visor:
      `scripts/visualize_segmentation.py` (láminas + `metrics.csv` en
      `data/processed/segmentation_preview/`). Métricas aproximadas en
      `src/evaluation/segmentation_proxy.py`, que usan las anotaciones
      existentes como evidencia indirecta. Línea base (100 imágenes por
      dataset): 99-100% de las anotaciones (incluidos los espacios
      vacíos) quedan dentro de la ROI; en SKU-110K la ROI ocupa el 91%
      del área, el 52% de los productos queda apoyado sobre una repisa
      detectada y el 76% de las repisas detectadas tiene productos
      encima. La métrica de repisas con productos subestima: el borde
      superior de la góndola y las repisas vacías son líneas correctas
      sin productos encima. Limitaciones conocidas y cómo atacarlas: ver
      ítem #15. Pendientes: set de validación con góndolas/repisas, y
      evaluarlo con imágenes reales de Walmart.
      Especificación original: debe entregar la ROI de la góndola
      (entrada de `crop_roi()`) y, para el Nivel 1, los límites de cada
      repisa. Corre después de `correct_image()`, sobre la imagen
      corregida (decidido 2026-09-27: con lente fisheye las líneas de
      repisa se ven curvas). La corrección de perspectiva por ángulo
      oblicuo (llevar el contorno de la góndola a un rectángulo) va
      aquí, porque necesita ese contorno; `image_correction.py` no la
      hace.
- [x] **#10** (dueño: Francisco) Descargar datasets candidatos (ver
      `docs/datasets.md`): SKU-110K, grocery-shelves (UniDataPro),
      supermarket-shelves (Kaggle), Out Of Stock detection y Empty Shelf
      Detector (Roboflow) — los 5 ya están en `data/raw/`.
- [x] **#11** (dueño: Francisco) Escribir conversores de anotaciones a
      nuestro estándar `[x_min, y_min, x_max, y_max]`: lógica pura en
      `src/datasets/converters.py` (probada en
      `tests/test_dataset_converters.py`, 8/8 tests OK) + CLI
      `scripts/prepare_datasets.py` que recorre `data/raw/` y escribe
      `data/processed/annotations/<dataset>.csv` + `all_annotations.csv`
      (1,760,633 anotaciones combinadas de los 5 datasets). No
      versionado (`data/processed/*` en `.gitignore`).
- [x] **#12** (dueño: Francisco) Script de descarga reproducible:
      `scripts/download_datasets.py` (`--list`, `--check`, `--dataset`,
      `--force`, `--keep-archives`) con el catálogo en
      `src/datasets/sources.py` (URLs y versiones fijas, licencia, si se
      puede compartir y cantidad de archivos esperada por dataset).
      SKU-110K y Kaggle bajan como archivo comprimido (SKU-110K con
      tamaño verificado y descarga reanudable), UniDataPro archivo por
      archivo desde Hugging Face, y Roboflow por su API con
      `ROBOFLOW_API_KEY`. Extracción protegida contra rutas que escapan
      de la carpeta; el zip de Kaggle trae una carpeta raíz extra que
      se quita (`archive_root`). 17 tests en
      `tests/test_dataset_sources.py`. Verificado: `--check` valida los
      5 datasets locales; descarga real de UniDataPro y Kaggle idéntica
      a la copia local, y reanudación real de una descarga cortada. Sin
      probar: la descarga de Roboflow (nadie tiene API key aún) y la
      de SKU-110K completa (solo URL y reanudación).
- [x] **#13** (dueño: Mariana) CI en GitHub Actions: correr
      `pytest tests/` y `docker build` en cada PR, y proteger `main`
      (merge solo por PR con una revisión y CI en verde). Hecho:
      `.github/workflows/ci.yml` con los jobs `tests` (Python 3.10,
      PyTorch CPU) y `docker` (build sin publicar + pytest dentro de la
      imagen), en `ubuntu-24.04` fijo (`ubuntu-latest` pasa a Ubuntu 26
      el 2026-10-19 y puede no traer Python 3.10). Protección de `main`
      aplicada: PR obligatorio, 1 aprobación, checks `tests` y `docker`,
      también para admins, sin force push ni borrado.

## Notas

- Cambio de alcance (2026-09-27): la ROI de la góndola la segmenta el
  sistema automáticamente (antes el Administrador la definía a mano) y la
  profundidad de góndola es constante, de 20-30 cm. Ya están actualizados
  README, CLAUDE.md, `docs/datasets.md` y `roi_filter.py`. Siguen
  desactualizados estos anexos de diseño, que no se modificaron:
  `Anexos/Diseño/Mockups/Mockup Admin-1.jpg` (pantalla "Editor de Región
  de Interés (ROI)" con el botón "Guardar Máscara ROI"),
  `Mockup Admin-4.jpg` (log "Actualizó máscara ROI") y
  `Plantilla de C.U 01.docx` (menciona YOLOv8 en vez de YOLO26).
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
  formato COCO). `scripts/download_datasets.py` los descarga si cada
  integrante configura su API key personal de Roboflow en
  `ROBOFLOW_API_KEY` o `.env`; sin key, se pueden copiar desde otro
  integrante (CC BY 4.0) y validar con `--check`.
