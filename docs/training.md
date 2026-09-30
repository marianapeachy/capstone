# Entrenamiento del detector YOLO26 (ítem #5)

Fine-tuning de YOLO26 sobre SKU-110K y comparación de dos variantes:
`yolo26s` y `yolo26s-p2` (cabeza extra P2 para objetos chicos). Los pesos
COCO de Ultralytics no tienen una clase "producto", así que sin este paso
el detector no sirve para góndolas.

Se entrena en un PC con GPU NVIDIA. En CPU, una sola época de SKU-110K a
1280 px tarda horas, y hacen falta decenas.

## Requisitos del PC

- GPU NVIDIA con 8 GB de VRAM o más, y el driver actualizado.
- ~30 GB libres: SKU-110K ocupa 12.2 GB descomprimido. El dataset YOLO
  enlaza las imágenes en vez de copiarlas y solo copia los ~700 JPEG
  truncados (~2 GB).
- Python 3.10 o superior y git.

## 1. Entorno

```bash
git clone https://github.com/marianapeachy/capstone.git && cd capstone
git switch feat/yolo26-detector   # mientras el PR no esté mergeado en main
python -m venv .venv              # activar: .venv\Scripts\activate (Windows) / source .venv/bin/activate
pip install -r requirements.txt
```

En Windows, `pip install -r requirements.txt` instala PyTorch **sin CUDA**.
Hay que reinstalarlo con el comando que da el selector de
[pytorch.org/get-started](https://pytorch.org/get-started/locally/)
(Pip + la versión de CUDA más alta que soporte el driver), agregando
`--force-reinstall`:

```bash
pip install --force-reinstall torch torchvision --index-url <URL que indique el selector>
python -c "import torch; print(torch.__version__, torch.cuda.is_available(), torch.cuda.get_device_name(0))"
```

La última línea debe mostrar `True` y el nombre de la GPU. En Linux, el
PyTorch de PyPI ya trae CUDA.

## 2. Datos

```bash
python scripts/download_datasets.py --dataset sku110k   # 12.2 GB; si se corta, repetir (se reanuda)
python scripts/prepare_datasets.py --dataset sku110k    # anotaciones al formato estándar
python scripts/prepare_yolo_dataset.py                  # data/processed/yolo/sku110k/data.yaml
```

SKU-110K se descarga desde su URL original. No se sube a otro servicio ni
se pasa entre integrantes (su licencia lo prohíbe; ver `docs/datasets.md`).

## 3. Prueba corta (1-2 minutos)

Sirve para confirmar que CUDA y los datos funcionan antes del entrenamiento
largo:

```bash
python scripts/prepare_yolo_dataset.py --limit 16
python scripts/train_detector.py train --variant yolo26n --data data/processed/yolo/sku110k-limit16/data.yaml --epochs 1 --imgsz 640 --name smoke
```

## 4. Entrenar las dos variantes

```bash
python scripts/train_detector.py train --variant yolo26s
python scripts/train_detector.py train --variant yolo26s-p2
```

- Por defecto: 50 épocas, `imgsz=1280`, y se detiene si pasan 15 épocas
  sin mejorar. El batch se ajusta solo a ~60% de la VRAM (`--batch -1`).
  Si se queda sin memoria, fijarlo a mano (`--batch 4`).
- Cada corrida queda en `data/processed/training/<variante>/`. Ahí,
  `results.csv` va registrando las métricas por época; la primera época da
  una estimación del tiempo total.
- Si se corta (por un corte de luz, un reinicio o un Ctrl+C), se continúa
  donde quedó:
  `python scripts/train_detector.py resume data/processed/training/yolo26s`.
- El entrenamiento y la validación usan `nms=False` y `max_det=1000`, igual
  que la inferencia del pipeline (`src/models/detector.py`). Con los
  valores por defecto, Ultralytics mediría la cabeza con NMS y cortaría en
  300 cajas por imagen, y `best.pt` saldría de otro modelo.

## 5. Comparar y elegir

```bash
python scripts/train_detector.py val --weights data/processed/training/yolo26s/weights/best.pt
python scripts/train_detector.py val --weights data/processed/training/yolo26s-p2/weights/best.pt
```

Cada comando guarda `val-val/metrics.json` en la carpeta de su corrida. Se
elige con el split `val`, mirando primero `map50_95` (la métrica estándar
de SKU-110K) y después `recall` (un producto no detectado se contaría como
espacio vacío). Solo la variante ganadora se evalúa una vez en `test`
(`--split test`). El split `test` no se usa para elegir.

## 6. Entregar

- Los pesos (`best.pt`) **no se versionan** (`*.pt` está en `.gitignore`).
  Se comparten por una carpeta de Drive/OneDrive compartida solo con los
  integrantes. Por venir de SKU-110K, su uso es académico y no comercial.
- Registrar en el ítem #5 de `PROGRESS.md` las métricas de ambas variantes
  en `val`, la ganadora y su resultado en `test`, junto con la GPU, las
  épocas y el tiempo de entrenamiento.
