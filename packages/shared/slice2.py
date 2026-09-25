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
    def no_number_when_uncalibrated(self) -> "Slice2Cue":
        if self.cue_status == CueStatus.uncalibrated:
            object.__setattr__(self, "value", None)
        return self
