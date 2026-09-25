from __future__ import annotations

import numpy as np

from services.cv_worker.calibration.field_line import Calibration, detect_field_line
from services.cv_worker.calibration.height_prior import height_prior
from services.cv_worker.calibration.imu_fused import fuse_imu


def resolve_calibration(
    frame: np.ndarray | None,
    keypoints: np.ndarray,
    height_cm: float | None,
    imu_tilt_deg: float | None = None,
) -> Calibration:
    a = detect_field_line(frame)
    if a is not None:
        return fuse_imu(a, imu_tilt_deg) or a
    b = height_prior(keypoints, height_cm)
    if b is not None:
        return fuse_imu(b, imu_tilt_deg) or b
    return Calibration(mode=None, confidence=0.0, meters_per_pixel=None, debug_points=[])
