"""Arma el dataset del fine-tuning del detector (item #33 de PROGRESS.md).

Entrenamiento: 24 fotos de Kaggle supermarket-shelves (CC0) reducidas a
2560 px, mas sus vistas giradas a 20 y 35 grados (15 grados hacia abajo,
oblique_view()), y N fotos de SKU-110K `train` para no olvidar (SKU-110K
no se modifica: solo se enlaza). Validacion: 12 fotos de Kaggle separadas
por foto, de frente y giradas, en carpetas por angulo para medir cada una
con `train_detector.py val --data data-<angulo>.yaml`.

Uso:
    python scripts/prepare_finetune_dataset.py [--sku-images 300]
"""

from __future__ import annotations

import argparse
import csv
import random
import shutil
import sys
from collections import defaultdict
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.datasets.converters import xyxy_to_yolo  # noqa: E402
from src.datasets.synthetic import oblique_view  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from prepare_yolo_dataset import IMAGES_ROOT, YOLO_OUT, place_image, read_labels  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
KAGGLE_CSV = ROOT / "data" / "processed" / "annotations" / "kaggle_supermarket.csv"
KAGGLE_IMAGES = ROOT / "data" / "raw" / "supermarket-shelves" / "Supermarket shelves"
SKU_CSV = ROOT / "data" / "processed" / "annotations" / "sku110k.csv"
OUT = YOLO_OUT / "finetune"

MAX_SIDE = 2560
# nombre de la vista -> (giro, giro hacia abajo); mismas vistas que AV-06 de docs/test-plan.md.
ANGLES = {"f": (0, 0), "y20": (20, -15), "y35": (35, -15)}
# Frutas y verduras sueltas: fuera del alcance (#34). La 035 repite la 004.
OUT_OF_SCOPE = ("005", "007", "014", "023", "029", "030", "033", "034", "035")
TEST_PHOTOS = ("001", "004", "009", "012", "016", "019", "022", "026", "031", "037", "040", "043")
TRAIN_PHOTOS = tuple(
    f"{i:03d}" for i in range(1, 46) if f"{i:03d}" not in OUT_OF_SCOPE + TEST_PHOTOS
)


def views(image: np.ndarray, boxes: np.ndarray, max_side: int = MAX_SIDE) -> list[tuple[str, np.ndarray, np.ndarray]]:
    """La foto reducida a `max_side` y sus vistas giradas, con las cajas
    [x_min, y_min, x_max, y_max] transformadas."""
    scale = max_side / max(image.shape[:2])
    if scale < 1:
        image = cv2.resize(image, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
        boxes = boxes * scale
    return [
        (name, *(oblique_view(image, boxes, yaw, pitch) if yaw else (image, boxes)))
        for name, (yaw, pitch) in ANGLES.items()
    ]


def write_view(image: np.ndarray, boxes: np.ndarray, stem: str, image_dir: Path, label_dir: Path) -> None:
    height, width = image.shape[:2]
    lines = []
    for box in boxes:
        if yolo := xyxy_to_yolo(tuple(box), width, height):
            lines.append("0 {:.6f} {:.6f} {:.6f} {:.6f}".format(*yolo))
    cv2.imwrite(str(image_dir / f"{stem}.jpg"), image, [cv2.IMWRITE_JPEG_QUALITY, 95])
    (label_dir / f"{stem}.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


def read_kaggle() -> dict[str, np.ndarray]:
    boxes = defaultdict(list)
    with KAGGLE_CSV.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["class_group"] == "product":
                boxes[Path(row["image_path"]).stem].append([float(row[k]) for k in ("x_min", "y_min", "x_max", "y_max")])
    return {photo: np.array(b) for photo, b in boxes.items()}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--sku-images", type=int, default=300, help="fotos de SKU-110K train para no olvidar")
    args = parser.parse_args()

    shutil.rmtree(OUT, ignore_errors=True)
    kaggle = read_kaggle()
    groups = {"train": TRAIN_PHOTOS, **{f"val-{name}": TEST_PHOTOS for name in ANGLES}}
    for folder in groups:
        (OUT / "images" / folder).mkdir(parents=True)
        (OUT / "labels" / folder).mkdir(parents=True)
    for split, photos in (("train", TRAIN_PHOTOS), ("val", TEST_PHOTOS)):
        for photo in photos:
            image = cv2.imread(str(KAGGLE_IMAGES / "images" / f"{photo}.jpg"))
            for name, img, boxes in views(image, kaggle[photo]):
                folder = "train" if split == "train" else f"val-{name}"
                write_view(img, boxes, f"kaggle_{photo}_{name}", OUT / "images" / folder, OUT / "labels" / folder)

    sku, _ = read_labels(SKU_CSV)
    chosen = random.Random(0).sample(sorted(sku["train"]), args.sku_images)
    for image_path in chosen:
        name = Path(image_path).name
        place_image(IMAGES_ROOT / image_path, OUT / "images" / "train" / name)
        (OUT / "labels" / "train" / name).with_suffix(".txt").write_text("\n".join(sku["train"][image_path]) + "\n", encoding="utf-8")

    def yaml(val: list[str], path: Path) -> None:
        lines = [f"path: {OUT.resolve().as_posix()}", "train: images/train"]
        lines += ["val:"] + [f"  - images/{v}" for v in val] + ["names:", "  0: product", ""]
        path.write_text("\n".join(lines), encoding="utf-8")

    yaml([f"val-{n}" for n in ANGLES], OUT / "data.yaml")
    for name in ANGLES:
        yaml([f"val-{name}"], OUT / f"data-{name}.yaml")
    print(f"dataset listo: {OUT.relative_to(ROOT).as_posix()} ({len(TRAIN_PHOTOS) * 3} vistas Kaggle + {len(chosen)} SKU-110K)")


if __name__ == "__main__":
    main()
