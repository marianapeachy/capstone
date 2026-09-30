"""Arma SKU-110K en el formato de entrenamiento de Ultralytics a partir de
las anotaciones estandar (salida de scripts/prepare_datasets.py).

Deja en data/processed/yolo/<nombre>/ las carpetas images/<split> y
labels/<split> y el data.yaml que recibe scripts/train_detector.py. Las
imagenes se enlazan (hard link) desde data/raw/ en vez de copiarse; se
copian los JPEG truncados (Ultralytics los reescribe al repararlos) y
todas si el sistema de archivos no permite enlaces.

Uso:
    python scripts/prepare_datasets.py --dataset sku110k   # requisito
    python scripts/prepare_yolo_dataset.py                 # SKU-110K completo
    python scripts/prepare_yolo_dataset.py --limit 16      # subconjunto para pruebas rapidas
"""

from __future__ import annotations

import argparse
import csv
import os
import shutil
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.datasets.converters import xyxy_to_yolo  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
ANNOTATIONS_CSV = ROOT / "data" / "processed" / "annotations" / "sku110k.csv"
IMAGES_ROOT = ROOT / "data" / "raw" / "sku-110k" / "SKU110K_fixed"
YOLO_OUT = ROOT / "data" / "processed" / "yolo"
SPLITS = ("train", "val", "test")
CLASS_NAME = "product"


def read_labels(csv_path: Path) -> tuple[dict[str, dict[str, list[str]]], int]:
    """Lineas de etiqueta YOLO por split e imagen, y cuantas cajas se
    descartaron por quedar sin area."""
    labels: dict[str, dict[str, list[str]]] = {split: defaultdict(list) for split in SPLITS}
    dropped = 0
    with csv_path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["class_group"] != CLASS_NAME or row["split"] not in labels:
                continue
            bbox = (float(row["x_min"]), float(row["y_min"]), float(row["x_max"]), float(row["y_max"]))
            yolo = xyxy_to_yolo(bbox, float(row["img_width"]), float(row["img_height"]))
            if yolo is None:
                dropped += 1
                continue
            labels[row["split"]][row["image_path"]].append("0 {:.6f} {:.6f} {:.6f} {:.6f}".format(*yolo))
    return labels, dropped


def is_truncated_jpeg(path: Path) -> bool:
    """JPEG sin el marcador de fin (FFD9); SKU-110K trae ~700. Ultralytics
    los repara reescribiendo el archivo en su lugar, asi que un hard link
    terminaria modificando el original de data/raw/."""
    if path.suffix.lower() not in {".jpg", ".jpeg"}:
        return False
    with path.open("rb") as f:
        f.seek(-2, os.SEEK_END)
        return f.read() != b"\xff\xd9"


def place_image(src: Path, dst: Path) -> bool:
    """Enlaza `src` en `dst` (hard link), o lo copia si es un JPEG truncado
    o si el sistema de archivos no permite enlaces. Devuelve True si copio."""
    if dst.exists():
        return False
    if not is_truncated_jpeg(src):
        try:
            os.link(src, dst)
            return False
        except OSError:
            pass
    shutil.copy2(src, dst)
    return True


def write_data_yaml(out_dir: Path) -> Path:
    yaml_path = out_dir / "data.yaml"
    lines = [f"path: {out_dir.resolve().as_posix()}"]
    lines += [f"{split}: images/{split}" for split in SPLITS]
    lines += ["names:", f"  0: {CLASS_NAME}", ""]
    yaml_path.write_text("\n".join(lines), encoding="utf-8")
    return yaml_path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--limit", type=int, help="maximo de imagenes por split (para pruebas rapidas)")
    args = parser.parse_args()

    if not ANNOTATIONS_CSV.exists():
        sys.exit(f"No existe {ANNOTATIONS_CSV}: corre primero scripts/prepare_datasets.py --dataset sku110k")

    out_dir = YOLO_OUT / ("sku110k" if args.limit is None else f"sku110k-limit{args.limit}")
    labels, dropped = read_labels(ANNOTATIONS_CSV)
    copied = 0
    for split in SPLITS:
        images = sorted(labels[split])[: args.limit]
        image_dir = out_dir / "images" / split
        label_dir = out_dir / "labels" / split
        image_dir.mkdir(parents=True, exist_ok=True)
        # Las etiquetas se regeneran completas para no dejar archivos de una corrida anterior.
        shutil.rmtree(label_dir, ignore_errors=True)
        label_dir.mkdir(parents=True)
        for image_path in images:
            name = Path(image_path).name
            copied += place_image(IMAGES_ROOT / image_path, image_dir / name)
            (label_dir / name).with_suffix(".txt").write_text("\n".join(labels[split][image_path]) + "\n", encoding="utf-8")
        boxes = sum(len(labels[split][i]) for i in images)
        print(f"[{split}] {len(images)} imagenes, {boxes} cajas")

    yaml_path = write_data_yaml(out_dir)
    if dropped:
        print(f"{dropped} cajas descartadas por quedar sin area dentro de la imagen")
    if copied:
        print(f"{copied} imagenes copiadas en vez de enlazadas (JPEG truncados o sin soporte de hard links)")
    print(f"dataset listo: {yaml_path.relative_to(ROOT).as_posix()}")


if __name__ == "__main__":
    main()
