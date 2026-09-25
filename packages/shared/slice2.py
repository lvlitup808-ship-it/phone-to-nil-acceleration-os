from __future__ import annotations

from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator


class AssessmentStatus(str, Enum):
    ok = "ok"
    low_confidence = "low_confidence"
    insufficient_data = "insufficient_data"
    uncalibrated = "uncalibrated"
    error = "error"
    scope_revoked = "scope_revoked"


class CueStatus(str, Enum):
    ok = "ok"
    low_confidence = "low_confidence"
    uncalibrated = "uncalibrated"
    insufficient_data = "insufficient_data"


class Slice2Cue(BaseModel):
    name: str
    value: float | None = None
    unit: str
    confidence: float = Field(ge=0, le=1)
    calibration_mode: str
    cue_status: CueStatus
    evidence_frames: list[int] = []
    source_clip_id: str
    actionable: dict[str, Any] | None = None

    @model_validator(mode="after")
    def no_number_when_uncalibrated(self) -> Slice2Cue:
        if self.cue_status == CueStatus.uncalibrated:
            object.__setattr__(self, "value", None)
        return self


class Slice2Event(BaseModel):
    name: str
    t_ms: int
    confidence: float = Field(ge=0, le=1)
    frame: int


class Slice2Assessment(BaseModel):
    """Payload of run_pose_assessment / POST /pose/assess. Extra keys are allowed (additive API)."""

    model_config = {"extra": "allow"}

    assessment_status: AssessmentStatus
    retake_instruction: str | None
    movement: Literal["release", "break"]
    template: Literal["wr_release", "db_break"]
    events: list[Slice2Event]
    cues: list[Slice2Cue]
    fix_this_first: str | None
    calibration_mode: str | None
    calibration_confidence: float
    synthetic_risk: Literal["low", "medium", "high"] | None
    minors_mode: bool
    versions: dict[str, str]
    assessment_lineage: dict[str, Any]
    artifacts: dict[str, str]
    golden_set: str
    pose_source: Literal["fixture", "model", "error"]
