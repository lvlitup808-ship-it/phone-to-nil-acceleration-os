from __future__ import annotations

from typing import Any

JOINT_CONF_MIN = 0.4
WR_DOWNGRADE_HEIGHT_PRIOR = {"shin_angle_at_contact", "hip_height_at_contact"}
DB_DOWNGRADE_HEIGHT_PRIOR = {"pad_level_at_break", "foot_plant_angle"}

RETAKE = {
    "uncalibrated": "No field lines and no athlete height on file. Reshoot side-on over visible yard lines, or add height to the profile.",
    "insufficient_data": "Could not find motion start. Reshoot 8 yards away, full body in frame, 5-10 seconds, start standing still then go.",
    "low_confidence": "Joints dropped below 0.4. Reshoot in daylight, phone at hip height.",
    "error": "Pipeline error. Re-upload both angles.",
}


def joint_ok(kp_frame, idxs: list[int]) -> bool:
    return all(float(kp_frame[i, 2]) >= JOINT_CONF_MIN for i in idxs)


def apply_gate(cue: dict[str, Any], *, movement: str, calibration_mode: str | None, joints_ok: bool) -> dict[str, Any]:
    if calibration_mode is None and cue["name"] in {
        "shin_angle_at_contact", "hip_height_at_contact", "first_step_separation",
        "pad_level_at_break", "foot_plant_angle",
    }:
        cue["value"] = None
        cue["cue_status"] = "uncalibrated"
        return cue
    if not joints_ok:
        cue["cue_status"] = "low_confidence"
        return cue
    if calibration_mode == "height_prior":
        watch = WR_DOWNGRADE_HEIGHT_PRIOR if movement == "release" else DB_DOWNGRADE_HEIGHT_PRIOR
        if cue["name"] in watch:
            cue["cue_status"] = "low_confidence"
            return cue
    cue["cue_status"] = "ok"
    return cue


def rollup(cues: list[dict[str, Any]], events: list) -> str:
    if not events:
        return "insufficient_data"
    if any(c["cue_status"] == "uncalibrated" for c in cues) and all(c["cue_status"] != "ok" for c in cues):
        return "uncalibrated"
    oks = [c for c in cues if c["cue_status"] == "ok"]
    if not oks:
        return "insufficient_data"
    if len(oks) < 3:
        return "low_confidence"
    return "ok"
