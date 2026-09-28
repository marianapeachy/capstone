"""Segmentacion automatica de la gondola y sus repisas (vision clasica).

Corre sobre la imagen ya corregida por correct_image() y antes del
recorte de ROI (ver CLAUDE.md): ningun usuario define la ROI, la entrega
este modulo. Las coordenadas de salida estan en pixeles de la imagen que
recibe (la corregida); CorrectedImage.to_original() las lleva a la
original.

Metodo:
1. La imagen se divide en franjas verticales. En cada una se promedia el
   brillo por fila y se buscan los saltos bruscos de ese promedio: el
   borde frontal de una repisa cruza la franja entera, asi que su salto
   sobrevive al promedio, mientras que el texto y los bordes de productos
   individuales se cancelan. (Se probo antes con bordes de Canny y
   Hough: el texto de las etiquetas dominaba y cada fila de cajas
   aparecia como repisa.)
2. Los saltos se enlazan entre franjas vecinas; cada cadena que cruza al
   menos la mitad de las franjas es candidata a repisa. Por franjas, cada
   repisa puede tener su propia inclinacion (perspectiva).
3. Cada candidata debe tener borde a lo largo de toda su recta (subfranjas
   angostas donde el brillo promedio siguiendo la recta salta), no solo en
   los centros de franja: asi se descartan las diagonales falsas que
   enlazan saltos de repisas o productos distintos. Las que quedan son
   repisas (ShelfLine), salvo las pegadas al borde superior de la foto
   (sin espacio para productos encima), que solo limitan la gondola.
4. La ROI envuelve las repisas y se extiende de a un nivel sobre la
   primera y bajo la ultima, y de a una franja hacia los lados, mientras
   haya textura de producto: incluye niveles que la foto corta y repisas
   tapadas en parte, y se detiene en techo, piso o paredes lisos.

Medicion contra las repisas anotadas de SHARD: scripts/evaluate_shard.py
(ver PROGRESS.md, item #15).

Si no se detecta ninguna repisa se devuelve la imagen completa con
found=False: el pipeline puede seguir con el analisis global de la
gondola (plan de contingencia del umbral <30%).
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import cv2
import numpy as np

from src.preprocessing._validation import check_image

PixelBBox = tuple[int, int, int, int]


@dataclass(frozen=True)
class SegmentationParams:
    """Parametros del metodo. Las fracciones son relativas al ancho o alto
    de la imagen de trabajo, para no depender de la resolucion."""

    work_size: int = 1024  # lado mayor de la imagen de trabajo (solo se reduce)
    strips: int = 6  # franjas verticales en que se busca cada repisa
    min_edge: float = 0.35  # salto minimo, relativo al percentil 99 de la franja
    min_jump: float = 2.0  # piso de esa referencia (niveles de gris por pixel)
    min_spacing_frac: float = 0.07  # distancia minima entre repisas (del alto)
    max_tilt_deg: float = 8.0  # inclinacion maxima de una repisa
    min_strip_fraction: float = 0.5  # fraccion de franjas que debe cruzar una repisa
    max_residual_frac: float = 0.02  # desvio maximo de la recta ajustada (del alto)
    content_ratio: float = 0.5  # textura minima (vs. franjas interiores) de la franja superior/inferior
    support_substrips: int = 4  # subfranjas por franja en que se verifica el borde de cada repisa
    support_radius_frac: float = 0.01  # holgura vertical al buscar el borde sobre la recta (del alto)
    support_edge: float = 0.5  # salto minimo en una subfranja (misma escala que min_edge)
    min_support: float = 0.7  # fraccion de subfranjas con borde que exige una repisa (0 = no se exige)


@dataclass(frozen=True)
class ShelfLine:
    """Borde frontal de una repisa: recta y = slope * x + intercept entre
    x_min y x_max, en pixeles de la imagen segmentada."""

    x_min: float
    x_max: float
    slope: float
    intercept: float

    def y_at(self, x: float) -> float:
        return self.slope * x + self.intercept

    def y_range(self, x_min: float, x_max: float) -> tuple[float, float]:
        ys = (self.y_at(x_min), self.y_at(x_max))
        return min(ys), max(ys)


@dataclass(frozen=True)
class GondolaSegmentation:
    """ROI de la gondola, bordes de repisa (de arriba hacia abajo) y un bbox
    por nivel de repisa (de arriba hacia abajo, para el Nivel 1). Con
    found=False la ROI es la imagen completa y no hay repisas."""

    roi: PixelBBox
    shelf_lines: tuple[ShelfLine, ...]
    shelves: tuple[PixelBBox, ...]
    found: bool


def segment_gondola(
    image: np.ndarray | None, params: SegmentationParams = SegmentationParams()
) -> GondolaSegmentation:
    """Detecta la gondola y sus repisas en una imagen BGR o en escala de
    grises (ya corregida con correct_image())."""
    check_image(image)
    height, width = image.shape[:2]
    gray = image if image.ndim == 2 else cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    scale = min(1.0, params.work_size / max(height, width))
    if scale < 1.0:
        gray = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)

    edges = _detect_shelf_lines(gray, params)
    # Sobre una repisa se apoyan productos: a menos de la separacion minima
    # entre repisas del borde superior de la foto no queda espacio para
    # ellos (es el borde de la imagen o una repisa cuyos productos quedan
    # fuera de cuadro). Ese borde no se informa como repisa, pero si limita
    # la gondola: el nivel bajo el (ej. espacios vacios, sin textura) queda
    # en la ROI.
    min_top = params.min_spacing_frac * gray.shape[0]
    lines = [line for line in edges if line.y_at((line.x_min + line.x_max) / 2) >= min_top]
    bounds = _shelf_bounds(gray, edges, params) if lines else None
    if bounds is None:
        return GondolaSegmentation(
            roi=(0, 0, width, height), shelf_lines=(), shelves=(), found=False
        )

    x_min, x_max, levels = bounds
    shelves = tuple(
        _to_pixels((x_min, top, x_max, bottom), scale, width, height)
        for top, bottom in levels
    )
    roi = (
        min(s[0] for s in shelves),
        shelves[0][1],
        max(s[2] for s in shelves),
        shelves[-1][3],
    )
    shelf_lines = tuple(
        ShelfLine(
            x_min=line.x_min / scale,
            x_max=line.x_max / scale,
            slope=line.slope,
            intercept=line.intercept / scale,
        )
        for line in lines
    )
    return GondolaSegmentation(roi=roi, shelf_lines=shelf_lines, shelves=shelves, found=True)


def _detect_shelf_lines(gray: np.ndarray, params: SegmentationParams) -> list[ShelfLine]:
    """Busca, en cada franja vertical, los saltos del brillo promedio por
    fila y enlaza esos saltos entre franjas vecinas: cada cadena que cruza
    buena parte del ancho es una repisa."""
    height, width = gray.shape
    strip_width = width / params.strips
    min_spacing = params.min_spacing_frac * height
    sigma = max(1.0, 0.004 * height)

    peaks_per_strip, references = [], []
    for strip in range(params.strips):
        columns = gray[:, int(strip * strip_width) : int((strip + 1) * strip_width)]
        row_mean = _smooth(columns.astype(np.float32).mean(axis=1), sigma)
        jumps = np.abs(np.gradient(row_mean))
        # Relativo a la propia franja, para no depender de la iluminacion,
        # pero con un piso absoluto: en una franja casi lisa no se
        # amplifica el ruido hasta parecer una repisa.
        references.append(max(float(np.percentile(jumps, 99)), params.min_jump))
        jumps /= references[-1]
        peaks_per_strip.append(_profile_peaks(jumps, params.min_edge, min_spacing))

    max_step = math.tan(math.radians(params.max_tilt_deg)) * strip_width + min_spacing / 4
    chains: list[list[tuple[int, float]]] = []
    for strip, peaks in enumerate(peaks_per_strip):
        open_chains = [c for c in chains if strip - c[-1][0] <= 2]
        for y in peaks:
            best, best_error = None, math.inf
            for chain in open_chains:
                last_strip, last_y = chain[-1]
                slope = (last_y - chain[0][1]) / (last_strip - chain[0][0]) if len(chain) > 1 else 0.0
                error = abs(last_y + slope * (strip - last_strip) - y)
                if error <= max_step * (strip - last_strip) and error < best_error:
                    best, best_error = chain, error
            if best is None:
                chains.append([(strip, y)])
            else:
                best.append((strip, y))
                open_chains.remove(best)

    min_strips = math.ceil(params.min_strip_fraction * params.strips)
    vertical_gradient = np.gradient(
        _smooth_rows(gray.astype(np.float32), sigma), axis=0
    ) if params.min_support > 0 else None
    lines = []
    for chain in chains:
        if len(chain) < min_strips:
            continue
        line = _fit_line(chain, strip_width)
        # Una repisa es recta: si los saltos se alejan de la recta, la
        # cadena salto entre repisas distintas (lineas diagonales falsas).
        residuals = [abs(line.y_at((s + 0.5) * strip_width) - y) for s, y in chain]
        if max(residuals) > params.max_residual_frac * height:
            continue
        # Los saltos de cada franja pueden calzar con la recta aunque la
        # recta cruce productos entre ellos (diagonal que salta entre
        # repisas): el borde debe verse a lo largo de toda la recta.
        if vertical_gradient is not None and (
            _edge_support(vertical_gradient, line, references, strip_width, params)
            < params.min_support
        ):
            continue
        lines.append(line)
    return sorted(lines, key=lambda line: line.y_at(width / 2))


def _smooth_rows(image: np.ndarray, sigma: float) -> np.ndarray:
    """Suavizado gaussiano solo en vertical (el mismo de _smooth)."""
    radius = int(math.ceil(3 * sigma))
    return cv2.GaussianBlur(
        image, (1, 2 * radius + 1), sigmaX=0, sigmaY=sigma, borderType=cv2.BORDER_REPLICATE
    )


def _edge_support(
    vertical_gradient: np.ndarray,
    line: ShelfLine,
    references: list[float],
    strip_width: float,
    params: SegmentationParams,
) -> float:
    """Fraccion de subfranjas, a lo largo de la recta, donde el brillo
    promedio siguiendo la recta (con una holgura vertical) salta al menos
    support_edge veces la referencia de su franja (la misma escala de
    min_edge). En un borde de repisa el salto
    es parejo en todo el ancho; en una recta que cruza productos, el texto y
    los bordes de cajas se cancelan al promediar."""
    height, width = vertical_gradient.shape
    radius = max(1, round(params.support_radius_frac * height))
    offsets = np.arange(-radius, radius + 1)[:, None]
    sub_width = strip_width / params.support_substrips
    starts = np.arange(line.x_min, line.x_max - sub_width / 2, sub_width)
    supported = 0
    for start in starts:
        xs = np.arange(int(start), min(int(start + sub_width), width))
        ys = np.clip(np.rint(line.slope * xs + line.intercept + offsets).astype(int), 0, height - 1)
        strength = float(np.abs(vertical_gradient[ys, xs].mean(axis=1)).max())
        strip = min(int((start + sub_width / 2) // strip_width), len(references) - 1)
        supported += strength / references[strip] >= params.support_edge
    return supported / len(starts) if len(starts) else 0.0


def _smooth(profile: np.ndarray, sigma: float) -> np.ndarray:
    """Suavizado gaussiano 1D. Repite el valor del borde en vez de rellenar
    con ceros, que crearia un salto falso (una repisa) en el borde."""
    radius = int(math.ceil(3 * sigma))
    kernel = np.exp(-0.5 * (np.arange(-radius, radius + 1) / sigma) ** 2)
    padded = np.pad(profile, radius, mode="edge")
    return np.convolve(padded, kernel / kernel.sum(), mode="valid")


def _profile_peaks(profile: np.ndarray, min_value: float, min_spacing: float) -> list[float]:
    """Maximos del perfil por encima de min_value, separados al menos
    min_spacing (supresion de no maximos: gana el mas alto). Los dos
    bordes de una misma repisa quedan como un solo pico."""
    peaks: list[int] = []
    for index in np.argsort(profile)[::-1]:
        if profile[index] < min_value:
            break
        if all(abs(index - p) >= min_spacing for p in peaks):
            peaks.append(int(index))
    return sorted(float(p) for p in peaks)


def _fit_line(chain: list[tuple[int, float]], strip_width: float) -> ShelfLine:
    xs = np.array([(strip + 0.5) * strip_width for strip, _ in chain])
    ys = np.array([y for _, y in chain])
    slope, intercept = np.polyfit(xs, ys, 1)
    return ShelfLine(
        x_min=chain[0][0] * strip_width,
        x_max=(chain[-1][0] + 1) * strip_width,
        slope=float(slope),
        intercept=float(intercept),
    )


def _shelf_bounds(
    gray: np.ndarray, lines: list[ShelfLine], params: SegmentationParams
) -> tuple[float, float, list[tuple[float, float]]] | None:
    """Rango horizontal de la gondola y limites (y superior, y inferior) de
    cada nivel de repisa, en coordenadas de la imagen de trabajo."""
    height = gray.shape[0]
    x_min = min(line.x_min for line in lines)
    x_max = max(line.x_max for line in lines)
    ranges = [line.y_range(x_min, x_max) for line in lines]
    centers = [line.y_at((x_min + x_max) / 2) for line in lines]
    spacing = float(np.median(np.diff(centers))) if len(lines) > 1 else None

    texture = _texture_map(gray)
    interior = [
        _band_texture(texture, x_min, x_max, ranges[i][0], ranges[i + 1][1])
        for i in range(len(lines) - 1)
    ]
    reference = float(np.median(interior)) if interior else float(texture.mean())
    threshold = params.content_ratio * reference

    levels = [(ranges[i][0], ranges[i + 1][1]) for i in range(len(lines) - 1)]
    # Sobre la primera repisa y bajo la ultima se agregan niveles de a uno
    # (del alto tipico de un nivel) mientras tengan contenido: la foto puede
    # cortar niveles cuyo borde no se ve. Se detiene en techo/piso liso o
    # en el borde de la imagen.
    step = spacing if spacing is not None else float(height)
    edge, upper = ranges[0][0], ranges[0][1]
    while edge > 1:
        top = max(0.0, edge - step)
        if _band_texture(texture, x_min, x_max, top, edge) < threshold:
            break
        levels.insert(0, (top, upper))
        edge, upper = top, edge
    edge, lower = ranges[-1][1], ranges[-1][0]
    while edge < height - 1:
        bottom = min(float(height), edge + step)
        if _band_texture(texture, x_min, x_max, edge, bottom) < threshold:
            break
        levels.append((lower, bottom))
        edge, lower = bottom, edge
    if not levels:
        return None
    # Igual hacia los lados, de a una franja: el borde de una repisa puede
    # verse solo en parte del ancho (tapado por productos) aunque la
    # gondola siga.
    top, bottom = levels[0][0], levels[-1][1]
    step = gray.shape[1] / params.strips
    while x_min > 1:
        left = max(0.0, x_min - step)
        if _band_texture(texture, left, x_min, top, bottom) < threshold:
            break
        x_min = left
    while x_max < gray.shape[1] - 1:
        right = min(float(gray.shape[1]), x_max + step)
        if _band_texture(texture, x_max, right, top, bottom) < threshold:
            break
        x_max = right
    return x_min, x_max, levels


def _texture_map(gray: np.ndarray) -> np.ndarray:
    """Magnitud del gradiente: alta en productos, baja en piso/techo lisos."""
    gx = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)
    return cv2.magnitude(gx, gy)


def _band_texture(texture: np.ndarray, x_min: float, x_max: float, top: float, bottom: float) -> float:
    band = texture[
        max(0, int(top)) : max(0, int(math.ceil(bottom))),
        max(0, int(x_min)) : max(0, int(math.ceil(x_max))),
    ]
    return float(band.mean()) if band.size else 0.0


def _to_pixels(
    bbox: tuple[float, float, float, float], scale: float, width: int, height: int
) -> PixelBBox:
    x_min, y_min, x_max, y_max = (v / scale for v in bbox)
    return (
        max(0, math.floor(x_min)),
        max(0, math.floor(y_min)),
        min(width, math.ceil(x_max)),
        min(height, math.ceil(y_max)),
    )
