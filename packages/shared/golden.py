"""Golden-set manifest (data/golden_set/manifest.json).

Vocabularies match the film intake form (apps/coach-console/app/film/intake) and the
clip naming contract (services/cv_worker/ingest/naming.py). The gate in
services/api/gates.py reads surface, lighting and athlete_id from filmed clips,
so a clip with real film must record all three.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

Surface = Literal["turf", "grass", "track"]
Lighting = Literal["daylight", "night_lit", "indoor"]


class Camera(BaseModel):
    model_config = ConfigDict(extra="forbid")

    path: str
    fps: float | None = Field(default=None, gt=0)
    present: bool = False


class ManifestClip(BaseModel):
    model_config = ConfigDict(extra="forbid")

    clip_id: str = Field(pattern=r"^clp_\d{4}$")
    athlete_id: str | None = Field(default=None, pattern=r"^ath_\d{4}$")
    position_target: Literal["WR", "DB"]
    movement: Literal["release", "break"]
    surface: Surface | None = None
    lighting: Lighting | None = None
    athlete_height_cm: float | None = Field(default=None, gt=0)
    camera_side: Camera | None = None
    camera_45: Camera | None = None
    disputed: bool = False
    labels: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def filmed_clips_record_diversity_fields(self) -> ManifestClip:
        filmed = any(cam is not None and cam.present for cam in (self.camera_side, self.camera_45))
        missing = [f for f in ("athlete_id", "surface", "lighting") if getattr(self, f) is None]
        if filmed and missing:
            raise ValueError(
                f"{self.clip_id} has film present; record athlete_id, surface, lighting "
                f"(missing: {', '.join(missing)})"
            )
        return self


class GoldenManifest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: str = "1.1.0"
    created_at: str | None = None
    labeling_protocol_version: str | None = None
    golden_set: Literal["pending", "ready"]
    note: str | None = None
    clips: list[ManifestClip]

    @model_validator(mode="after")
    def unique_clip_ids(self) -> GoldenManifest:
        seen: set[str] = set()
        for clip in self.clips:
            if clip.clip_id in seen:
                raise ValueError(f"duplicate clip_id {clip.clip_id}")
            seen.add(clip.clip_id)
        return self
