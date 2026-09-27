"""CLI de preparacion de datasets: convierte las anotaciones de cada
dataset descargado en data/raw/ al formato estandar del proyecto
(ver CLAUDE.md) y las deja en data/processed/annotations/.

Uso:
    python scripts/prepare_datasets.py            # convierte todos los disponibles
    python scripts/prepare_datasets.py --dataset sku110k
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.datasets.converters import (  # noqa: E402
    class_group,
    clip_bbox,
    coco_bbox_to_xyxy,
    polyline_to_bbox,
    sku110k_row_to_bbox,
    supervisely_rect_to_xyxy,
)

DATA_RAW = Path(__file__).resolve().parent.parent / "data" / "raw"
DATA_PROCESSED = Path(__file__).resolve().parent.parent / "data" / "processed"
ANNOTATIONS_OUT = DATA_PROCESSED / "annotations"

CSV_COLUMNS = [
    "dataset",
    "split",
    "image_path",
    "img_width",
    "img_height",
    "class_name",
    "class_group",
    "x_min",
    "y_min",
    "x_max",
    "y_max",
]


def convert_unidatapro() -> list[dict]:
    dataset_dir = DATA_RAW / "grocery-shelves-unidatapro"
    xml_path = dataset_dir / "annotations.xml"
    if not xml_path.exists():
        return []

    records = []
    root = ET.parse(xml_path).getroot()
    for image_el in root.findall("image"):
        name = image_el.get("name", "")
        width = float(image_el.get("width", 0))
        height = float(image_el.get("height", 0))
        image_path = f"img/{Path(name).name}"

        for polyline_el in image_el.findall("polyline"):
            if polyline_el.get("label") != "Box":
                continue
            bbox = polyline_to_bbox(polyline_el.get("points", ""))
            x_min, y_min, x_max, y_max = clip_bbox(bbox, width, height)
            records.append(
                {
                    "dataset": "unidatapro",
                    "split": "sample",
                    "image_path": image_path,
                    "img_width": width,
                    "img_height": height,
                    "class_name": "Box",
                    "class_group": class_group("unidatapro", "Box"),
                    "x_min": x_min,
                    "y_min": y_min,
                    "x_max": x_max,
                    "y_max": y_max,
                }
            )
    return records


def convert_kaggle_supermarket() -> list[dict]:
    dataset_dir = DATA_RAW / "supermarket-shelves" / "Supermarket shelves"
    ann_dir = dataset_dir / "annotations"
    if not ann_dir.exists():
        return []

    records = []
    for ann_path in sorted(ann_dir.glob("*.json")):
        data = json.loads(ann_path.read_text(encoding="utf-8"))
        width = float(data["size"]["width"])
        height = float(data["size"]["height"])
        image_path = f"images/{ann_path.name.removesuffix('.json')}"

        for obj in data.get("objects", []):
            if obj.get("geometryType") != "rectangle":
                continue
            class_name = obj.get("classTitle", "unknown")
            bbox = supervisely_rect_to_xyxy(obj["points"]["exterior"])
            x_min, y_min, x_max, y_max = clip_bbox(bbox, width, height)
            records.append(
                {
                    "dataset": "kaggle_supermarket",
                    "split": "all",
                    "image_path": image_path,
                    "img_width": width,
                    "img_height": height,
                    "class_name": class_name,
                    "class_group": class_group("kaggle_supermarket", class_name),
                    "x_min": x_min,
                    "y_min": y_min,
                    "x_max": x_max,
                    "y_max": y_max,
                }
            )
    return records


def convert_sku110k() -> list[dict]:
    ann_dir = DATA_RAW / "sku-110k" / "SKU110K_fixed" / "annotations"
    if not ann_dir.exists():
        return []

    records = []
    for split in ("train", "val", "test"):
        csv_path = ann_dir / f"annotations_{split}.csv"
        if not csv_path.exists():
            continue
        with csv_path.open(newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            for row in reader:
                filename, x1, y1, x2, y2, cls, width, height = row
                width_f, height_f = float(width), float(height)
                bbox = sku110k_row_to_bbox(float(x1), float(y1), float(x2), float(y2))
                x_min, y_min, x_max, y_max = clip_bbox(bbox, width_f, height_f)
                records.append(
                    {
                        "dataset": "sku110k",
                        "split": split,
                        "image_path": f"images/{filename}",
                        "img_width": width_f,
                        "img_height": height_f,
                        "class_name": cls,
                        "class_group": class_group("sku110k", cls),
                        "x_min": x_min,
                        "y_min": y_min,
                        "x_max": x_max,
                        "y_max": y_max,
                    }
                )
    return records


def convert_roboflow_coco(dataset_dir: Path, dataset_key: str) -> list[dict]:
    if not dataset_dir.exists():
        return []

    records = []
    for split_dir in sorted(p for p in dataset_dir.iterdir() if p.is_dir()):
        ann_path = split_dir / "_annotations.coco.json"
        if not ann_path.exists():
            continue
        data = json.loads(ann_path.read_text(encoding="utf-8"))
        categories = {c["id"]: c["name"] for c in data["categories"]}
        images = {img["id"]: img for img in data["images"]}

        for ann in data["annotations"]:
            image = images[ann["image_id"]]
            width, height = float(image["width"]), float(image["height"])
            class_name = categories.get(ann["category_id"], "unknown")
            bbox = coco_bbox_to_xyxy(ann["bbox"])
            x_min, y_min, x_max, y_max = clip_bbox(bbox, width, height)
            records.append(
                {
                    "dataset": dataset_key,
                    "split": split_dir.name,
                    "image_path": f"{split_dir.name}/{image['file_name']}",
                    "img_width": width,
                    "img_height": height,
                    "class_name": class_name,
                    "class_group": class_group(dataset_key, class_name),
                    "x_min": x_min,
                    "y_min": y_min,
                    "x_max": x_max,
                    "y_max": y_max,
                }
            )
    return records


CONVERTERS = {
    "unidatapro": convert_unidatapro,
    "kaggle_supermarket": convert_kaggle_supermarket,
    "sku110k": convert_sku110k,
    "roboflow_out_of_stock": lambda: convert_roboflow_coco(
        DATA_RAW / "out-of-stock-detection-roboflow", "roboflow_out_of_stock"
    ),
    "roboflow_empty_shelf": lambda: convert_roboflow_coco(
        DATA_RAW / "empty-shelf-detector-roboflow", "roboflow_empty_shelf"
    ),
}


def write_csv(records: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        writer.writerows(records)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dataset",
        choices=["all", *CONVERTERS.keys()],
        default="all",
        help="Dataset a convertir (default: all)",
    )
    args = parser.parse_args()

    keys = CONVERTERS.keys() if args.dataset == "all" else [args.dataset]
    all_records: list[dict] = []

    for key in keys:
        records = CONVERTERS[key]()
        if not records:
            print(f"[{key}] sin datos (no descargado o vacio) - se omite")
            continue
        write_csv(records, ANNOTATIONS_OUT / f"{key}.csv")
        print(f"[{key}] {len(records)} anotaciones -> data/processed/annotations/{key}.csv")
        all_records.extend(records)

    if all_records:
        write_csv(all_records, ANNOTATIONS_OUT / "all_annotations.csv")
        print(f"[all] {len(all_records)} anotaciones -> data/processed/annotations/all_annotations.csv")


if __name__ == "__main__":
    main()
