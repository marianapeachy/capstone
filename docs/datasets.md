# Datasets - ShelfVision AI

Registro de datasets candidatos para entrenamiento y validación del
pipeline (preprocessing -> YOLO26 -> postprocessing). Ninguno se versiona
en Git (ver `.gitignore`); se descargan a `data/raw/` en el entorno local
de cada integrante.

## Ya identificados por el equipo

| Dataset | Fuente | Contenido | Licencia | Estado |
| --- | --- | --- | --- | --- |
| [grocery-shelves](https://huggingface.co/datasets/UniDataPro/grocery-shelves) | Hugging Face (UniDataPro) | **Solo 15 imágenes de muestra** (+ máscaras de etiqueta) con `annotations.xml`. El "5000+" del README es material de marketing del dataset comercial completo que UniDataPro vende aparte; el repo público de HF es únicamente el sample gratuito. | `cc-by-nc-nd-4.0` (no comercial, sin derivados) | Descargado en `data/raw/grocery-shelves-unidatapro/` (~37 MB). Se descarga con `scripts/download_datasets.py` (clave `unidatapro`) |
| [supermarket-shelves-dataset](https://www.kaggle.com/datasets/humansintheloop/supermarket-shelves-dataset) | Kaggle (humansintheloop) | Góndolas con anotación de producto y precio | CC0 1.0 (dominio público; [ficha de Humans in the Loop](https://humansintheloop.org/resources/datasets/supermarket-shelves-dataset/)) | Descargado en `data/raw/supermarket-shelves/`. Se descarga con `scripts/download_datasets.py` (clave `kaggle_supermarket`) |

## Adicionales recomendados

| Dataset | Fuente | Por qué aporta valor | Licencia | Estado |
| --- | --- | --- | --- | --- |
| [SKU-110K](https://docs.ultralytics.com/datasets/detect/sku-110k/) | [Trax Retail / eg4000/SKU110K_CVPR19](https://github.com/eg4000/SKU110K_CVPR19) | Benchmark académico estándar (CVPR'19) para detección en góndolas densamente pobladas: 11,743 imágenes, 1.7M+ bounding boxes de producto en clase única. **Soporte nativo en Ultralytics** (YAML de config `SKU-110K.yaml` incluido en la librería `ultralytics`, compatible con YOLO26). Ideal para pre-entrenar/afinar el detector base antes del dataset oculto de Walmart Chile. | Académico y no comercial, sin redistribución | Descargado (12.2 GB) en `data/raw/sku-110k/SKU110K_fixed/` (train/val/test + anotaciones CSV). Se descarga con `scripts/download_datasets.py` (clave `sku110k`) |
| [Out Of Stock detection](https://universe.roboflow.com/empty-space-detection-capstone/out-of-stock-detection) | Roboflow Universe | Anota directamente la clase **"Empty-space"**, no productos. Es el único dataset de la lista alineado 1:1 con RF02/RF03 (alerta con espacio libre `>= 30%`), en vez de inferir el vacío por ausencia de producto. | CC BY 4.0 | Descargado (346 MB, formato COCO) en `data/raw/out-of-stock-detection-roboflow/train/` (3024 imágenes, `_annotations.coco.json`). Solo trae split `train`, sin `valid`/`test`. Se descarga con `scripts/download_datasets.py` (clave `roboflow_out_of_stock`; requiere `ROBOFLOW_API_KEY`) |
| [Empty Shelf Detector](https://universe.roboflow.com/fyp-ormnr/empty-shelf-detector) | Roboflow Universe | Complementa al anterior con más variabilidad de ángulos/iluminación en la misma clase "empty". | CC BY 4.0 | Descargado (31 MB, formato COCO) en `data/raw/empty-shelf-detector-roboflow/` (train: 291, valid: 24, test: 18 imágenes). Se descarga con `scripts/download_datasets.py` (clave `roboflow_empty_shelf`; requiere `ROBOFLOW_API_KEY`) |

> **Corrección:** el dataset "TrainingDataPro/grocery-shelves-dataset"
> reportado previamente **no existe** (confirmado vía API de Hugging Face:
> repo inexistente). Se descarta de la lista.

## Candidatos tipo cámara de sala

Búsqueda del 2026-09-27 (ítem #14 de `PROGRESS.md`): imágenes con vista
alta, oblicua o gran angular/fisheye, parecidas a las cámaras de
seguridad de Walmart. Ningún dataset público combina cámaras reales de
sala con anotación de productos o espacios vacíos; estos cubren partes
del problema.

| Dataset | Qué aporta | Anotación | Licencia / acceso |
| --- | --- | --- | --- |
| [SHARD](https://figshare.com/articles/dataset/SHARD_-_SHelf_mAnagement_Row_Dataset/24100695) | ~22K fotos de góndolas de ~2000 supermercados de Italia. Es el único que **anota repisas**: sirve para medir `segment_gondola()` sin etiquetar a mano (ítem #15). Son fotos de mano, casi frontales. | Altura (Y) de cada repisa como fracción del alto de la imagen (`annotation.csv`, `archivo;y1,y2,...`, en cualquier orden) | CC BY 4.0, descarga directa (3.6 GB, `.7z`). Citar [el paper](https://doi.org/10.1016/j.eswa.2024.124635). **Descargado** en `data/raw/shard/` (22,743 fotos de ~1000 px de alto en `shelf_detection/` + `annotation.csv`, 3.4 GB). Se descarga con `scripts/download_datasets.py` (clave `shard`). Ojo: el `.7z` trae además un `shelf_detection/annotation.csv` truncado (10,663 filas); la anotación válida es el `annotation.csv` aparte de figshare (22,745 filas; 2 imágenes repetidas). Se mide con `scripts/evaluate_shard.py` |
| [MMPTrack](https://iccv2021-mmp.github.io/subpage/dataset.html), entorno *retail* | Cámaras fijas en altura en una tienda de prueba con estanterías, **con calibración intrínseca y extrínseca**: prueba real de dewarping y segmentación desde vista alta. | Solo personas (bbox y posición en el piso) | Solo investigación: firmar términos y enviarlos a iccv2021mmp@outlook.com |
| [Unitail-Det](https://unitedretail.github.io/) | 1.8M productos anotados como cuadriláteros, con set de prueba de otros dominios y ángulos; útil para robustez del detector en vistas oblicuas. | Cuadriláteros por producto | Solo académico. Ya no es público: pedir a fangyic@andrew.cmu.edu |
| [Simuletic CCTV](https://www.kaggle.com/datasets/simuletic/cctv-shoplifting-detection-dataset-yolo-and-vlm) | 400 fotogramas + 8 videos sintéticos con ángulo alto de CCTV, incluidos pasillos de supermercado: revisión a ojo de la segmentación. | Solo personas (bbox + pose) | Muestra gratis en Kaggle; revisar términos |
| [WEPDTOF](https://vip.bu.edu/projects/vsns/cossy/datasets/wepdtof/) | Cámaras fisheye cenitales en interiores reales (no necesariamente tiendas): estresa el dewarping fisheye. | Solo personas | CC BY 4.0, no comercial |
| [ShelfRectSet](https://arxiv.org/abs/2511.20335) | Rectificación de góndolas por homografía (la corrección de perspectiva que falta en el ítem #4). | Homografía / esquinas | Anunciado por los autores (nov. 2025); sin link publicado aún |

Complemento recomendado: generar imágenes "tipo CCTV" a partir de
SHARD y Kaggle supermarket-shelves (no de SKU-110K: su licencia prohíbe
modificar sus fotos) (distorsión fisheye con `LensCalibration`, homografía
oblicua, baja resolución, compresión JPEG, ruido), transformando también
sus anotaciones. Walmart Chile no puede compartir fotogramas reales de
sus cámaras, por privacidad (informado el 2026-10-01): estas imágenes
sintéticas son el principal sustituto de la cámara de sala.

> **Sin anotaciones de góndola ni repisa:** ninguno de los datasets
> descargados anota la góndola ni sus repisas (SHARD, arriba, sí anota
> repisas); solo productos, espacios vacíos y
> precios (grocery-shelves solo trae la clase `Box`). Sirven para
> entrenar el detector, pero no para evaluar la segmentación automática
> de la ROI. Para eso hace falta un set de validación etiquetado a mano
> (ver `PROGRESS.md`).

## Descarga reproducible

`scripts/download_datasets.py` descarga los 5 datasets de arriba y SHARD
a `data/raw/` con la misma estructura que espera
`scripts/prepare_datasets.py` (SHARD no se convierte: no anota bboxes,
sino repisas, y lo usa `scripts/evaluate_shard.py`), y verifica la
cantidad de archivos de cada uno. El catálogo (URLs, versiones fijas, licencias y archivos esperados)
está en `src/datasets/sources.py`.

```bash
python scripts/download_datasets.py --list    # catálogo y licencias
python scripts/download_datasets.py           # descarga lo que falte (SKU-110K: 12.2 GB)
python scripts/download_datasets.py --check   # solo verifica data/raw/
python scripts/prepare_datasets.py            # convierte las anotaciones
```

- **Roboflow** (Out Of Stock detection y Empty Shelf Detector) requiere
  una API key personal gratuita
  ([app.roboflow.com/settings/api](https://app.roboflow.com/settings/api))
  en `ROBOFLOW_API_KEY` o en `.env` (no versionado). Sin ella esos dos se
  omiten.
  - **Descarga manual sin API key:** en cada página de Roboflow Universe
    ([Out Of Stock detection](https://universe.roboflow.com/empty-space-detection-capstone/out-of-stock-detection),
    [Empty Shelf Detector](https://universe.roboflow.com/fyp-ormnr/empty-shelf-detector)),
    botón "Download Dataset" -> formato **COCO** -> "download zip to
    computer" (pide cuenta gratuita de Roboflow, sin API key). Descomprimir
    el `.zip` completo (conserva las carpetas `train/`, `valid/`, `test/`
    con su `_annotations.coco.json`) directo en
    `data/raw/out-of-stock-detection-roboflow/` o
    `data/raw/empty-shelf-detector-roboflow/` según corresponda (el `.zip`
    no trae una carpeta raíz extra, a diferencia del de Kaggle). Confirmar
    con `python scripts/download_datasets.py --check`.
- Kaggle, Hugging Face y figshare (SHARD) se descargan sin cuenta.
  SKU-110K y SHARD se reanudan si la descarga se corta (el parcial queda
  en `data/raw/.downloads/`); son descargas grandes (12.2 GB y 3.6 GB) y
  es normal que un timeout o corte de conexión interrumpa alguna, basta
  con volver a correr `python scripts/download_datasets.py` para
  continuar donde quedó.
- El `.7z` de SHARD se descomprime con `py7zr` (en `requirements.txt`):
  funciona igual en macOS, Windows y Linux sin instalar 7-Zip, y permite
  validar todas las rutas del archivo antes de escribir (como con los
  `.zip`).
- Un dataset que ya está completo no se vuelve a descargar.

### Compartir datasets entre integrantes

Los datasets con licencia que lo permite (`--list` muestra
"compartible: si": los de Roboflow, Kaggle y UniDataPro, ~550 MB) se
pueden pasar comprimidos por una carpeta de Drive/OneDrive **compartida
solo con los integrantes** (no "cualquiera con el enlace"), manteniendo
los `README` con la atribución. Quien los recibe los descomprime en
`data/raw/<carpeta>/` y corre `--check` para confirmar que están
completos. **SKU-110K no se comparte** (su licencia prohíbe
redistribuirlo): cada integrante lo descarga con el script.

## Qué hacer con estos datasets (proceso)

1. **Verificar licencia antes de descargar.** Todos deben permitir uso
   académico/no comercial. SKU-110K lo permite explícitamente pero
   prohíbe redistribución: no subir las imágenes a este repo ni a
   ningún servicio externo, solo referenciarlas por URL.
2. **Descargar a `data/raw/<nombre-dataset>/`**, nunca a la raíz del
   repo. Esa carpeta está en `.gitignore`, así que no se versiona.
3. **Estandarizar anotaciones** al formato definido en `CLAUDE.md`:
   `[x_min, y_min, x_max, y_max]` en píxeles absolutos. Cada dataset
   trae su propio formato (XML, CSV, JSON de Roboflow, YOLO txt) y debe
   convertirse con un script dedicado antes de entrar al pipeline.
4. **Separar en `train/val/test`** de forma reproducible (semilla fija)
   y documentar la proporción usada.
5. **Guardar solo metadatos/scripts de descarga en Git**, no las
   imágenes: cada dataset nuevo se agrega al catálogo de
   `src/datasets/sources.py` (lo usa `scripts/download_datasets.py`),
   para que cualquier integrante lo reproduzca sin subir binarios
   pesados al repositorio.
6. **Nunca mezclar con el Dataset Oculto de Walmart Chile.** Estos
   datasets públicos son solo para entrenamiento/validación interna; el
   dataset oculto se reserva exclusivamente para la evaluación ciega
   final (ver README, sección "Estrategia de Datos y Evaluación"). Como
   Walmart no comparte imágenes de sus cámaras, esa evaluación solo
   puede correrla Walmart en sus instalaciones; sus imágenes nunca
   llegan al equipo.
7. **Registrar en este archivo** cualquier dataset nuevo que se agregue,
   junto con su licencia y el motivo de uso.
