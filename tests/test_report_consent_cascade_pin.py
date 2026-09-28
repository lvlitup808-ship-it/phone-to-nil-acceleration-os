"""Honesty: report after consent revoke does not leak cues.

GET /report/{id} runs CONSENT.cascade. After revoke, assessment_status
must be scope_revoked and cues/events must be empty so a revoked athlete
cannot be reconstructed from the report payload.
"""

from fastapi.testclient import TestClient

from services.api.app import STORE, app
from services.api.film import CONSENT

client = TestClient(app)


def test_report_after_revoke_is_scope_revoked_no_cues():
    cid = client.post(
        "/consent", json={"athlete_id": "ath_report_pin", "consent_scope": ["capture", "coach"]}
    ).json()["consent_id"]
    up = client.post(
        "/upload",
        json={
            "athlete_id": "ath_report_pin",
            "angle": "side",
            "uri": "demo://report-pin",
            "consent_id": cid,
        },
    ).json()
    assess = client.post(
        "/assess",
        json={"clip_ids": [up["clip_id"]], "athlete_id": "ath_report_pin"},
    ).json()
    aid = assess["id"]
    # Mutate the stored row so report's cascade has consent_id.
    CONSENT.attach(STORE["assessments"][aid], cid)
    client.post(f"/consent/{cid}/revoke")
    body = client.get(f"/report/{aid}").json()
    assert body.get("assessment_status") == "scope_revoked"
    assert body.get("cues", []) == []
    assert body.get("events", []) == []


def test_report_unknown_is_404():
    r = client.get("/report/does-not-exist")
    assert r.status_code == 404
