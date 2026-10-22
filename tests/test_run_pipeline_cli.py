import csv
import importlib.util
import json
from pathlib import Path

import cv2
import numpy as np
import pytest

from tests.pipeline_fixtures import ColorDetector, gondola

ROOT = Path(__file__).resolve().parent.parent
EMPTIED = {1: (0.15, 0.85), 2: (0.15, 0.85)}


@pytest.fixture
def cli(monkeypatch):
    spec = importlib.util.spec_from_file_location("run_pipeline", ROOT / "scripts" / "run_pipeline.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    monkeypatch.setattr(module, "make_detector", lambda weights, device: ColorDetector())
    return module


@pytest.fixture
def photos(tmp_path):
    folder = tmp_path / "fotos"
    folder.mkdir()
    full, _ = gondola()
    emptied, truth = gondola(EMPTIED)
    cv2.imwrite(str(folder / "a_llena.jpg"), full)
    cv2.imwrite(str(folder / "b_vacia.png"), emptied)
    weights = tmp_path / "best.pt"
    weights.write_bytes(b"pesos falsos")
    return folder, weights, truth


def _run(cli, *args) -> int:
    return cli.main([str(a) for a in args])


def test_folder_with_two_photos_writes_a_view_and_a_json_per_photo(cli, photos, tmp_path, capsys):
    folder, weights, _ = photos
    out = tmp_path / "salida"
    assert _run(cli, folder, "--weights", weights, "--out", out) == 0
    assert sorted(p.name for p in out.iterdir()) == [
        "a_llena.jpg", "a_llena.json", "b_vacia.jpg", "b_vacia.json"
    ]
    assert json.loads((out / "b_vacia.json").read_text(encoding="utf-8"))["critical"] is True
    assert json.loads((out / "a_llena.json").read_text(encoding="utf-8"))["critical"] is False
    table = capsys.readouterr().out
    assert "a_llena.jpg" in table and "b_vacia.png" in table and "mediana" in table


def test_without_photos_exits_with_code_2(cli, photos, tmp_path):
    _, weights, _ = photos
    empty = tmp_path / "vacia"
    empty.mkdir()
    assert _run(cli, empty, "--weights", weights, "--out", tmp_path / "salida") == 2


def test_without_weights_exits_with_code_2(cli, photos, tmp_path):
    folder, _, _ = photos
    assert _run(cli, folder, "--weights", tmp_path / "no_existe.pt", "--out", tmp_path / "s") == 2


def test_unreadable_photo_is_reported_and_the_rest_processed(cli, photos, tmp_path, capsys):
    folder, weights, _ = photos
    (folder / "c_rota.jpg").write_bytes(b"no es una imagen")
    out = tmp_path / "salida"
    assert _run(cli, folder, "--weights", weights, "--out", out) == 0
    assert not (out / "c_rota.json").exists()
    assert (out / "b_vacia.json").exists()
    assert "no se pudo leer" in capsys.readouterr().out


def test_photo_without_products_has_no_free_space_or_alert(cli, photos, tmp_path, capsys):
    # #52: sin detecciones no se informa % libre ni alerta (daría 100% libre y una alerta falsa).
    folder, weights, _ = photos
    cv2.imwrite(str(folder / "c_tapada.png"), np.full((600, 800, 3), 90, np.uint8))
    out = tmp_path / "salida"
    assert _run(cli, folder, "--weights", weights, "--out", out) == 0
    assert not (out / "c_tapada.json").exists() and not (out / "c_tapada.jpg").exists()
    assert (out / "b_vacia.json").exists()
    assert "sin productos detectados" in capsys.readouterr().out


def test_annotations_produce_iou_and_alert_metrics(cli, photos, tmp_path):
    folder, weights, truth = photos
    annotations = tmp_path / "anotaciones.csv"
    with annotations.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["dataset", "split", "image_path", "img_width", "img_height",
                         "class_name", "class_group", "x_min", "y_min", "x_max", "y_max"])
        for box in truth:
            writer.writerow(["prueba", "all", "otra/carpeta/b_vacia.png", 800, 600,
                             "Product", "product", *box])
        writer.writerow(["prueba", "all", "b_vacia.png", 800, 600, "Empty", "empty", 1, 1, 50, 50])
    out = tmp_path / "salida"
    assert _run(cli, folder, "--weights", weights, "--out", out, "--annotations", annotations) == 0
    with (out / "metrics.csv").open(encoding="utf-8") as f:
        rows = {row["image"]: row for row in csv.DictReader(f)}
    assert set(rows) == {"b_vacia.png", "total"}  # a_llena no tiene anotacion
    image = rows["b_vacia.png"]
    assert float(image["precision"]) == 1.0 and float(image["recall"]) == 1.0
    assert int(image["annotated"]) == len(truth)  # la caja "empty" no cuenta
    assert image["alert_matches"] == "True"
    assert float(rows["total"]["alert_accuracy"]) == 1.0
