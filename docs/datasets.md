# Datasets - ShelfVision AI

Registro de datasets candidatos para entrenamiento y validación del
pipeline (preprocessing -> YOLOv8 -> postprocessing). Ninguno se versiona
en Git (ver `.gitignore`); se descargan a `data/raw/` en el entorno local
de cada integrante.

## Ya identificados por el equipo

| Dataset | Fuente | Contenido | Licencia | Estado |
| --- | --- | --- | --- | --- |
| [grocery-shelves](https://huggingface.co/datasets/UniDataPro/grocery-shelves) | Hugging Face (UniDataPro) | **Solo 15 imágenes de muestra** (+ máscaras de etiqueta) con `annotations.xml`. El "5000+" del README es material de marketing del dataset comercial completo que UniDataPro vende aparte; el repo público de HF es únicamente el sample gratuito. | `cc-by-nc-nd-4.0` (no comercial, sin derivados) | Descargado en `data/raw/grocery-shelves-unidatapro/` (71 MB) |
| [supermarket-shelves-dataset](https://www.kaggle.com/datasets/humansintheloop/supermarket-shelves-dataset) | Kaggle (humansintheloop) | Góndolas con anotación de producto y precio | Verificar licencia Kaggle del dataset | Ya instalado manualmente por el equipo |

## Adicionales recomendados

| Dataset | Fuente | Por qué aporta valor | Licencia | Estado |
| --- | --- | --- | --- | --- |
| [SKU-110K](https://docs.ultralytics.com/datasets/detect/sku-110k/) | [Trax Retail / eg4000/SKU110K_CVPR19](https://github.com/eg4000/SKU110K_CVPR19) | Benchmark académico estándar (CVPR'19) para detección en góndolas densamente pobladas: 11,743 imágenes, 1.7M+ bounding boxes de producto en clase única. **Soporte nativo en Ultralytics** (YAML de config ya incluido en la librería YOLOv8/v11). Ideal para pre-entrenar/afinar el detector base antes del dataset oculto de Walmart Chile. | Académico y no comercial, sin redistribución | Descargado (12.2 GB) en `data/raw/sku-110k/SKU110K_fixed/` (train/val/test + anotaciones CSV) |
| [Out Of Stock detection](https://universe.roboflow.com/empty-space-detection-capstone/out-of-stock-detection) | Roboflow Universe | Anota directamente la clase **"Empty-space"**, no productos. Es el único dataset de la lista alineado 1:1 con RF02/RF03 (umbral `<30%`), en vez de inferir el vacío por ausencia de producto. | Ver ficha del proyecto en Roboflow | Descargado (346 MB, formato COCO) en `data/raw/out-of-stock-detection-roboflow/train/` (3024 imágenes, `_annotations.coco.json`). Solo trae split `train`, sin `valid`/`test` |
| [Empty Shelf Detector](https://universe.roboflow.com/fyp-ormnr/empty-shelf-detector) | Roboflow Universe | Complementa al anterior con más variabilidad de ángulos/iluminación en la misma clase "empty". | Ver ficha del proyecto en Roboflow | Descargado (31 MB, formato COCO) en `data/raw/empty-shelf-detector-roboflow/` (train: 291, valid: 24, test: 18 imágenes) |

> **Corrección:** el dataset "TrainingDataPro/grocery-shelves-dataset"
> reportado previamente **no existe** (confirmado vía API de Hugging Face:
> repo inexistente). Se descarta de la lista.

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
   imágenes: un script en `scripts/` (ej. `download_dataset.py`) que
   descarga y prepara cada dataset, para que cualquier integrante lo
   reproduzca sin subir binarios pesados al repositorio.
6. **Nunca mezclar con el Dataset Oculto de Walmart Chile.** Estos
   datasets públicos son solo para entrenamiento/validación interna; el
   dataset oculto se reserva exclusivamente para la evaluación ciega
   final (ver README, sección "Estrategia de Datos y Evaluación").
7. **Registrar en este archivo** cualquier dataset nuevo que se agregue,
   junto con su licencia y el motivo de uso.
