from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from packages.capture.contract import validate_ingest
from packages.consent.store import ConsentStore
from services.api.gates import gate_state
from services.cv_worker.ingest.naming import validate_name

router = APIRouter()
CONSENT = ConsentStore()
SHARE: dict[str, dict[str, Any]] = {}


class IngestCheckIn(BaseModel):
    fps: float
    duration_s: float
    angles: list[str]
    stable_first_500ms: bool = True
    pair_complete: bool | None = None
    filename: str | None = None


class ConsentGrantIn(BaseModel):
    athlete_id: str
    consent_scope: list[str] = Field(default_factory=lambda: ["capture", "coach"])
    parent_attested: bool = False


class ShareIn(BaseModel):
    athlete_id: str
    recipient: str
    ttl_days: int = 30


def _purge_share_links(consent: dict[str, Any]) -> dict[str, int]:
    n = 0
    for row in SHARE.values():
        if row["athlete_id"] == consent["athlete_id"] and not row["revoked"]:
            row["revoked"] = True
            n += 1
    return {"passport_share": n}


CONSENT.purgers.append(_purge_share_links)


@router.post("/ingest/check")
def ingest_check(body: IngestCheckIn) -> dict[str, Any]:
    if body.filename:
        ok, msg = validate_name(body.filename)
        if not ok:
            return {"accepted": False, "reasons": ["bad_filename"], "retake_instruction": msg}
    d = validate_ingest(
        fps=body.fps,
        duration_s=body.duration_s,
        angles=body.angles,
        stable_first_500ms=body.stable_first_500ms,
        pair_complete=body.pair_complete,
    )
    return {"accepted": d.accepted, "reasons": d.reasons, "retake_instruction": d.retake_instruction}


@router.post("/consent")
def grant_consent(body: ConsentGrantIn) -> dict[str, Any]:
    return CONSENT.grant(body.athlete_id, body.consent_scope, parent=body.parent_attested)


@router.post("/consent/{consent_id}/revoke")
def revoke_consent(consent_id: str) -> dict[str, Any]:
    try:
        return CONSENT.revoke(consent_id, artifacts=["clips", "pose_debug", "passport_share"])
    except KeyError:
        raise HTTPException(404, "consent not found") from None


@router.post("/share-link")
def share_link(body: ShareIn) -> dict[str, Any]:
    ttl = min(max(body.ttl_days, 1), 30)
    expires = datetime.now(UTC) + timedelta(days=ttl)
    token = f"shr_{body.athlete_id}_{expires.strftime('%Y%m%d')}"
    SHARE[token] = {
        "token": token,
        "athlete_id": body.athlete_id,
        "recipient": body.recipient,
        "expires_at": expires.isoformat(),
        "revoked": False,
    }
    return SHARE[token]


@router.post("/share-link/{token}/revoke")
def revoke_share(token: str) -> dict[str, Any]:
    row = SHARE.get(token)
    if not row:
        raise HTTPException(404, "link not found")
    row["revoked"] = True
    return row


@router.get("/golden/assignments")
def assignments() -> dict[str, Any]:
    import json
    from pathlib import Path

    path = Path(__file__).resolve().parents[2] / "data/golden_set/assignments.json"
    return json.loads(path.read_text())


@router.get("/gates/golden")
def golden_gate() -> dict[str, Any]:
    return gate_state()


@router.get("/nil-band/{athlete_id}/scenarios")
def nil_scenarios(athlete_id: str) -> dict[str, Any]:
    return {
        "athlete_id": athlete_id,
        "status": "schema_only",
        "slice": 4,
        "scenarios": [],
        "note": "Projected P4-comp bands wait for a labeled golden set. No numbers invented.",
    }


@router.get("/position-fit/{athlete_id}")
def position_fit(athlete_id: str) -> dict[str, Any]:
    return {
        "athlete_id": athlete_id,
        "status": "blocked_on_golden_set",
        "clusters": [],
        "note": "Will report cluster similarity + confidence. Will not say you are a nickel.",
    }
