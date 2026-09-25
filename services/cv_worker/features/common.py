from __future__ import annotations

from typing import Any

import numpy as np

from packages.shared.slice2 import CueStatus
from services.cv_worker.events.detector import Event
from services.cv_worker.pose.base import L_HIP, R_HIP

FEATURE_ALGORITHM_VERSION = "wr_db_v1"


def mid_hip(kp_frame: np.ndarray) -> np.ndarray:
    return (kp_frame[L_HIP, :2] + kp_frame[R_HIP, :2]) / 2.0


def envelope(
    name: str,
    value: float | None,
    unit: str,
    confidence: float,
    calibration_mode: str | None,
    frames: list[int],
    clip_id: str,
    status: str = "ok",
) -> dict[str, Any]:
    status = CueStatus(status).value
    return {
        "name": name,
        "value": None if status == "uncalibrated" else value,
        "unit": unit,
        "confidence": confidence,
        "calibration_mode": calibration_mode or "none",
        "cue_status": status,
        "evidence_frames": frames,
        "source_clip_id": clip_id,
    }


def event_map(events: list[Event]) -> dict[str, Event]:
    return {e.name: e for e in events}


def angle_from_vertical(dx: float, dy: float) -> float:
    """Signed angle (deg) between segment (dx, dy) and the image vertical.

    Image y grows downward, so a segment pointing up has dy < 0. The angle is
    measured against the vertical axis regardless of up/down, signed by dx.
    """
    return float(np.degrees(np.arctan2(dx, max(abs(dy), 1e-6))))
