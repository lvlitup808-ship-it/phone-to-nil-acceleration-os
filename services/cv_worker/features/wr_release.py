from __future__ import annotations

import numpy as np

from services.cv_worker.calibration.field_line import Calibration
from services.cv_worker.confidence import apply_gate, joint_ok
from services.cv_worker.events.detector import Event
from services.cv_worker.features.common import angle_from_vertical, envelope, event_map, mid_hip
from services.cv_worker.pose.base import (
    L_ANKLE,
    L_HIP,
    L_SHOULDER,
    NOSE,
    R_ANKLE,
    R_HIP,
    R_KNEE,
    R_SHOULDER,
    PoseSequence,
)

GCT_MIN_MS = 90.0  # unsourced plausibility floor; see docs/audit/open_questions.md #5

WR_CUES = [
    "first_step_separation", "shin_angle_at_contact", "hip_height_at_contact",
    "ground_contact_time_first_step", "lean_at_release", "arm_drive_symmetry",
]


def extract_wr(
    seq: PoseSequence, events: list[Event], calibration: Calibration, clip_id: str, side_clip: bool
) -> list[dict]:
    em = event_map(events)
    kp = seq.keypoints
    mode = calibration.mode
    mpp = calibration.meters_per_pixel
    cues = []
    fs = em.get("first_step")
    rel = em.get("release")
    ms = em.get("motion_start")

    if fs:
        f = kp[fs.frame]
        hip = mid_hip(f)
        lead = f[R_ANKLE, :2]
        px = abs(float(lead[0] - hip[0]))
        yards = (px * mpp / 0.9144) if mpp else None
        status = "ok" if mpp else "uncalibrated"
        cue = envelope("first_step_separation", yards, "yd", fs.confidence, mode, [fs.frame], clip_id, status)
        cues.append(apply_gate(cue, movement="release", calibration_mode=mode, joints_ok=joint_ok(f, [L_HIP, R_HIP, R_ANKLE])))
    else:
        cues.append(envelope("first_step_separation", None, "yd", 0.0, mode, [], clip_id, "insufficient_data"))

    if fs and side_clip:
        f = kp[fs.frame]
        tibia = f[R_KNEE, :2] - f[R_ANKLE, :2]
        val = angle_from_vertical(float(tibia[0]), float(tibia[1]))
        status = "ok" if mode else "uncalibrated"
        cue = envelope("shin_angle_at_contact", val if status != "uncalibrated" else None, "deg", 0.7, mode, [fs.frame], clip_id, status)
        cues.append(apply_gate(cue, movement="release", calibration_mode=mode, joints_ok=joint_ok(f, [R_KNEE, R_ANKLE])))
    else:
        cues.append(envelope("shin_angle_at_contact", None, "deg", 0.0, mode, [], clip_id, "insufficient_data" if not side_clip else "uncalibrated"))

    if fs:
        f = kp[fs.frame]
        hip_y = float(mid_hip(f)[1])
        ankle_y = float(max(f[L_ANKLE, 1], f[R_ANKLE, 1]))
        nose_y = float(f[NOSE, 1])
        span = abs(ankle_y - nose_y) or 1.0
        ratio = abs(ankle_y - hip_y) / span
        status = "ok" if mode else "uncalibrated"
        cue = envelope("hip_height_at_contact", ratio if status != "uncalibrated" else None, "ratio", 0.7, mode, [fs.frame], clip_id, status)
        cues.append(apply_gate(cue, movement="release", calibration_mode=mode, joints_ok=joint_ok(f, [L_HIP, R_HIP, NOSE])))
    else:
        cues.append(envelope("hip_height_at_contact", None, "ratio", 0.0, mode, [], clip_id, "insufficient_data"))

    gct = float(em["second_step"].t_ms - fs.t_ms) * 0.45 if fs and "second_step" in em else None
    if fs and gct is not None and gct >= GCT_MIN_MS:
        ss = em["second_step"]
        cues.append(envelope("ground_contact_time_first_step", gct, "ms", 0.6, mode, [fs.frame, ss.frame], clip_id, "ok"))
    else:
        # Below the plausibility floor is reported as missing, not clamped to the floor.
        cues.append(envelope("ground_contact_time_first_step", None, "ms", 0.0, mode, [], clip_id, "insufficient_data"))

    if rel:
        f = kp[rel.frame]
        torso = f[NOSE, :2] - mid_hip(f)
        lean = angle_from_vertical(float(torso[0]), float(torso[1]))
        cues.append(envelope("lean_at_release", abs(lean), "deg", 0.65, mode, [rel.frame], clip_id, "ok"))
    else:
        cues.append(envelope("lean_at_release", None, "deg", 0.0, mode, [], clip_id, "insufficient_data"))

    if ms and rel:
        sl = np.gradient(kp[ms.frame : rel.frame + 1, L_SHOULDER, 1])
        sr = np.gradient(kp[ms.frame : rel.frame + 1, R_SHOULDER, 1])
        ratio = float((np.mean(np.abs(sl)) + 1e-6) / (np.mean(np.abs(sr)) + 1e-6))
        ratio = min(ratio, 1 / ratio) if ratio else 0.0
        cues.append(envelope("arm_drive_symmetry", ratio, "ratio", 0.6, mode, [ms.frame, rel.frame], clip_id, "ok"))
    else:
        cues.append(envelope("arm_drive_symmetry", None, "ratio", 0.0, mode, [], clip_id, "insufficient_data"))
    return cues
