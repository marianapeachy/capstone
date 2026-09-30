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
| `src/models/` | En curso: `ProductDetector` y scripts de entrenamiento listos; falta entrenar en GPU | #5 |
| `src/postprocessing/` | Hecho: disponibilidad por repisa y alerta de quiebre (libre >= 30%) | #6 |
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
5. [x] (dueño: Francisco) Resolver limitaciones de la segmentación. Ítem
       #15: F1 de repisas en SHARD 0.758 -> 0.823 (holdout); lo que
       sigue, en #17.

## Pendientes (priorizados)

- [ ] **#5** (dueño: Francisco) Integrar inferencia YOLO26 en `src/models/` (se decidió
      YOLO26 sobre YOLOv8/YOLO11 por su cabeza sin NMS y mejor manejo de
      objetos chicos, clave en productos apilados). Validado en local:
      `ultralytics` 8.4.164 + `yolo26n.pt` corre sobre SKU-110K y se
      encadena con `crop_roi()`/`to_original()`; `tests/test_models.py`
      fija el contrato (versión >= 8.4.0, `nms=False` activa el modo
      end-to-end y respeta `max_det`). Hecho (2026-09-29): inferencia en
      `src/models/detector.py` (`ProductDetector.detect()` -> lista de
      `Detection` con bbox estándar, fija `nms=False`, `max_det=1000` e
      `imgsz=1280`, y rechaza modelos sin cabeza sin NMS). Dataset YOLO con
      `scripts/prepare_yolo_dataset.py` (`xyxy_to_yolo()` en
      `converters.py`). Las imágenes se enlazan desde `data/raw/`; los 712
      JPEG truncados de SKU-110K se copian, porque Ultralytics los
      reescribe al repararlos. Entrenamiento, reanudación y evaluación en
      `scripts/train_detector.py` (variantes `yolo26s` y `yolo26s-p2`,
      entrena y valida con `nms=False` y `max_det=1000`: por defecto
      Ultralytics mide la cabeza con NMS y corta en 300 cajas). Guía para
      el PC con GPU en `docs/training.md`. Todo el flujo verificado con
      una prueba corta en CPU (16 imágenes, 1 época). Pendiente: entrenar
      en el PC con GPU NVIDIA (sin GPU en el portátil de Francisco),
      comparar las dos variantes en `val`, evaluar la ganadora en `test` y
      registrar aquí las métricas.
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
- [ ] **#17** Limitaciones de la segmentación que siguen tras #15 (F1
      de repisas 0.82 en SHARD):
      - Líneas sobre filas de productos iguales (bandas de color o
        bordes superiores alineados de bolsas y cajas apiladas): los
        chequeos clásicos probados en #15 no las separan de las
        repisas. Atacarlas en `src/postprocessing/` con el detector
        (#5): una línea que cruza por el medio de productos detectados
        no es repisa.
      - Recall 0.85: el soporte de borde descarta repisas reales tapadas
        en parte (postes, productos colgantes).
      - Localización: la diferencia con la altura anotada en SHARD está
        centrada (mediana +0.5% del alto) pero dispersa (desv. estándar
        2%), por el grosor del borde de repisa y el ruido de anotación;
        con tolerancia 5% el F1 es 0.88.
      - Fotos con perspectiva fuerte y primeros planos de productos
        colgantes (sin repisas).
      - ROI casi igual a la imagen en primeros planos y validación con
        cámaras de sala: siguen en #14. Para lo que SHARD no cubre
        (repisas inclinadas, contorno de la góndola), set chico
        etiquetado a mano (polilíneas, ej. en CVAT o Label Studio).

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
- [x] **#15** (dueño: Francisco) Limitaciones de la segmentación (ítem
      #4), medidas contra las repisas anotadas de SHARD. Hecho: SHARD en
      el catálogo (`shard`: figshare, CC BY 4.0, `.7z` de 3.6 GB que se
      descomprime con `py7zr`, más `annotation.csv`; 22,743 fotos
      verificadas con `--check` y MD5 de figshare). Evaluador
      `src/evaluation/shelf_evaluation.py`: cada `ShelfLine` se reduce a
      su Y promedio (en una recta, la Y en el centro del tramo) como
      fracción del alto y se empareja 1 a 1 con las repisas anotadas con
      tolerancia configurable (3% del alto por defecto); precisión,
      recall y F1 por imagen y en total. CLI `scripts/evaluate_shard.py`
      (fotos barajadas con semilla 0: "dev" = primeras 1000, para
      ajustar; "holdout" = siguientes 1000, para confirmar) y
      `visualize_segmentation.py --dataset shard` (lámina con las
      repisas anotadas en verde). Resultados con tolerancia 3%
      (precisión / recall / F1):
      línea base dev 0.661 / 0.888 / 0.758, holdout 0.660 / 0.890 /
      0.758; final dev 0.793 / 0.851 / 0.821, holdout 0.796 / 0.851 /
      0.823. Cambios adoptados, medidos uno a uno en dev:
      (1) soporte de borde a lo largo de toda la recta (subfranjas de
      1/4 de franja; el 70% debe tener un salto de al menos 0.5 veces
      la referencia de su franja): F1 0.758 -> 0.796, elimina la mayoría
      de las diagonales falsas; (2) un borde a menos de la separación
      mínima entre repisas (7% del alto) del borde superior de la foto
      no se informa como repisa (sin espacio para productos encima;
      SHARD anota ahí el 0.1% de sus repisas y el método ponía 536
      líneas en 1000 fotos, ~1% correctas), pero sigue limitando la ROI:
      -> 0.821; (3) la ROI se extiende de a una franja hacia los lados
      mientras haya textura (antes era la unión de los tramos de las
      líneas y, con menos líneas, quedaba a media imagen): no cambia el
      F1 y mantiene las anotaciones dentro de la ROI en 0.99-1.00.
      Descartados porque bajan el F1: coherencia de la pendiente con las
      repisas vecinas (ajuste ángulo vs. altura; con umbral de 1-3°, F1
      0.695-0.790: las pendientes ajustadas con 6 puntos son ruidosas),
      patrón de franja de repisa (dos bordes cercanos de signo opuesto:
      no separa repisas de filas de productos, AUC 0.50; uniformidad y
      saturación de la franja: AUC 0.62-0.67, todo umbral baja el F1),
      más franjas, menor `min_edge` y menor separación mínima. Métricas
      aproximadas en los otros 5 datasets (100 fotos c/u): anotaciones
      dentro de la ROI y área de la ROI sin cambios; repisas con
      productos encima sube (SKU-110K 0.76 -> 0.80) y productos
      apoyados en una repisa baja (0.52 -> 0.48), coherente con más
      precisión y algo menos de recall. Una foto de Out Of Stock (de
      100) queda sin repisas (`found=False`, contingencia de análisis
      global). Lo que sigue: ítem #17.
- [x] **#6** (dueño: Francisco) Cálculo de disponibilidad y alerta de
      quiebre de stock en `src/postprocessing/availability.py`:
      `compute_availability(productos, niveles)` ->
      `GondolaAvailability` (espacio libre de la góndola, alerta y
      `ShelfAvailability` por repisa con sus huecos, área libre en px y
      `level_index`) y `free_volume_cm3()` (área libre x 25 cm, cuando
      haya escala cm/px). Recibe cajas y niveles como tuplas o arrays
      (no importa `src/preprocessing` ni `src/models`); sin repisas, la
      ROI es el único nivel. Criterio (decidido 2026-09-30, reemplaza
      "disponibilidad < 30%", que leído al pie de la letra alertaba con la
      góndola llena): alerta si el espacio **libre** es >= 30% del
      frente de la góndola. Métrica: cobertura horizontal por repisa;
      hueco = tramo sin producto de al menos 1 ancho de producto (mediana
      de la repisa). No mide la altura de los productos: pilas con pocas
      unidades o productos bajos siguen disponibles, y el eje vertical es
      el que más deforma una cámara de sala. Una caja cubre todo nivel
      con el que comparte >= 30% del alto menor, así una repisa falsa a
      media altura de una fila de productos (#17) no crea un nivel vacío.
      La góndola se acota a los productos (del primer al último nivel con
      productos, y del producto más a la izquierda al más a la derecha):
      la ROI de la segmentación incluye pasillo, techo y carteles. Medido
      con `scripts/evaluate_availability.py` (SKU-110K `val`, 300 fotos,
      anotaciones como detector y recall simulado 0.9): falsas alertas
      con la góndola llena 24.7% con la ROI -> 4.0% acotada; quiebre
      simulado en el interior de 30% del frente detectado 87%, de 40%
      99.7%. Umbral: 20% / 25% / 30% / 35% dan 20.7% / 8.7% / 4.0% / 1.0%
      de falsas alertas; se mantiene 30%. Costo del acotado: una repisa
      extrema vacía entera, o una franja vacía en todas las repisas en un
      extremo, no se cuentan (quiebre de 40% en cualquier parte: 88%).
      24 tests en `tests/test_availability.py`. Pendiente: medir con el
      detector entrenado (#5) y con fotos de cámaras de sala (#14).
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
- [x] **#16** (dueño: Mariana) Corregir datos desactualizados de
      `docs/datasets.md` (licencias, tamaño de grocery-shelves y estado
      de descarga). Licencias: supermarket-shelves es CC0 1.0 y los dos
      de Roboflow CC BY 4.0, igual que `src/datasets/sources.py`;
      grocery-shelves ocupa ~37 MB en disco (no 71 MB); el estado de
      los 5 indica su clave en `scripts/download_datasets.py`.
- [x] **#18** (dueño: Francisco) Notas de instalación en un entorno
      nuevo (Windows): README explica cómo detectar una copia vieja de
      `graphify` que tapa la 0.9.70 en el `PATH`, y que SKU-110K y SHARD
      se reanudan volviendo a correr el script si la descarga se corta;
      `docs/datasets.md` explica la descarga manual de los 2 datasets
      de Roboflow (sin API key) y dónde descomprimirlos.
- [x] **#19** (dueño: Francisco) Plan de pruebas en `docs/test-plan.md`:
      para cada etapa ya hecha, qué requisito cumple, cómo se prueba,
      criterio de aceptación y resultado actual; trazabilidad con
      RF01-RF05 y lo que aún no se puede probar. Primera ejecución
      completa tras mergear #6 (2026-09-30, `main` 9cd8286): 131 tests
      OK; SEG-02 F1 0.823, SEG-03 0.99-1.00, AV-02 4.0% y AV-03 99.7%,
      todo dentro de criterio (detalle en el registro del plan).
      Volver a ejecutarlo con el detector entrenado (#5) y con el
      pipeline completo (#8).

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
