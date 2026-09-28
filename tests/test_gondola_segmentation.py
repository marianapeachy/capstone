import math

import cv2
import numpy as np
import pytest

from src.preprocessing.gondola_segmentation import (
    GondolaSegmentation,
    SegmentationParams,
    ShelfLine,
    segment_gondola,
)

HEIGHT, WIDTH = 600, 800
CEILING_END = 60  # techo liso sobre la gondola
LIPS = [150, 290, 430, 540]  # borde superior de cada repisa (donde se apoyan productos)
LIP_THICKNESS = 12


def _gondola() -> tuple[np.ndarray, list[tuple[int, int, int, int]]]:
    """Gondola sintetica de frente: techo y piso lisos, cuatro repisas
    blancas y productos de colores (con 'texto') apoyados en cada una.
    Devuelve la imagen BGR y los bboxes de los productos."""
    rng = np.random.default_rng(0)
    image = np.full((HEIGHT, WIDTH, 3), 90, dtype=np.uint8)  # fondo del estante
    image[:CEILING_END] = 200
    image[LIPS[-1] + LIP_THICKNESS :] = 170  # piso
    products = []
    previous_lip_bottom = CEILING_END + 10
    for lip in LIPS:
        x = 5
        while x < WIDTH - 60:
            width = int(rng.integers(35, 60))
            top = max(previous_lip_bottom + 5, lip - int(rng.integers(60, 110)))
            color = tuple(int(c) for c in rng.integers(40, 220, size=3))
            cv2.rectangle(image, (x, top), (x + width, lip - 1), color, -1)
            for text_y in range(top + 8, lip - 8, 9):  # texto del empaque
                cv2.line(image, (x + 5, text_y), (x + width - 5, text_y), (20, 20, 20), 1)
            products.append((x, top, x + width, lip))
            x += width + int(rng.integers(3, 12))
        image[lip : lip + LIP_THICKNESS] = 245
        previous_lip_bottom = lip + LIP_THICKNESS
    return image, products


def _rotate(image: np.ndarray, degrees: float) -> np.ndarray:
    matrix = cv2.getRotationMatrix2D((WIDTH / 2, HEIGHT / 2), degrees, 1.0)
    return cv2.warpAffine(image, matrix, (WIDTH, HEIGHT), borderMode=cv2.BORDER_REPLICATE)


def _line_heights(segmentation: GondolaSegmentation, scale: float = 1.0) -> list[float]:
    return [line.y_at(WIDTH * scale / 2) / scale for line in segmentation.shelf_lines]


# Bordes horizontales esperados: el borde superior de la gondola (fin del
# techo) y el de cada repisa.
EDGES = [CEILING_END, *LIPS]


def test_detects_gondola_top_and_each_shelf_edge():
    image, _ = _gondola()
    result = segment_gondola(image)
    assert result.found
    heights = _line_heights(result)
    assert len(heights) == len(EDGES)
    for detected, edge in zip(heights, EDGES):
        assert detected == pytest.approx(edge, abs=LIP_THICKNESS + 3)


def test_roi_contains_products_and_excludes_ceiling_and_floor():
    image, products = _gondola()
    x_min, y_min, x_max, y_max = segment_gondola(image).roi
    for px_min, py_min, px_max, py_max in products:
        assert x_min <= px_min and px_max <= x_max
        # Los productos se apoyan sobre la linea: su base puede quedar un
        # pixel bajo el borde detectado.
        assert y_min <= py_min and py_max <= y_max + 2
    assert y_min >= CEILING_END - 5  # el techo liso queda fuera
    assert y_max <= LIPS[-1] + LIP_THICKNESS + 10  # el piso liso queda fuera


def test_one_shelf_level_per_row_of_products_in_order():
    image, _ = _gondola()
    result = segment_gondola(image)
    assert len(result.shelves) == len(LIPS)
    tops = [shelf[1] for shelf in result.shelves]
    assert tops == sorted(tops)
    x_min, y_min, x_max, y_max = result.roi
    for sx_min, sy_min, sx_max, sy_max in result.shelves:
        assert x_min <= sx_min < sx_max <= x_max and y_min <= sy_min < sy_max <= y_max


def test_follows_shelves_tilted_by_perspective():
    image, _ = _gondola()
    result = segment_gondola(_rotate(image, 3.0))
    assert len(result.shelf_lines) >= len(LIPS)
    for line in result.shelf_lines:
        # cv2 rota en sentido antihorario: en coordenadas de imagen, pendiente negativa.
        assert math.degrees(math.atan(-line.slope)) == pytest.approx(3.0, abs=1.0)


