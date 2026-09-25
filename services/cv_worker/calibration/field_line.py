from __future__ import annotations

from dataclasses import dataclass

import numpy as np

CALIBRATION_ALGORITHM_VERSION = "cal_v1"


@dataclass
class Calibration:
    mode: str | None
    confidence: float
    meters_per_pixel: float | None
    debug_points: list[tuple[int, int]]


def detect_field_line(frame: np.ndarray | None) -> Calibration | None:
    if frame is None:
        return None
    try:
        import cv2
    except Exception:
        return None
    gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY) if frame.ndim == 3 else frame
    edges = cv2.Canny(gray.astype(np.uint8), 60, 160)
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=80, minLineLength=120, maxLineGap=20)
    if lines is None:
        return None
    horiz = []
    for x1, y1, x2, y2 in lines[:, 0]:
        if abs(y2 - y1) < 12 and abs(x2 - x1) > 80:
            horiz.append((int(x1), int(y1), int(x2), int(y2)))
    if len(horiz) < 2:
        return None
    ys = sorted({h[1] for h in horiz})
    if len(ys) < 2:
        return None
    dy = abs(ys[-1] - ys[0])
    if dy < 20:
        return None
    mpp = (5 * 0.9144) / dy
    return Calibration(mode="field_line", confidence=min(0.9, 0.4 + 0.1 * len(horiz)), meters_per_pixel=mpp, debug_points=[(h[0], h[1]) for h in horiz[:8]])
