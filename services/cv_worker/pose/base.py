"""Pose adapter contract. COCO-17 keypoints, raw + One-Euro smoothed."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import numpy as np

COCO17 = [
    "nose", "l_eye", "r_eye", "l_ear", "r_ear",
    "l_shoulder", "r_shoulder", "l_elbow", "r_elbow", "l_wrist", "r_wrist",
    "l_hip", "r_hip", "l_knee", "r_knee", "l_ankle", "r_ankle",
]

L_HIP, R_HIP = 11, 12
L_KNEE, R_KNEE = 13, 14
L_ANKLE, R_ANKLE = 15, 16
L_SHOULDER, R_SHOULDER = 5, 6
NOSE = 0

POSE_MODEL_VERSION_MEDIAPIPE = "mediapipe_blazepose_v0"
POSE_MODEL_VERSION_RTMPOSE = "rtmpose_onnx_v0"
POSE_MODEL_VERSION_FIXTURE = "fixture_synth_v0"


@dataclass
class PoseSequence:
    keypoints: np.ndarray
    keypoints_raw: np.ndarray
    fps: float
    frame_timestamps_ms: list[int]
    model_id: str
    model_version: str
    width: int = 1280
    height: int = 720


class PoseAdapter(Protocol):
    def infer(self, frames: list[np.ndarray]) -> PoseSequence: ...


def one_euro(signal: np.ndarray, fps: float, min_cutoff: float = 1.0, beta: float = 0.007) -> np.ndarray:
    if signal.size == 0:
        return signal
    t = signal.shape[0]
    out = np.zeros_like(signal, dtype=float)
    out[0] = signal[0]
    x_hat = signal[0].astype(float)
    dx_hat = np.zeros_like(signal[0], dtype=float)
    dt = 1.0 / max(fps, 1e-6)

    def alpha(cutoff: float) -> float:
        tau = 1.0 / (2.0 * np.pi * max(cutoff, 1e-6))
        return 1.0 / (1.0 + tau / dt)

    for i in range(1, t):
        dx = (signal[i] - x_hat) / dt
        dx_hat = dx_hat + alpha(1.0) * (dx - dx_hat)
        cutoff = min_cutoff + beta * np.abs(dx_hat)
        a = alpha(cutoff)
        x_hat = x_hat + a * (signal[i] - x_hat)
        out[i] = x_hat
    return out


def smooth_sequence(raw: np.ndarray, fps: float) -> np.ndarray:
    sm = raw.copy()
    for j in range(raw.shape[1]):
        for c in range(2):
            sm[:, j, c] = one_euro(raw[:, j, c], fps)
    return sm


def timestamps_ms(n: int, fps: float) -> list[int]:
    return [int(round(1000.0 * i / fps)) for i in range(n)]
