from src.datasets.converters import (
    class_group,
    clip_bbox,
    coco_bbox_to_xyxy,
    polyline_to_bbox,
    sku110k_row_to_bbox,
    supervisely_rect_to_xyxy,
)


def test_polyline_to_bbox_returns_enclosing_rect():
    points = "8.24,430.94;212.74,429.60;228.40,637.40;21.50,645.90"
    x_min, y_min, x_max, y_max = polyline_to_bbox(points)
    assert x_min == 8.24
    assert y_min == 429.60
    assert x_max == 228.40
    assert y_max == 645.90


def test_coco_bbox_to_xyxy_converts_xywh():
    x_min, y_min, x_max, y_max = coco_bbox_to_xyxy([447, 10, 175, 100.938])
    assert (x_min, y_min) == (447, 10)
    assert x_max == 447 + 175
    assert y_max == 10 + 100.938


def test_supervisely_rect_to_xyxy_handles_unordered_points():
    exterior = [[286, 165], [4, 4]]
    assert supervisely_rect_to_xyxy(exterior) == (4, 4, 286, 165)


def test_sku110k_row_to_bbox_normalizes_order():
    assert sku110k_row_to_bbox(120, 2527, 225, 2764) == (120, 2527, 225, 2764)
    assert sku110k_row_to_bbox(225, 2764, 120, 2527) == (120, 2527, 225, 2764)


def test_clip_bbox_swaps_inverted_coordinates():
    assert clip_bbox((50, 50, 10, 10), width=100, height=100) == (10, 10, 50, 50)


def test_clip_bbox_clamps_to_image_bounds():
    assert clip_bbox((-20, -5, 150, 90), width=100, height=80) == (0, 0, 100, 80)


def test_class_group_maps_known_classes():
    assert class_group("unidatapro", "Box") == "product"
    assert class_group("roboflow_out_of_stock", "empty") == "empty_space"
    assert class_group("kaggle_supermarket", "Price") == "price"


def test_class_group_defaults_to_other_for_unknown_class():
    assert class_group("sku110k", "not-a-real-class") == "other"
    assert class_group("dataset-not-registered", "anything") == "other"
