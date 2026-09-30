"""Deteccion de productos con YOLO26 (Ultralytics), la etapa `models` del
pipeline.

Recibe la imagen ya recortada a la ROI de la gondola (`RoiCrop.image`) y
devuelve cajas [x_min, y_min, x_max, y_max] en pixeles absolutos de esa
imagen. El llamador las lleva a la imagen original con
`RoiCrop.to_original()` y luego `CorrectedImage.to_original()`.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
from ultralytics import YOLO

BBox = tuple[float, float, float, float]

# Fijados en CLAUDE.md para gondolas densas: el default de Ultralytics
# (max_det=300) trunca una gondola llena de SKU-110K.
IMGSZ = 1280
MAX_DET = 1000
DEFAULT_CONF = 0.25


@dataclass(frozen=True)
class Detection:
    bbox: BBox
    score: float
    class_id: int
    class_name: str


class ProductDetector:
    """Carga los pesos una vez y detecta productos imagen por imagen.

    `weights` es un checkpoint `.pt` de YOLO26 (o un YAML de arquitectura,
    solo para pruebas). `device` sigue la convencion de Ultralytics
    ("cpu", "0", ...); None usa la GPU si hay una disponible.
    """

    def __init__(self, weights: str | Path, device: str | None = None) -> None:
        self._model = YOLO(str(weights))
        if getattr(self._model.model.model[-1], "one2one_cv2", None) is None:
            raise ValueError(
                f"{weights} no tiene la cabeza sin NMS de YOLO26; "
                "el pipeline infiere con nms=False y necesita un modelo YOLO26"
            )
        self._device = device

    def detect(self, image: np.ndarray | None, conf: float = DEFAULT_CONF) -> list[Detection]:
        if image is None or image.size == 0:
            raise ValueError("La imagen a detectar es None o esta vacia")
        result = self._model.predict(
            image,
            nms=False,
            max_det=MAX_DET,
            imgsz=IMGSZ,
            conf=conf,
            device=self._device,
            verbose=False,
        )[0]
        boxes = result.boxes
        return [
            Detection(
                bbox=(x_min, y_min, x_max, y_max),
                score=score,
                class_id=int(class_id),
                class_name=result.names[int(class_id)],
            )
            for (x_min, y_min, x_max, y_max), score, class_id in zip(
                boxes.xyxy.tolist(), boxes.conf.tolist(), boxes.cls.tolist()
            )
        ]
