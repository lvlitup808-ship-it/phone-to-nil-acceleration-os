from __future__ import annotations

import numpy as np

from services.cv_worker.confidence import apply_gate, joint_ok
from services.cv_worker.features.common import angle_from_vertical, envelope, event_map, mid_hip
from services.cv_worker.pose.base import L_ANKLE, L_HIP, NOSE, R_ANKLE, R_HIP, R_KNEE, PoseSequence


def extract_db(seq: PoseSequence, events, calibration, clip_id: str) -> list[dict]:
    em = event_map(events)
    kp = seq.keypoints
    mode = calibration.mode
    br = em.get("break") or em.get("release")
    pv = em.get("peak_velocity")
    fs = em.get("first_step")
    cues = []
    if br:
        f = kp[br.frame]
        ankle_y = float(max(f[L_ANKLE, 1], f[R_ANKLE, 1]))
        nose_y = float(f[NOSE, 1])
        hip_y = float(mid_hip(f)[1])
        span = abs(ankle_y - nose_y) or 1.0
        ratio = abs(ankle_y - hip_y) / span
        status = "ok" if mode else "uncalibrated"
        cue = envelope("pad_level_at_break", ratio if status != "uncalibrated" else None, "ratio", 0.7, mode, [br.frame], clip_id, status)
        cues.append(apply_gate(cue, movement="break", calibration_mode=mode, joints_ok=joint_ok(f, [L_HIP, R_HIP])))
    else:
        cues.append(envelope("pad_level_at_break", None, "ratio", 0.0, mode, [], clip_id, "insufficient_data"))
    if br:
        f = kp[br.frame]
        foot = f[R_ANKLE, :2] - f[R_KNEE, :2]
        ang = angle_from_vertical(float(foot[0]), float(foot[1]))
        status = "ok" if mode else "uncalibrated"
        cue = envelope("foot_plant_angle", ang if status != "uncalibrated" else None, "deg", 0.65, mode, [br.frame], clip_id, status)
        cues.append(apply_gate(cue, movement="break", calibration_mode=mode, joints_ok=joint_ok(f, [R_ANKLE, R_KNEE])))
    else:
        cues.append(envelope("foot_plant_angle", None, "deg", 0.0, mode, [], clip_id, "insufficient_data"))
    if br and br.frame > 2:
        hips = np.array([mid_hip(kp[i]) for i in range(max(0, br.frame - 3), br.frame + 1)])
        rate = float(np.linalg.norm(np.gradient(hips, axis=0)[-1]) * seq.fps)
        cues.append(envelope("hip_rotation_rate", rate, "px/s", 0.55, mode, [br.frame], clip_id, "ok"))
    else:
        cues.append(envelope("hip_rotation_rate", None, "px/s", 0.0, mode, [], clip_id, "insufficient_data"))
    if br and pv:
        dt = abs(br.t_ms - pv.t_ms)
        cues.append(envelope("deceleration_time", float(dt), "ms", 0.6, mode, [pv.frame, br.frame], clip_id, "ok"))
    else:
        cues.append(envelope("deceleration_time", None, "ms", 0.0, mode, [], clip_id, "insufficient_data"))
    if br:
        sl = slice(max(0, br.frame - 4), br.frame + 4)
        yaw = kp[sl, NOSE, 0] - ((kp[sl, L_HIP, 0] + kp[sl, R_HIP, 0]) / 2)
        cues.append(envelope("eye_discipline_proxy", float(np.var(yaw)), "px^2", 0.45, mode, list(range(sl.start, sl.stop)), clip_id, "ok"))
    else:
        cues.append(envelope("eye_discipline_proxy", None, "px^2", 0.0, mode, [], clip_id, "insufficient_data"))
    if br and fs and fs.t_ms >= br.t_ms:
        cues.append(envelope("recovery_first_step", float(fs.t_ms - br.t_ms), "ms", 0.6, mode, [br.frame, fs.frame], clip_id, "ok"))
    else:
        cues.append(envelope("recovery_first_step", None, "ms", 0.0, mode, [], clip_id, "insufficient_data"))
    return cues
