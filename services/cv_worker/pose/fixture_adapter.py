"""Deterministic synthetic pose for CI. Not athlete validation."""

from __future__ import annotations

import numpy as np

from services.cv_worker.pose.base import (
    L_ANKLE, L_HIP, L_KNEE, L_SHOULDER, NOSE,
    POSE_MODEL_VERSION_FIXTURE, R_ANKLE, R_HIP, R_KNEE, R_SHOULDER,
    PoseSequence, smooth_sequence, timestamps_ms,
)


def synthesize_start(n: int = 90, fps: float = 60.0, width: int = 1280, height: int = 720) -> np.ndarray:
    raw = np.zeros((n, 17, 3), dtype=float)
    raw[:, :, 2] = 0.92
    cx, ground = width * 0.42, height * 0.88
    head = height * 0.28
    for t in range(n):
        phase = 0.0 if t < 25 else min(1.0, (t - 25) / 40.0)
        hip_x = cx + phase * 140
        hip_y = height * 0.55 - phase * 8
        raw[t, L_HIP] = (hip_x - 18, hip_y, 0.93)
        raw[t, R_HIP] = (hip_x + 18, hip_y, 0.93)
        raw[t, NOSE] = (hip_x, head + phase * 6, 0.9)
        raw[t, L_SHOULDER] = (hip_x - 40, height * 0.38, 0.9)
        raw[t, R_SHOULDER] = (hip_x + 38, height * 0.38, 0.9)
        raw[t, 7] = (hip_x - 50, height * 0.48, 0.88)
        raw[t, 8] = (hip_x + 62, height * 0.46, 0.88)
        raw[t, 9] = (hip_x - 55, height * 0.56, 0.86)
        raw[t, 10] = (hip_x + 80, height * 0.50, 0.86)
        raw[t, L_KNEE] = (hip_x - 16, height * 0.72, 0.91)
        raw[t, L_ANKLE] = (hip_x - 14, ground, 0.91)
        lead = 0.0 if t < 37 else min(1.0, (t - 37) / 8.0)
        raw[t, R_KNEE] = (hip_x + 20 + lead * 70, height * 0.70, 0.91)
        raw[t, R_ANKLE] = (hip_x + 22 + lead * 110, ground - (8 if 37 <= t <= 47 else 0), 0.91)
        raw[t, 1] = (hip_x - 8, head + 8, 0.8)
        raw[t, 2] = (hip_x + 8, head + 8, 0.8)
        raw[t, 3] = (hip_x - 14, head + 10, 0.75)
        raw[t, 4] = (hip_x + 14, head + 10, 0.75)
    return raw


class FixturePoseAdapter:
    model_id = "fixture_synth"
    model_version = POSE_MODEL_VERSION_FIXTURE

    def infer(self, frames: list[np.ndarray] | None = None, n: int = 90, fps: float = 60.0) -> PoseSequence:
        if frames:
            n = len(frames)
            h, w = frames[0].shape[:2]
        else:
            h, w = 720, 1280
        raw = synthesize_start(n=n, fps=fps, width=w, height=h)
        return PoseSequence(
            keypoints=smooth_sequence(raw, fps),
            keypoints_raw=raw,
            fps=fps,
            frame_timestamps_ms=timestamps_ms(n, fps),
            model_id=self.model_id,
            model_version=self.model_version,
            width=w,
            height=h,
        )
