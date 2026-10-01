"""Honesty: GET /report must not mint NIL dollars, MAE, or a composite.

Assessments store evidence comps as placeholders. A report that copies a
numeric band would look like a valuation. Gate stays closed; this pin does
not open it.
"""

import json

from fastapi.testclient import TestClient

from services.api.app import app

client = TestClient(app)

FORBIDDEN_KEYS = ("p25", "p50", "p75", "mae", "composite", "nil_dollars", "confidence")


def _report() -> dict:
    up = client.post(
        "/upload",
        json={"athlete_id": "ath_rpt", "angle": "side", "uri": "demo://rpt"},
    )
    assert up.status_code == 200
    assessed = client.post(
        "/assess",
        json={
            "clip_ids": [up.json()["clip_id"]],
            "athlete_id": "ath_rpt",
            "template": "wr_release",
        },
    )
    assert assessed.status_code == 200
    aid = assessed.json()["id"]
    res = client.get(f"/report/{aid}")
    assert res.status_code == 200
    return res.json()


def test_report_unknown_assessment_is_404():
    res = client.get("/report/missing-assessment")
    assert res.status_code == 404


def test_report_has_no_nil_or_mae_fields():
    body = _report()
    assert "cues" in body
    for key in FORBIDDEN_KEYS:
        assert key not in body
    blob = json.dumps(body).lower()
    assert "mae" not in blob
    assert "$" not in blob
    assert "composite" not in blob
    for cue in body["cues"]:
        assert cue.get("value") is None


def test_report_evidence_comps_stay_null_placeholders():
    body = _report()
    evidence = body.get("evidence") or {}
    comps = evidence.get("comps") or []
    assert comps, "expected placeholder comps so a numeric leak would be visible"
    for comp in comps:
        assert comp.get("status") == "placeholder"
        assert comp.get("p25") is None
        assert comp.get("p50") is None
        assert comp.get("p75") is None
        assert comp.get("n") is None
        assumptions = " ".join(comp.get("assumptions") or []).lower()
        assert "no comp data" in assumptions
