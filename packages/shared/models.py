from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class PositionTemplate(str, Enum):
    wr_release = "wr_release"
    db_break = "db_break"
    rb_first_cut = "rb_first_cut"
    ol_first_step = "ol_first_step"
    edge_rush = "edge_rush"
    lb_scrape = "lb_scrape"
    qb_drop = "qb_drop"


class CueId(str, Enum):
    shin_angle = "shin_angle"
    hip_height = "hip_height"
    ground_contact_time = "ground_contact_time"
    first_step_separation = "first_step_separation"
    asymmetry = "asymmetry"
    stride_frequency = "stride_frequency"
    deceleration = "deceleration"


class ClipQuality(BaseModel):
    score: float = Field(ge=0, le=1)
    usable: bool
    reasons: list[str] = []
    retake_instructions: str | None = None


class Cue(BaseModel):
    id: CueId
    value: float | None = None
    unit: str | None = None
    confidence: float = Field(ge=0, le=1, default=0.5)
    priority: int = 1
    trainability: float = Field(ge=0, le=1, default=0.5)
    note: str


class Assessment(BaseModel):
    id: str
    athlete_id: str
    template: PositionTemplate
    cues: list[Cue]
    quality: ClipQuality
    created_at: datetime


class NILBand(BaseModel):
    athlete_id: str
    currency: str = "USD"
    p25: int
    p50: int
    p75: int
    confidence: float
    assumptions: list[str]
    comp_cluster_ids: list[str]
    disclaimer_version: str
    counterfactuals: dict[str, Any] = {}


class Drill(BaseModel):
    id: str
    cue: CueId
    name: str
    sets: str
    cue_language: str
    progression: str
