from __future__ import annotations

import numpy as np

from services.cv_worker.calibration.field_line import Calibration
from services.cv_worker.pose.base import L_ANKLE, NOSE, R_ANKLE


def height_prior(keypoints: np.ndarray, height_cm: float | None, standing_frame: int = 5) -> Calibration | None:
    if not height_cm or height_cm < 120:
        return None
    frame = keypoints[min(standing_frame, len(keypoints) - 1)]
    if frame[NOSE, 2] < 0.4 or min(frame[L_ANKLE, 2], frame[R_ANKLE, 2]) < 0.4:
        return None
    span = abs(max(frame[L_ANKLE, 1], frame[R_ANKLE, 1]) - frame[NOSE, 1])
    if span < 20:
        return None
    return Calibration(mode="height_prior", confidence=0.55, meters_per_pixel=(height_cm / 100.0) / span, debug_points=[])
