# Diseño: `scripts/run_pipeline.py` (ítem #8)

Fecha: 2026-10-07. Dueño: Francisco. Estado: aprobado en conversación,
pendiente de revisión escrita.

## Objetivo

Correr el pipeline completo sobre fotos de góndola y mostrar el resultado.
Esta primera versión sirve para tres cosas:

1. **Demo visual para Walmart**: una imagen anotada, limpia, con los
   huecos y la alerta.
2. **Demo interna** del avance del sistema.
3. **Medir y probar**: cerrar INT-02, INT-03 y RF01 de
   `docs/test-plan.md`.

Fuera de alcance: lote para la prueba ciega de Walmart, reportes Excel /
CSV / PDF (#7), envío de alertas (RF04) y calibración de lente por CLI
(no hay calibración de ninguna cámara todavía).

## Arquitectura

```
scripts/run_pipeline.py      CLI: argumentos, recorrer fotos, guardar, tabla
        │
        ├── src/pipeline.py              run_image() -> PipelineResult
        │      correct_image -> segment_gondola -> crop_roi -> detector.detect
        │      -> RoiCrop.to_original -> shelf_levels -> compute_availability
        │      -> CorrectedImage.to_original_points (a la foto original)
        │
        └── src/reporting/annotate.py    draw_availability(foto, resultado)
```

- `src/pipeline.py` es el único módulo que conoce todas las etapas. No es
  una etapa: las etapas siguen sin importarse entre sí (`CLAUDE.md`).
- `src/reporting/annotate.py` recibe el `PipelineResult` (dataclass de
  datos simples) y no importa `preprocessing`, `models` ni
  `postprocessing`.

## `src/pipeline.py`

```python
def run_image(image, detector, calibration=None, conf=DEFAULT_CONF) -> PipelineResult
```

- `image`: foto original BGR (`np.ndarray`).
- `detector`: cualquier objeto con `detect(image, conf) -> list` de
  elementos con `.bbox` (`ProductDetector` en producción, un detector
  falso en los tests).
- `calibration`: `LensCalibration | None`. Sin calibración solo se aplica
  CLAHE (como en `scripts/evaluate_availability.py`).

Pasos:

1. `corrected = correct_image(image, calibration)`.
2. `segmentation = segment_gondola(corrected.image)`.
3. `crop = crop_roi(corrected.image, segmentation.roi)`.
4. `detections = detector.detect(crop.image, conf)`; cada caja pasa a la
   imagen corregida con `crop.to_original()`.
5. `levels = shelf_levels(boxes, [astuple(l) for l in segmentation.shelf_lines], segmentation.roi)`.
6. `availability = compute_availability(boxes, levels)`.
7. Todo lo que se devuelve pasa a la **foto original**: cajas con
   `corrected.to_original()`; polígonos de repisa y de hueco con
   `corrected.to_original_points()`, densificando cada borde (puntos
   intermedios) para que con lente fisheye se vean curvos como en la foto.

Los cálculos de disponibilidad se hacen en la imagen corregida (donde se
segmentaron las repisas); solo la salida está en la original (INT-03).

Tiempos medidos con `time.perf_counter()`: `correction`, `segmentation`
(incluye el recorte), `detection` (incluye `to_original` de las cajas) y
`availability` (`shelf_levels` + `compute_availability` + paso a la
original).

### `PipelineResult`

Dataclasses congeladas, solo con tuplas y números:

```python
ShelfResult:
    level_index: int
    polygon: tuple[Point, ...]          # contorno en la foto original
    gaps: tuple[tuple[Point, ...], ...] # un polígono por hueco, foto original
    product_count: int
    free_fraction: float
    critical: bool

StageTimes:
    correction, segmentation, detection, availability: float  # segundos
    total (propiedad)

PipelineResult:
    image_size: tuple[int, int]         # (ancho, alto) de la original
    roi: BBox                           # foto original
    products: tuple[BBox, ...]          # foto original
    shelves: tuple[ShelfResult, ...]
    free_fraction: float                # góndola completa
    critical: bool                      # libre >= 30%
    segmentation_found: bool            # False: sin repisas, análisis global
    times: StageTimes
    to_dict() -> dict                   # serializable a JSON
```

El polígono de un hueco `(x0, x1)` de una repisa es el tramo del
cuadrilátero de esa repisa entre `x0` y `x1`, siguiendo sus bordes
superior e inferior (inclinados si la repisa lo está).

## `src/reporting/annotate.py`

`draw_availability(image, result) -> np.ndarray`: copia de la foto
original con la **vista limpia**:

- Huecos rellenos en rojo semitransparente.
- Contorno tenue de cada repisa y etiqueta "Repisa N · 12% libre".
- Cartel superior: rojo "QUIEBRE DE STOCK · 34% libre" si `critical`,
  verde "OK · 8% libre" si no. Si `segmentation_found` es falso, agrega
  "(sin repisas: análisis global)".
- Sin cajas de productos ni ROI.

Textos con `cv2.putText`, escalados al tamaño de la foto.

## `scripts/run_pipeline.py`

```
python scripts/run_pipeline.py FOTOS_O_CARPETAS...
       [--weights data/processed/training/yolo26s/weights/best.pt]
       [--out data/processed/pipeline] [--device cpu] [--threads 4] [--conf 0.25]
```

- Entradas: fotos y/o carpetas (no recursivo; `.jpg`, `.jpeg`, `.png`,
  `.bmp`, en orden alfabético).
- Carga el modelo una vez (`ProductDetector(weights, device)`,
  `torch.set_num_threads(threads)`) e informa ese tiempo aparte.
- Por foto: `<out>/<nombre>.jpg` (vista limpia) y `<out>/<nombre>.json`
  (`PipelineResult.to_dict()`).
- Tabla en la terminal: foto, % libre, alerta, segundos por etapa y total;
  última fila con la mediana de las fotos procesadas.
- Errores: foto ilegible -> fila "no se pudo leer" y sigue; sin repisas ->
  se procesa con análisis global y la fila lo indica; sin pesos o sin
  fotos -> mensaje claro y código de salida 2.
- El `--weights` por defecto se actualiza a la variante ganadora cuando
  termine el ítem #5.

## Pruebas (`tests/test_pipeline.py`, sin pesos ni GPU)

- **Góndola sintética**: fondo gris, repisas como franjas oscuras
  horizontales y productos como bloques de color saturado. Un detector
  falso encuentra los bloques por color (umbral de saturación +
  contornos) en la imagen que recibe.
- **INT-02**: `run_image()` sobre la góndola sintética da el mismo
  resultado que encadenar las etapas a mano; quitar productos de una
  repisa crea un hueco en esa repisa y, sobre el 30% libre, la alerta.
- **INT-03**: la góndola sintética distorsionada con una calibración
  fisheye sintética (`LensCalibration.approximate`). Las cajas, repisas y
  huecos del resultado son los calculados en la imagen corregida llevados
  a la original con `CorrectedImage`; sin calibración, coinciden con los de
  la imagen corregida.
- **Vista limpia**: misma forma que la foto; píxeles dentro de un hueco
  quedan con más rojo; el color del cartel sigue a `critical`.
- **CLI**: con `ProductDetector` reemplazado por el detector falso
  (`monkeypatch`), una carpeta con dos fotos produce dos JPG y dos JSON;
  sin fotos, código de salida 2.
- **RF01** (manual, no en CI): `yolo26s` en CPU sobre las 6 fotos de
  `data/processed/demo/`; mediana por etapa registrada en
  `docs/test-plan.md`.

## Documentación

- README, "Ejecución local": uso del CLI.
- `docs/test-plan.md`: INT-02, INT-03 y RF01 con su resultado.
- `PROGRESS.md`: ítem #8 marcado `[x]` y movido a "Hecho" en el mismo PR.
- `CLAUDE.md`, "Estructura relevante": `src/pipeline.py`.

## Restricciones de este PC mientras entrena

Trabajo en el worktree `../capstone-pipeline` (rama `feat/run-pipeline`).
Nada en la GPU (`CUDA_VISIBLE_DEVICES=-1`). La corrida de RF01 con YOLO en
CPU, con prioridad baja, 4 hilos y solo con al menos 2 GB de RAM libres.
