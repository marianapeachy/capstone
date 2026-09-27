"""Validaciones de entrada compartidas por los modulos de pre-procesamiento.

Las imagenes son arrays de NumPy tal como los entrega OpenCV
(cv2.imread): (alto, ancho) en escala de grises o (alto, ancho, canales)
en BGR.
"""

from __future__ import annotations

import numpy as np


def check_image(image: np.ndarray | None) -> None:
    """Lanza ValueError si la imagen es None, vacia o no tiene 2 o 3
    dimensiones, y TypeError si no es un np.ndarray."""
    if image is None:
        raise ValueError("La imagen es None (¿fallo cv2.imread?)")
    if not isinstance(image, np.ndarray):
        raise TypeError(f"Se esperaba un np.ndarray, se recibio {type(image).__name__}")
    if image.ndim not in (2, 3):
        raise ValueError(
            f"La imagen debe tener 2 o 3 dimensiones, tiene {image.ndim}"
        )
    if image.size == 0:
        raise ValueError(f"La imagen esta vacia (shape={image.shape})")
