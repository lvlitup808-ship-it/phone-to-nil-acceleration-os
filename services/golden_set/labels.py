"""Coach labels for golden-set clips.

A save writes data/golden_set/labels/<clip_id>_<coach_id>.json, which is what
services/api/gates.py counts. Saves are append-only: a coach labels a clip once.
A save needs all five events and the six frozen cues for the clip's movement
(docs/product/cue_freeze_v1.md), unless the coach marks the clip cannot_label
(excluded). An unsure cue is saved as disputed, never guessed.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

GOLDEN_DIR = Path(__file__).resolve().parents[2] / "data/golden_set"

EVENTS = {
    "release": ["motion_start", "first_step", "second_step", "release", "peak_velocity"],
    "break": ["motion_start", "first_step", "second_step", "break", "peak_velocity"],
}
CUES = {
    "release": [
        "first_step_separation", "shin_angle_at_contact", "hip_height_at_contact",
        "ground_contact_time_first_step", "lean_at_release", "arm_drive_symmetry",
    ],
    "break": [
        "pad_level_at_break", "foot_plant_angle", "hip_rotation_rate",
        "deceleration_time", "eye_discipline_proxy", "recovery_first_step",
    ],
}


class EventLabel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    t_ms: int = Field(ge=0)


class CueLabel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    value: float | None = None
    disputed: bool = False

    @model_validator(mode="after")
    def unsure_is_disputed(self) -> CueLabel:
        if self.value is None and not self.disputed:
            raise ValueError("a cue without a value must be marked disputed")
        return self


class LabelIn(BaseModel):
    model_config = ConfigDict(extra="forbid")

    clip_id: str = Field(pattern=r"^clp_\d{4}$")
    coach_id: str = Field(pattern=r"^coach_[a-z0-9]{1,32}$")
    events: dict[str, EventLabel] = Field(default_factory=dict)
    cues: dict[str, CueLabel] = Field(default_factory=dict)
    disputed: bool = False
    excluded: bool = False
    notes: str = Field(default="", max_length=2000)


class LabelError(Exception):
    def __init__(self, status: int, detail: str):
        super().__init__(detail)
        self.status = status
        self.detail = detail


def _manifest(golden_dir: Path) -> dict[str, Any]:
    return json.loads((golden_dir / "manifest.json").read_text())


def spec(clip_id: str, golden_dir: Path | None = None) -> dict[str, Any]:
    """What a label for this clip must contain."""
    golden_dir = golden_dir or GOLDEN_DIR
    manifest = _manifest(golden_dir)
    clip = next((c for c in manifest.get("clips", []) if c.get("clip_id") == clip_id), None)
    if clip is None:
        raise LabelError(404, f"{clip_id} is not in the golden-set manifest")
    movement = clip["movement"]
    return {
        "clip_id": clip_id,
        "position_target": clip["position_target"],
        "movement": movement,
        "events": EVENTS[movement],
        "cues": CUES[movement],
        "labeling_protocol_version": manifest.get("labeling_protocol_version"),
    }


def save(body: LabelIn, golden_dir: Path | None = None) -> dict[str, Any]:
    golden_dir = golden_dir or GOLDEN_DIR
    s = spec(body.clip_id, golden_dir)
    clip = next(c for c in _manifest(golden_dir).get("clips", []) if c.get("clip_id") == body.clip_id)
    # Import here so the label module does not import the API package at load.
    from services.api.gates import has_film

    if not has_film(clip, golden_dir):
        raise LabelError(409, f"{body.clip_id} has no film on disk; fixture clips cannot be labeled")
    if not body.excluded:
        if sorted(body.events) != sorted(s["events"]):
            raise LabelError(422, f"events must be exactly {s['events']}")
        if sorted(body.cues) != sorted(s["cues"]):
            raise LabelError(422, f"cues must be exactly the frozen {s['movement']} cues {s['cues']}")
    path = golden_dir / "labels" / f"{body.clip_id}_{body.coach_id}.json"
    record = {
        **body.model_dump(),
        "labeling_protocol_version": s["labeling_protocol_version"],
        "saved_at": datetime.now(UTC).isoformat(),
    }
    try:
        with path.open("x") as fh:
            json.dump(record, fh, indent=2)
            fh.write("\n")
    except FileExistsError:
        raise LabelError(409, f"{path.name} exists; labels are append-only") from None
    return {"path": f"labels/{path.name}", "label": record}
