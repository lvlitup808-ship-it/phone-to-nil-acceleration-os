from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from packages.biomech.features import extract_cues
from packages.evidence.pipeline import EvidencePipeline
from packages.judgment.client import JudgmentClient
from packages.shared.models import ClipQuality, NILBand, PositionTemplate

app = FastAPI(
    title="Phone-to-NIL Acceleration OS",
    version="0.2.0",
    description="Capture → Assess → Prescribe → Re-test → Value",
)

STORE: dict[str, dict[str, Any]] = {"clips": {}, "assessments": {}, "athletes": {}, "teams": {}}
JUDGE = JudgmentClient()
EVIDENCE = EvidencePipeline(JUDGE)


class UploadIn(BaseModel):
    athlete_id: str
    angle: str = Field(pattern="^(side|fortyfive|front)$")
    quality_score: float = 0.8
    blur: float = 0.1
    uri: str


class AssessIn(BaseModel):
    clip_ids: list[str]
    athlete_id: str
    template: PositionTemplate = PositionTemplate.wr_release
    metrics: dict[str, float] = {}


class RetestIn(BaseModel):
    athlete_id: str
    previous_assessment_id: str
    clip_ids: list[str]
    template: PositionTemplate


class AnnotateIn(BaseModel):
    assessment_id: str
    coach_id: str
    note: str


class PoseAssessIn(BaseModel):
    athlete_id: str
    clip_id: str
    movement: str = Field(pattern="^(release|break)$")
    side_clip: bool = True
    height_cm: float | None = 185.0
    minors_mode: bool = False


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/upload")
def upload(body: UploadIn) -> dict[str, Any]:
    decisions = JUDGE.decide(
        {"quality_score": body.quality_score, "blur": body.blur, "angle": body.angle},
        {
            "usable": {"type": "noul", "instructions": "Is this clip usable for pose estimation?"},
            "synthetic": {"type": "noul", "instructions": "Does this look like a synthetic highlight?"},
        },
    )
    usable = float(decisions["usable"].value) >= JUDGE.threshold
    synthetic = float(decisions["synthetic"].value) >= 0.5
    quality = ClipQuality(
        score=body.quality_score,
        usable=usable and not synthetic,
        reasons=[] if usable else ["low quality or suspected synthetic"],
        retake_instructions=None if usable else "Retake side-on, 5-10s, phone stable, full body in frame, 60fps if possible.",
    )
    clip_id = str(uuid.uuid4())
    STORE["clips"][clip_id] = {**body.model_dump(), "id": clip_id, "quality": quality.model_dump()}
    if not quality.usable:
        raise HTTPException(status_code=422, detail=quality.model_dump())
    return {"clip_id": clip_id, "quality": quality.model_dump()}


@app.post("/assess")
def assess(body: AssessIn) -> dict[str, Any]:
    for cid in body.clip_ids:
        if cid not in STORE["clips"]:
            raise HTTPException(404, f"clip {cid} not found")
    cues = extract_cues(body.template, body.metrics)
    evidence = EVIDENCE.run(f"{body.template.value} acceleration", cues[0].id.value)
    assessment_id = str(uuid.uuid4())
    row = {
        "id": assessment_id,
        "athlete_id": body.athlete_id,
        "template": body.template.value,
        "cues": [c.model_dump() for c in cues],
        "evidence": evidence,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    STORE["assessments"][assessment_id] = row
    return row


@app.get("/report/{assessment_id}")
def report(assessment_id: str) -> dict[str, Any]:
    row = STORE["assessments"].get(assessment_id)
    if not row:
        raise HTTPException(404, "assessment not found")
    return row


@app.get("/prescribe/{assessment_id}")
def prescribe(assessment_id: str) -> dict[str, Any]:
    row = STORE["assessments"].get(assessment_id)
    if not row:
        raise HTTPException(404, "assessment not found")
    first = row["cues"][0]
    cue = first.get("id") or first.get("name")
    pack = EVIDENCE.run("drill prescription", cue)
    reviewed = [d for d in pack["drills"] if d.get("coach_reviewed") is not False]
    return {"assessment_id": assessment_id, "primary_cue": cue, "drills": reviewed, "grounded": pack["grounded"]}


@app.post("/pose/assess")
def pose_assess(body: PoseAssessIn) -> dict[str, Any]:
    from pathlib import Path

    from services.cv_worker.pipeline_v2 import run_pose_assessment

    out = run_pose_assessment(
        movement=body.movement,
        clip_id=body.clip_id,
        side_clip=body.side_clip,
        height_cm=body.height_cm,
        athlete_id=body.athlete_id,
        artifacts_dir=Path("artifacts") / body.clip_id,
        judge=JUDGE,
    )
    out["minors_mode"] = body.minors_mode
    out["id"] = str(uuid.uuid4())
    out["athlete_id"] = body.athlete_id
    if out.get("synthetic_risk") == "high":
        out["nil_band_blocked"] = True
    STORE["assessments"][out["id"]] = out
    return out


@app.post("/retest")
def retest(body: RetestIn) -> dict[str, Any]:
    prev = STORE["assessments"].get(body.previous_assessment_id)
    if not prev:
        raise HTTPException(404, "previous assessment not found")
    nxt = assess(AssessIn(clip_ids=body.clip_ids, athlete_id=body.athlete_id, template=body.template))
    nxt["previous_assessment_id"] = body.previous_assessment_id
    return nxt


@app.get("/nil-band/{athlete_id}")
def nil_band(athlete_id: str) -> dict[str, Any]:
    from services.valuation.engine import estimate_band

    band: NILBand = estimate_band(athlete_id)
    return band.model_dump()


@app.get("/passport/{athlete_id}")
def passport(athlete_id: str) -> dict[str, Any]:
    assessments = [a for a in STORE["assessments"].values() if a["athlete_id"] == athlete_id]
    return {
        "athlete_id": athlete_id,
        "assessments": assessments,
        "consent": {"capture": True, "coach": True, "public": False},
        "tamper_resistant": False,
        "note": "v1 passport is a signed-intent stub. Hash chain lands in verified mode.",
    }


@app.post("/coach/annotate")
def annotate(body: AnnotateIn) -> dict[str, Any]:
    row = STORE["assessments"].get(body.assessment_id)
    if not row:
        raise HTTPException(404, "assessment not found")
    notes = row.setdefault("coach_notes", [])
    notes.append({"coach_id": body.coach_id, "note": body.note})
    return {"ok": True, "count": len(notes)}


@app.get("/roster/{team_id}")
def roster(team_id: str) -> dict[str, Any]:
    athletes = STORE["teams"].setdefault(team_id, {"id": team_id, "athletes": []})
    return athletes
