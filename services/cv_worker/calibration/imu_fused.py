from __future__ import annotations

from services.cv_worker.calibration.field_line import Calibration


def fuse_imu(base: Calibration | None, tilt_deg: float | None) -> Calibration | None:
    if base is None or tilt_deg is None:
        return base
    return Calibration(mode="imu_fused", confidence=min(1.0, base.confidence + 0.08), meters_per_pixel=base.meters_per_pixel, debug_points=base.debug_points)
