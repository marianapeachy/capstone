from pathlib import Path

import pytest

from src.datasets.sources import (
    DATASETS,
    DatasetSource,
    ExpectedFiles,
    check_layout,
    huggingface_file_url,
    roboflow_export_url,
    safe_destination,
    strip_archive_root,
)

TINY = DatasetSource(
    key="tiny",
    folder="tiny",
    title="Dataset de prueba",
    license="CC0",
    shareable=True,
    method="archive",
    expected=(ExpectedFiles("images/*.jpg", 2), ExpectedFiles("labels.json", 1)),
)


def _touch(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"")


def test_catalog_keys_match_prepare_datasets_converters():
    # scripts/prepare_datasets.py usa estas mismas claves en --dataset.
    assert set(DATASETS) == {
        "unidatapro",
        "kaggle_supermarket",
        "sku110k",
        "roboflow_out_of_stock",
        "roboflow_empty_shelf",
    }
    for key, source in DATASETS.items():
        assert source.key == key
        assert source.expected, f"{key} sin archivos esperados"


def test_sku110k_is_not_shareable():
    # Su licencia prohibe redistribuirlo: cada integrante lo descarga.
    assert DATASETS["sku110k"].shareable is False


def test_check_layout_ok_when_counts_match(tmp_path):
    _touch(tmp_path / "images" / "a.jpg")
    _touch(tmp_path / "images" / "b.jpg")
    _touch(tmp_path / "labels.json")
    assert check_layout(tmp_path, TINY) == []


def test_check_layout_reports_missing_and_extra_files(tmp_path):
    _touch(tmp_path / "images" / "a.jpg")
    problems = check_layout(tmp_path, TINY)
    assert problems == [
        "images/*.jpg: 1 archivos, se esperaban 2",
        "labels.json: 0 archivos, se esperaban 1",
    ]


def test_check_layout_ignores_directories_matching_pattern(tmp_path):
    (tmp_path / "images" / "fake.jpg").mkdir(parents=True)
    _touch(tmp_path / "labels.json")
    assert check_layout(tmp_path, TINY) == ["images/*.jpg: 0 archivos, se esperaban 2"]


def test_check_layout_missing_folder(tmp_path):
    problems = check_layout(tmp_path / "no-existe", TINY)
    assert len(problems) == 1
    assert "no existe la carpeta" in problems[0]


def test_safe_destination_keeps_nested_paths_inside_base(tmp_path):
    dest = safe_destination(tmp_path, "Supermarket shelves/images/001.jpg")
    assert dest == tmp_path / "Supermarket shelves" / "images" / "001.jpg"


@pytest.mark.parametrize(
    "name",
    ["../evil.txt", "img/../../evil.txt", "/etc/passwd", "..\\evil.txt", "C:/evil.txt"],
)
def test_safe_destination_rejects_path_traversal(tmp_path, name):
    with pytest.raises(ValueError):
        safe_destination(tmp_path, name)


def test_strip_archive_root_removes_top_folder():
    root = "Supermarket shelves"
    assert (
        strip_archive_root("Supermarket shelves/Supermarket shelves/images/1.jpg", root)
        == "Supermarket shelves/images/1.jpg"
    )
    assert strip_archive_root("Supermarket shelves/meta.json", root) == "meta.json"


def test_strip_archive_root_skips_outside_entries_and_root_itself():
    assert strip_archive_root("otra/cosa.txt", "Supermarket shelves") is None
    assert strip_archive_root("Supermarket shelves/", "Supermarket shelves") is None


def test_strip_archive_root_without_root_keeps_name():
    assert strip_archive_root("train/a.jpg", "") == "train/a.jpg"


def test_huggingface_file_url_pins_revision_and_quotes_path():
    url = huggingface_file_url("UniDataPro/grocery-shelves", "abc123", "img/11 b.jpeg")
    assert url == (
        "https://huggingface.co/datasets/UniDataPro/grocery-shelves/resolve/abc123/img/11%20b.jpeg"
    )


def test_roboflow_export_url_encodes_api_key():
    url = roboflow_export_url("ws", "proj", 1, "k&y")
    assert url == "https://api.roboflow.com/ws/proj/1/coco?api_key=k%26y"