def test_large_images_return_coordinates_of_the_input_image():
    image, _ = _gondola()
    large = cv2.resize(image, None, fx=2.5, fy=2.5, interpolation=cv2.INTER_NEAREST)
    result = segment_gondola(large)
    heights = _line_heights(result, scale=2.5)
    assert len(heights) == len(EDGES)
    for detected, edge in zip(heights, EDGES):
        assert detected == pytest.approx(edge, abs=LIP_THICKNESS + 3)
    assert result.roi[2] <= large.shape[1] and result.roi[3] <= large.shape[0]


def test_without_shelves_falls_back_to_full_image():
    result = segment_gondola(np.full((HEIGHT, WIDTH, 3), 128, dtype=np.uint8))
    assert result == GondolaSegmentation(
        roi=(0, 0, WIDTH, HEIGHT), shelf_lines=(), shelves=(), found=False
    )


def test_accepts_grayscale_images():
    image, _ = _gondola()
    result = segment_gondola(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY))
    assert len(result.shelf_lines) == len(EDGES)


def test_rejects_none_image():
    with pytest.raises(ValueError, match="None"):
        segment_gondola(None)


def test_shelf_line_evaluates_its_equation():
    line = ShelfLine(x_min=0, x_max=100, slope=0.1, intercept=50)
    assert line.y_at(20) == pytest.approx(52)
    assert line.y_range(0, 100) == pytest.approx((50, 60))


def _staircase_and_shelf() -> np.ndarray:
    """Fondo con ruido, una repisa real de lado a lado (y=400) y una
    'escalera' de barras cortas, una por franja y cada una mas abajo: en
    cada franja hay un salto, y los saltos quedan alineados en una recta
    inclinada que en realidad cruza zonas sin borde (como una diagonal
    falsa que salta entre bordes de productos)."""
    rng = np.random.default_rng(1)
    image = rng.normal(90, 6, size=(HEIGHT, WIDTH)).clip(0, 255).astype(np.uint8)
    image[400:412] = 245
    strip_width = WIDTH / SegmentationParams().strips
    for strip in range(SegmentationParams().strips):
        center = (strip + 0.5) * strip_width
        top = 150 + 15 * strip
        image[top : top + 12, int(center - strip_width / 4) : int(center + strip_width / 4)] = 245
    return image


def test_rejects_lines_without_edge_along_their_whole_length():
    image = _staircase_and_shelf()
    heights = [line.y_at(WIDTH / 2) for line in segment_gondola(image).shelf_lines]
    assert heights == [pytest.approx(400, abs=LIP_THICKNESS + 3)]
    # Sin exigir borde a lo largo de la recta, la escalera sale como repisa.
    unchecked = segment_gondola(image, SegmentationParams(min_support=0.0))
    assert len(unchecked.shelf_lines) == 2


def test_ignores_edges_too_close_to_the_top_of_the_image():
    # Un borde a 2% del alto: una repisa cuyos productos quedan fuera de
    # cuadro (o el borde de la foto), sin espacio para un nivel encima.
    image, _ = _gondola()
    image[:12] = 20  # franja oscura sobre el techo claro: salto fuerte en y=12
    heights = _line_heights(segment_gondola(image))
    assert all(h > 0.07 * HEIGHT for h in heights)
    assert len(heights) == len(EDGES)


def test_roi_covers_products_beyond_partial_shelf_lines():
    # El tercio derecho es textura sin ningun borde horizontal (franjas
    # verticales de colores, ej. repisas tapadas por productos altos): las
    # repisas solo se detectan a la izquierda, pero la ROI igual cubre la
    # gondola completa.
    image, _ = _gondola()
    right = WIDTH - 2 * WIDTH // 3
    stripes = np.random.default_rng(2).integers(40, 220, size=(right // 6 + 1, 3), dtype=np.uint8)
    image[:, -right:] = np.repeat(stripes, 6, axis=0)[:right]
    result = segment_gondola(image)
    assert result.shelf_lines
    assert all(line.x_max <= WIDTH - right + 1 for line in result.shelf_lines)
    assert result.roi[0] == 0 and result.roi[2] == WIDTH


def test_edge_near_the_top_still_bounds_the_roi():
    # El borde pegado arriba no es repisa, pero si limite de la gondola: el
    # nivel entre el y la primera repisa (ej. espacios vacios, sin textura)
    # queda dentro de la ROI.
    image, _ = _gondola()
    image[:12] = 20
    image[12:LIPS[0]] = 200  # nivel superior vacio (liso)
    result = segment_gondola(image)
    assert all(line.y_at(WIDTH / 2) > 0.07 * HEIGHT for line in result.shelf_lines)
    assert result.roi[1] <= 15
