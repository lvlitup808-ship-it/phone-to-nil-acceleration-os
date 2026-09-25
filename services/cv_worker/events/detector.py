from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from services.cv_worker.pose.base import L_ANKLE, L_HIP, R_ANKLE, R_HIP, PoseSequence


@dataclass
class Event:
    name: str
    t_ms: int
    confidence: float
    frame: int


def _hip_xy(kp: np.ndarray) -> np.ndarray:
    return (kp[:, L_HIP, :2] + kp[:, R_HIP, :2]) / 2.0


def detect_events(seq: PoseSequence, movement: str) -> list[Event]:
    kp = seq.keypoints
    fps = seq.fps
    hip = _hip_xy(kp)
    vel = np.gradient(hip[:, 0]) * fps
    baseline = vel[: max(8, int(0.25 * fps))]
    mu, sd = float(np.mean(baseline)), float(np.std(baseline) + 1e-6)
    thresh = mu + 2 * sd
    motion_idx = next((i for i in range(len(vel)) if vel[i] > thresh and i > 5), None)
    if motion_idx is None:
        return []
    events = [Event("motion_start", seq.frame_timestamps_ms[motion_idx], 0.8, motion_idx)]
    lead_x = kp[:, R_ANKLE, 0]
    d = np.gradient(lead_x)
    strikes = [i for i in range(motion_idx + 3, len(d) - 1) if d[i] > d[i - 1] and d[i] >= d[i + 1]]
    if strikes:
        events.append(Event("first_step", seq.frame_timestamps_ms[strikes[0]], 0.75, strikes[0]))
    if len(strikes) > 1:
        events.append(Event("second_step", seq.frame_timestamps_ms[strikes[1]], 0.7, strikes[1]))
    window_end = min(len(vel) - 1, motion_idx + int(3 * (fps / 4)))
    hip_ang = np.gradient(_hip_xy(kp)[:, 1])
    rel_slice = hip_ang[motion_idx : window_end + 1]
    rel_i = motion_idx + int(np.argmax(np.abs(rel_slice))) if rel_slice.size else motion_idx
    name = "break" if movement == "break" else "release"
    events.append(Event(name, seq.frame_timestamps_ms[rel_i], 0.65, rel_i))
    peak_i = motion_idx + int(np.argmax(vel[motion_idx:]))
    events.append(Event("peak_velocity", seq.frame_timestamps_ms[peak_i], 0.7, peak_i))
    return events
