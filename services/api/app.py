from __future__ import annotations

import os
import re
import shutil
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from packages.biomech.features import extract_cues
from packages.capture.contract import validate_ingest
from packages.evidence.pipeline import EvidencePipeline
from packages.judgment.client import JudgmentClient
from packages.shared.models import ClipQuality, PositionTemplate
from services.api.film import CONSENT
from services.api.film import router as film_router
from services.api.gates import gate_state

app = FastAPI(
    title="Phone-to-NIL Acceleration OS",
    version="0.2.1",
    description="Capture → Assess → Prescribe → Re-test → Value",
)

STORE: dict[str, dict[str, Any]] = {"clips": {}, "assessments": {}, "athletes": {}, "teams": {}}
JUDGE = JudgmentClient()
EVIDENCE = EvidencePipeline(JUDGE)
app.include_router(film_router)
CLIP_ID_RE = re.compile(r"[A-Za-z0-9_-]{1,64}")


class UploadIn(BaseModel):
    athlete_id: str
    angle: str = Field(pattern="^(side|fortyfive|front)$")
    quality_score: float = 0.8
    blur: float = 0.1
    uri: str
    fps: float = 60
    duration_s: float = 8
    stable_first_500ms: bool = True
    consent_id: str | None = None


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
    consent_id: str | None = None


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/upload")
def upload(body: UploadIn) -> dict[str, Any]:
    contract = validate_ingest(
        fps=body.fps,
        duration_s=body.duration_s,
        angles=[body.angle],
        stable_first_500ms=body.stable_first_500ms,
        pair_complete=True,
    )
    if not contract.accepted:
        raise HTTPException(status_code=422, detail={"reasons": contract.reasons, "retake_instruction": contract.retake_instruction})
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
        retake_instructions=None if usable else "Retake side-on, 5-10s, phone stable, full body in frame.",
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
        "created_at": datetime.now(UTC).isoformat(),
    }
    STORE["assessments"][assessment_id] = row
    return row


@app.get("/report/{assessment_id}")
def report(assessment_id: str) -> dict[str, Any]:
    row = STORE["assessments"].get(assessment_id)
    if not row:
        raise HTTPException(404, "assessment not found")
    return CONSENT.cascade(row)


@app.get("/prescribe/{assessment_id}")
def prescribe(assessment_id: str) -> dict[str, Any]:
    row = STORE["assessments"].get(assessment_id)
    if not row:
        raise HTTPException(404, "assessment not found")
    row = CONSENT.cascade(row)
    if row.get("assessment_status") == "scope_revoked":
        raise HTTPException(403, "consent revoked")
    gate = gate_state()
    if gate["status"] != "open":
        return {"assessment_id": assessment_id, "primary_cue": None, "drills": [], "grounded": False, **gate}
    if not row.get("cues"):
        return {"assessment_id": assessment_id, "primary_cue": None, "drills": [], "grounded": False, "status": "open"}
    first = row["cues"][0]
    cue = first.get("id") or first.get("name")
    pack = EVIDENCE.run("drill prescription", cue)
    reviewed = [d for d in pack["drills"] if d.get("coach_reviewed") is not False]
    return {
        "assessment_id": assessment_id,
        "primary_cue": cue,
        "drills": reviewed,
        "grounded": pack["grounded"],
        "status": "open",
    }


def artifacts_dir_for(clip_id: str) -> Path:
    """Debug-artifact folder for a clip. Refuses ids that could escape ARTIFACTS_DIR."""
    if not CLIP_ID_RE.fullmatch(clip_id):
        raise HTTPException(422, "clip_id must match [A-Za-z0-9_-]{1,64}")
    root = Path(os.getenv("ARTIFACTS_DIR", "artifacts")).resolve()
    folder = (root / clip_id).resolve()
    if folder.parent != root:
        raise HTTPException(422, "clip_id resolves outside the artifacts directory")
    return folder


def _purge_for_consent(consent: dict[str, Any]) -> dict[str, int]:
    """Delete what a revoked consent covered: clips, pose debug files; blank assessments."""
    cid = consent["consent_id"]
    clips = [
        k
        for k, v in STORE["clips"].items()
        if v.get("consent_id") == cid or (not v.get("consent_id") and v.get("athlete_id") == consent["athlete_id"])
    ]
    for k in clips:
        del STORE["clips"][k]
    debug = 0
    for row in STORE["assessments"].values():
        if row.get("consent_id") != cid:
            continue
        CONSENT.cascade(row)
        for clip_id in (row.get("assessment_lineage") or {}).get("clip_ids", []):
            if CLIP_ID_RE.fullmatch(clip_id):
                folder = artifacts_dir_for(clip_id)
                if folder.is_dir():
                    shutil.rmtree(folder)
                    debug += 1
        row["artifacts"] = {}
    return {"clips": len(clips), "pose_debug": debug}


CONSENT.purgers.append(_purge_for_consent)


@app.post("/pose/assess")
def pose_assess(body: PoseAssessIn) -> dict[str, Any]:
    from services.cv_worker.pipeline_v2 import run_pose_assessment

    if body.consent_id:
        consent = CONSENT.consents.get(body.consent_id)
        if consent is None:
            raise HTTPException(404, "consent not found")
        if consent.get("revoked"):
            # Checked before the pipeline runs so no debug files are written for revoked consent.
            raise HTTPException(403, "consent revoked")
    out = run_pose_assessment(
        movement=body.movement,
        clip_id=body.clip_id,
        side_clip=body.side_clip,
        height_cm=body.height_cm,
        athlete_id=body.athlete_id,
        artifacts_dir=artifacts_dir_for(body.clip_id),
        judge=JUDGE,
    )
    out["minors_mode"] = body.minors_mode
    out["id"] = str(uuid.uuid4())
    out["athlete_id"] = body.athlete_id
    out["labeling_protocol_version"] = "1.0.0"
    if body.consent_id:
        CONSENT.attach(out, body.consent_id)
    if out.get("synthetic_risk") == "high":
        out["nil_band_blocked"] = True
    STORE["assessments"][out["id"]] = out
    return CONSENT.cascade(out)


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

    band = estimate_band(athlete_id).model_dump()
    gate = gate_state()
    if gate["status"] != "open":
        band.update(gate)
    return band


@app.get("/passport/{athlete_id}")
def passport(athlete_id: str) -> dict[str, Any]:
    consent = CONSENT.active_scopes(athlete_id)
    gate = gate_state()
    if gate["status"] != "open":
        return {"athlete_id": athlete_id, "assessments": [], "consent": consent, **gate}
    assessments = [CONSENT.cascade(dict(a)) for a in STORE["assessments"].values() if a["athlete_id"] == athlete_id]
    assessments = [a for a in assessments if a.get("assessment_status") != "scope_revoked"]
    return {"athlete_id": athlete_id, "assessments": assessments, "consent": consent, "status": "open"}


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
    return STORE["teams"].setdefault(team_id, {"id": team_id, "athletes": []})
