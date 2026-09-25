from __future__ import annotations

import numpy as np

from services.cv_worker.pose.base import L_HIP, R_HIP

FEATURE_ALGORITHM_VERSION = "wr_db_v1"


def mid_hip(kp_frame):
    return (kp_frame[L_HIP, :2] + kp_frame[R_HIP, :2]) / 2.0


def envelope(name, value, unit, confidence, calibration_mode, frames, clip_id, status="ok"):
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


def event_map(events):
    return {e.name: e for e in events}


def angle_from_vertical(dx: float, dy: float) -> float:
    return float(np.degrees(np.arctan2(dx, max(dy, 1e-6))))
