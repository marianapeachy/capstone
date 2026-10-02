# Plan de pruebas - ShelfVision AI

Verifica que cada etapa ya construida cumple lo que promete: qué
requisito cubre, cómo se prueba, qué resultado se exige y qué resultado
dio la última vez. Ítem #19 de `PROGRESS.md`.

**Cuándo se ejecuta completo:**

1. Al mergear el ítem #6 (disponibilidad, PR #16).
2. Cuando exista el detector entrenado (`best.pt`, ítem #5).
3. Antes de cada entrega académica (Fase 2 y Fase 3).

Cada ejecución se anota en el [registro](#registro-de-ejecuciones) al
final.

## Tipos de prueba

| Tipo | Qué asegura | Cómo se corre |
| --- | --- | --- |
| **Unitaria** | El contrato de cada función: formato de bbox, coordenadas, errores ante entradas inválidas | `pytest tests/` (también en el CI de cada PR) |
| **Métrica** | Que el método funciona sobre datos reales, con un número comparable entre versiones | Scripts de `scripts/` sobre los datasets de `data/raw/` |
| **Visual** | Lo que un número no muestra: repisas mal puestas, cajas corridas | Láminas generadas por los visores, revisadas con la lista de cada sección |
| **Trazabilidad** | Que cada requisito del README (RF01-RF05) y cada regla de `CLAUDE.md` tiene al menos una prueba | Tablas de las secciones 8 y 9 |

Los criterios marcados **(por acordar)** no estaban definidos en el
proyecto: son una propuesta basada en lo ya medido y se confirman en la
revisión de este plan.

## Cómo ejecutarlo

Desde la raíz del repo, con el `.venv` activo y los datasets descargados
(ver `docs/datasets.md`):

```bash
pytest tests/                                          # unitarias
python scripts/download_datasets.py --check            # DAT-01
python scripts/prepare_datasets.py                     # DAT-04 (sin --dataset, ver DAT-04)
python scripts/evaluate_shard.py --split holdout       # SEG-02
python scripts/visualize_segmentation.py               # SEG-03 y SEG-04
python scripts/evaluate_availability.py                # AV-02 y AV-03
python scripts/train_detector.py val --weights <best.pt> --split test   # DET-04 (con el modelo entrenado)
```

## 1. Datos (ítems #10, #11, #12, #16)

| ID | Qué se verifica | Cómo | Criterio | Último resultado |
| --- | --- | --- | --- | --- |
| DAT-01 | Los 6 datasets están completos en `data/raw/` | `download_datasets.py --check` | Los 6 en OK | OK (2026-09-29) |
| DAT-02 | Los conversores llevan cada formato (COCO, CSV, XML, Supervisely) a `[x_min, y_min, x_max, y_max]` en píxeles | `tests/test_dataset_converters.py` | Pasan | Pasan |
| DAT-03 | La descarga es reproducible y segura (versiones fijas, sin rutas que escapan de la carpeta) | `tests/test_dataset_sources.py` | Pasan | Pasan |
| DAT-04 | Las anotaciones combinadas están completas | `prepare_datasets.py`; revisar el total | 1,760,633 anotaciones de 5 datasets | 1,760,633 (#11). **Problema conocido:** con `--dataset X`, `all_annotations.csv` queda solo con ese dataset; correrlo sin `--dataset` |
| DAT-05 | El dataset YOLO es correcto (cajas normalizadas y ruta local) | `tests/test_dataset_converters.py` (`xyxy_to_yolo`) y `prepare_yolo_dataset.py --limit 16` | Pasan; `data.yaml` apunta a la carpeta del repo | OK (2026-09-30, regenerado tras mover el repo) |

## 2. Corrección de imagen (ítem #3)

| ID | Qué se verifica | Cómo | Criterio | Último resultado |
| --- | --- | --- | --- | --- |
| COR-01 | CLAHE mejora el detalle en sombras sin alterar colores | `tests/test_image_correction.py` | Pasan | Pasan |
| COR-02 | El dewarping endereza una repisa curvada (distorsión sintética) y `to_original()` vuelve a la imagen original | `tests/test_image_correction.py` | Pasan | Pasan |
| COR-03 | Sin calibración solo se aplica CLAHE y las coordenadas no cambian | `tests/test_image_correction.py` | Pasan | Pasan |
| COR-04 | El dewarping funciona con una cámara real | Fotos de un tablero de ajedrez o la calibración de Walmart | Repisas rectas a ojo; error de reproyección < 1 px **(por acordar)** | **No probado**: no hay calibración real |

## 3. Segmentación de góndola y repisas (ítems #4, #15)

| ID | Qué se verifica | Cómo | Criterio | Último resultado |
| --- | --- | --- | --- | --- |
| SEG-01 | Repisas, niveles y ROI en imágenes sintéticas (incluidas repisas inclinadas y el caso sin repisas) | `tests/test_gondola_segmentation.py` y `tests/test_shelf_evaluation.py` | Pasan | Pasan |
| SEG-02 | Las repisas detectadas coinciden con las anotadas en SHARD (tolerancia 3% del alto) | `evaluate_shard.py --split holdout` | F1 >= 0.80 **(por acordar)**; no bajar de la última medición | P 0.796 / R 0.851 / F1 0.823 (2026-09-30; igual que en #15) |
| SEG-03 | La ROI contiene los productos | `visualize_segmentation.py` (`metrics.csv`, `annotations_inside_roi`) | >= 0.99 en cada dataset | 0.99-1.00 (2026-09-30) |
| SEG-04 | Revisión visual de 30 láminas por dataset | `visualize_segmentation.py` | Las líneas rojas caen sobre bordes de repisa reales; sin diagonales; la ROI cubre los productos. Anotar los casos que fallan | Hecho en #15; limitaciones en #17 |
| SEG-05 | Funciona con vista de cámara de sala (alta, oblicua, fisheye) | Imágenes tipo CCTV (#14) | Por definir con #14 | **No probado** |

## 4. Recorte de ROI (ítems #1, #2)

| ID | Qué se verifica | Cómo | Criterio | Último resultado |
| --- | --- | --- | --- | --- |
| ROI-01 | Recorte exacto; ROI parcialmente fuera se recorta; ROI totalmente fuera, imagen `None` o vacía -> `ValueError` | `tests/test_preprocessing.py` | Pasan | Pasan |
| ROI-02 | Una caja del recorte vuelve a su lugar en la imagen original (`RoiCrop.to_original()`) | `tests/test_preprocessing.py` y `tests/test_detector.py` | Pasan | Pasan |

## 5. Detector YOLO26 (ítem #5)

| ID | Qué se verifica | Cómo | Criterio | Último resultado |
| --- | --- | --- | --- | --- |
| DET-01 | Contrato de inferencia: `ultralytics>=8.4.0`, cabeza sin NMS (`nms=False`), sin tope de 300 cajas, rechazo de modelos que no son YOLO26 | `tests/test_models.py` y `tests/test_detector.py` | Pasan | Pasan |
| DET-02 | El entrenamiento corre de punta a punta y se reanuda | Prueba corta de `docs/training.md` (16 fotos, 1 época) | Termina y deja `best.pt` y `metrics.json` | OK en CPU (2026-09-29) |
| DET-03 | Comparación de `yolo26s` y `yolo26s-p2` en `val` | `train_detector.py val` para cada una | Se elige por `map50_95` y luego `recall` (ver `docs/training.md`) | **Pendiente**: entrenamiento en GPU |
| DET-04 | La variante ganadora en `test` (una sola vez) | `train_detector.py val --split test` | Recall >= 0.90 con `conf=0.25` **(por acordar)**: la tasa de falsas alertas de AV-02 (4%) se midió con recall 0.9, y con 0.8 sube a 11.7%. `map50_95` se informa | **Pendiente** |
| DET-05 | Revisión visual de las detecciones | Láminas `val_batch*_pred.jpg` de Ultralytics | Cajas ajustadas a cada producto, sin cajas sobre carteles ni pilares | **Pendiente** |

## 6. Disponibilidad y alerta (ítem #6, PR #16)

| ID | Qué se verifica | Cómo | Criterio | Último resultado |
| --- | --- | --- | --- | --- |
| AV-01 | Huecos, acotado a los productos, niveles, umbral inclusivo de 30%, volumen con 25 cm | `tests/test_availability.py` | Pasan | Pasan (24 tests) |
| AV-02 | Falsas alertas con la góndola llena (anotaciones de SKU-110K como detector, recall simulado 0.9) | `evaluate_availability.py` | <= 5% **(por acordar)** | 4.0% (2026-09-30) |
| AV-03 | Detección de un quiebre simulado de 40% del frente en el interior | `evaluate_availability.py` | >= 95% **(por acordar)** | 99.7% (2026-09-30) |
| AV-04 | AV-02 y AV-03 con las detecciones del modelo entrenado en vez de las anotaciones | `evaluate_availability.py` con detector (hay que agregarle esa opción) | Mismos criterios | **Pendiente**: #5 |

## 7. Integración entre etapas

| ID | Qué se verifica | Cómo | Criterio | Último resultado |
| --- | --- | --- | --- | --- |
| INT-01 | Una detección sobre el recorte vuelve a la imagen original | `tests/test_detector.py` | Pasa | Pasa |
| INT-02 | El pipeline completo corre sobre una imagen: `correct_image()` -> `segment_gondola()` -> `crop_roi()` -> `detect()` -> `to_original()` -> `compute_availability()` | Test de punta a punta con una imagen sintética, junto con `scripts/run_pipeline.py` (#8) | Pasa; resultado igual al de las etapas por separado | **No existe aún**: hoy solo se encadena en la guía visual local |
| INT-03 | Sistema de coordenadas: la disponibilidad se calcula en la imagen corregida (donde se segmentaron las repisas) y el reporte usa la original | Test con calibración fisheye sintética | Los huecos coinciden con los de la imagen corregida | **No existe aún** (#8) |

## 8. Trazabilidad con los requisitos (README)

| Requisito | Cubierto por | Estado |
| --- | --- | --- |
| RF01 Ingesta de imágenes, 2 a 5 s por imagen | INT-02; medir el tiempo por etapa con 50 fotos en el portátil (CPU) y en el PC con GPU | **Sin medir** |
| RF02 Espacios vacíos dentro de la ROI | SEG-03, AV-01, AV-02 | Cubierto con anotaciones; falta con el detector (AV-04) |
| RF03 Disponibilidad en % o cm, profundidad fija de 25 cm | AV-01 (% y volumen) | % cubierto. Para cm falta la escala cm/px de cada cámara, que hoy no tiene fuente |
| RF04 Alertas de quiebre | AV-01 a AV-03 (la decisión de alertar) | Decisión cubierta; el envío de la notificación no está implementado |
| RF05 Reportes Excel, CSV y PDF | - | **Pendiente**: #7 |

## 9. Reglas de `CLAUDE.md`

| Regla | Cómo se verifica | Estado |
| --- | --- | --- |
| Bounding boxes `[x_min, y_min, x_max, y_max]` en píxeles | DAT-02, ROI-02, DET-01 | Cubierta |
| Orden híbrido: corrección -> segmentación -> recorte -> YOLO26 | INT-02 | **Sin test** hasta #8 |
| ROI automática, sin configuración por cámara | Revisión de código: ninguna función lee una ROI de configuración | Cubierta por diseño |
| Profundidad constante de 25 cm | AV-01 (`GONDOLA_DEPTH_CM`) | Cubierta |
| YOLO26 con `nms=False`, `max_det >= 1000`, `imgsz=1280` | DET-01 | Cubierta |
| Etapas sin importar detalles internos de otras | Test que revise los `import` de cada paquete de `src/` **(por agregar)** | **Sin test** |
| Alerta con espacio libre >= 30% | AV-01 | Cubierta |

## 10. Lo que aún no se puede probar

- **Dataset oculto de Walmart**: se reserva para la evaluación ciega
  final; nunca se usa para ajustar.
- **Cámaras reales de sala**: sin fotogramas ni calibración de Walmart
  (COR-04, SEG-05). Mientras tanto, imágenes sintéticas tipo CCTV (#14).
- **Escala en centímetros** (RF03 en cm): depende de cada cámara.
- **Tiempo en el hardware final** (RF01): no se conoce el equipo donde
  correrá el sistema.

## Registro de ejecuciones

| Fecha | Commit | Quién | Resultado | Observaciones |
| --- | --- | --- | --- | --- |
| 2026-09-30 | `main` 4848c64 + PR #16 | Francisco | `pytest`: 131 passed. AV-02 y AV-03 cumplen. SEG-02 y SEG-03 tomados de #15 (2026-09-28) | Línea base del plan. DET-03 a DET-05, AV-04, INT-02, INT-03 y RF01 pendientes |
| 2026-09-30 | `main` 9cd8286 (PR #16 mergeado) | Francisco | `pytest`: 131 passed. DAT-01 6/6 OK; DAT-04 1,760,633; DAT-05 OK. SEG-02 F1 0.823 (P 0.796 / R 0.851); SEG-03 0.99-1.00. AV-02 4.0%; AV-03 99.7%. Todo cumple | Primera ejecución tras mergear #6. SEG-04: lámina de SKU-110K revisada, sin casos nuevos (diagonales en una foto oblicua de refrigeradores, ya en #17). Sin imports entre etapas en `src/` (revisión manual; sigue sin test). DET-02 no se repitió (OK 2026-09-29) |
