"""Slice 2 orchestrator. Additive. Does not replace the v1 stub pipeline."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np

from packages.judgment.client import JudgmentClient
from packages.shared.slice2 import AssessmentStatus
from services.cv_worker.calibration.field_line import CALIBRATION_ALGORITHM_VERSION, Calibration
from services.cv_worker.calibration.resolve import resolve_calibration
from services.cv_worker.confidence import RETAKE, rollup
from services.cv_worker.events.detector import Event, detect_events
from services.cv_worker.features.common import FEATURE_ALGORITHM_VERSION
from services.cv_worker.features.db_break import extract_db
from services.cv_worker.features.wr_release import extract_wr
from services.cv_worker.pose.base import PoseAdapter, PoseSequence
from services.cv_worker.pose.factory import get_adapter
from services.cv_worker.pose.fixture_adapter import FixturePoseAdapter
from services.cv_worker.pose.mediapipe_adapter import MediaPipePoseAdapter

PIPELINE_VERSION = "slice2.0.0"
LABELING_PROTOCOL_VERSION = "1.0.0"
DISCLAIMER_VERSION = "2026-09-24"


def _synthetic_risk(judge: JudgmentClient | None, clip_meta: dict) -> str:
    client = judge or JudgmentClient()
    out = client.decide(
        {"quality_score": clip_meta.get("quality_score", 0.8), "blur": clip_meta.get("blur", 0.1)},
        {"synthetic": {"type": "noul", "instructions": "Does this look like a synthetic highlight?"}},
    )
    p = float(out["synthetic"].value)
    if p >= 0.66:
        return "high"
    if p >= 0.33:
        return "medium"
    return "low"


def is_cue_actionable(cue: dict, athlete_context: dict | None = None, judge: JudgmentClient | None = None) -> dict:
    from packages.judgment.client import JudgmentClient

    if cue.get("cue_status") != "ok" or cue.get("value") is None:
        return {"actionable": False, "reason": f"cue_status={cue.get('cue_status')}", "source": "gate"}
    client = judge or JudgmentClient()
    state = {"cue": cue["name"], "value": cue["value"], "confidence": cue["confidence"], **(athlete_context or {})}
    decision = client.decide(
        state,
        {"actionable": {"type": "noul", "instructions": "Is this cue actionable for a coach this week?"}},
    )
    j = decision["actionable"]
    return {
        "actionable": float(j.value) >= 0.55,
        "reason": "ok_and_confident" if float(j.value) >= 0.55 else "below_action_threshold",
        "source": j.source,
    }


def run_pose_assessment(
    *,
    movement: str,
    clip_id: str,
    side_clip: bool = True,
    frames: list[np.ndarray] | None = None,
    height_cm: float | None = 185.0,
    fps: float = 60.0,
    imu_tilt_deg: float | None = None,
    athlete_id: str = "unknown",
    artifacts_dir: Path | None = None,
    judge: JudgmentClient | None = None,
) -> dict[str, Any]:
    if movement not in {"release", "break"}:
        raise ValueError("Slice 2 only supports WR release and DB break")
    adapter = get_adapter()
    if frames is None:
        adapter = FixturePoseAdapter()
        seq = adapter.infer(None)
    else:
        try:
            seq = adapter.infer(frames, fps=fps) if isinstance(adapter, MediaPipePoseAdapter) else adapter.infer(frames)
        except Exception as exc:  # noqa: BLE001 - any adapter failure becomes status=error
            # Never substitute synthetic poses for a real clip.
            return _error_result(movement, clip_id, adapter, exc)
    pose_source = "fixture" if isinstance(adapter, FixturePoseAdapter) else "model"
    standing = frames[5] if frames is not None and len(frames) > 5 else None
    calibration = resolve_calibration(standing, seq.keypoints, height_cm, imu_tilt_deg)
    events = detect_events(seq, movement)
    if movement == "release":
        cues = extract_wr(seq, events, calibration, clip_id, side_clip=side_clip)
    else:
        cues = extract_db(seq, events, calibration, clip_id)
    status = rollup(cues, events)
    for cue in cues:
        cue["actionable"] = is_cue_actionable(cue, {"athlete_id": athlete_id}, judge=judge)
    fix_first = next((c["name"] for c in cues if c.get("actionable", {}).get("actionable") and c["cue_status"] == "ok"), None)
    artifacts = {}
    if artifacts_dir:
        artifacts_dir.mkdir(parents=True, exist_ok=True)
        artifacts = _write_debug(artifacts_dir, seq, calibration, events)
    return {
        "assessment_status": status,
        "retake_instruction": None if status == "ok" else RETAKE.get(status),
        "movement": movement,
        "template": "wr_release" if movement == "release" else "db_break",
        "events": [e.__dict__ for e in events],
        "cues": cues,
        "fix_this_first": fix_first,
        "calibration_mode": calibration.mode,
        "calibration_confidence": calibration.confidence,
        "synthetic_risk": _synthetic_risk(judge, {}),
        "minors_mode": False,
        "versions": _versions(seq.model_version),
        "assessment_lineage": {
            "clip_ids": [clip_id],
            "pipeline_version": PIPELINE_VERSION,
            "produced_at": datetime.now(UTC).isoformat(),
        },
        "artifacts": artifacts,
        "golden_set": "pending",
        "pose_source": pose_source,
    }


def _versions(pose_model_version: str) -> dict[str, str]:
    return {
        "pose_model_version": pose_model_version,
        "calibration_algorithm_version": CALIBRATION_ALGORITHM_VERSION,
        "feature_algorithm_version": FEATURE_ALGORITHM_VERSION,
        "labeling_protocol_version": LABELING_PROTOCOL_VERSION,
        "disclaimer_version": DISCLAIMER_VERSION,
        "pipeline_version": PIPELINE_VERSION,
    }


def _error_result(movement: str, clip_id: str, adapter: PoseAdapter, exc: Exception) -> dict[str, Any]:
    return {
        "assessment_status": AssessmentStatus.error.value,
        "retake_instruction": RETAKE["error"],
        "movement": movement,
        "template": "wr_release" if movement == "release" else "db_break",
        "events": [],
        "cues": [],
        "fix_this_first": None,
        "calibration_mode": None,
        "calibration_confidence": 0.0,
        "synthetic_risk": None,
        "minors_mode": False,
        "versions": _versions(getattr(adapter, "model_version", "unknown")),
        "assessment_lineage": {
            "clip_ids": [clip_id],
            "pipeline_version": PIPELINE_VERSION,
            "produced_at": datetime.now(UTC).isoformat(),
        },
        "artifacts": {},
        "golden_set": "pending",
        "pose_source": "error",
        "pose_error": f"{type(exc).__name__}: {exc}",
    }


def _write_debug(folder: Path, seq: PoseSequence, calibration: Calibration, events: list[Event]) -> dict[str, str]:
    heat = seq.keypoints[:, :, 2]
    np.save(folder / "pose_confidence_heatmap.npy", heat)
    debug = {
        "calibration_mode": calibration.mode,
        "debug_points": calibration.debug_points,
        "events": [e.__dict__ for e in events],
        "note": "pose_debug.mp4 needs real frames; heatmap + json shipped for fixtures.",
    }
    (folder / "calibration_debug.json").write_text(json.dumps(debug, indent=2))
    (folder / "pose_debug.json").write_text(json.dumps({"model": seq.model_id, "frames": int(seq.keypoints.shape[0]), "fps": seq.fps}, indent=2))
    return {
        "pose_confidence_heatmap": str(folder / "pose_confidence_heatmap.npy"),
        "calibration_debug": str(folder / "calibration_debug.json"),
        "pose_debug": str(folder / "pose_debug.json"),
    }
