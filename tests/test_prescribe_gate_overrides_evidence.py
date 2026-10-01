"""Honesty: closed golden-set gate overrides the evidence drill pack.

If EvidencePipeline.run is later wired to return priced drills, GET
/prescribe must still short-circuit to drills: [] and
blocked_on_golden_set. This pin does not open the gate and does not
invent NIL numbers.
"""

from __future__ import annotations

from fastapi.testclient import TestClient

from services.api import app as app_mod
from services.api.app import app
from services.api.gates import get_progress, prescription_enabled

client = TestClient(app)


def _assessment_id() -> str:
    up = client.post(
        "/upload",
        json={
            "athlete_id": "ath_prescribe_gate",
            "angle": "side",
            "quality_score": 0.9,
            "blur": 0.05,
            "uri": "demo://ath_prescribe_gate",
        },
    )
    assert up.status_code == 200, up.text
    assessed = client.post(
        "/assess",
        json={
            "clip_ids": [up.json()["clip_id"]],
            "athlete_id": "ath_prescribe_gate",
            "template": "wr_release",
        },
    )
    assert assessed.status_code == 200, assessed.text
    return assessed.json()["id"]


def test_gate_still_closed() -> None:
    assert prescription_enabled(get_progress()) is False


def test_prescribe_returns_empty_drills_while_gate_closed() -> None:
    aid = _assessment_id()
    res = client.get(f"/prescribe/{aid}")
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "blocked_on_golden_set"
    assert body["drills"] == []
    assert body["primary_cue"] is None
    assert body["grounded"] is False
    missing = body.get("missing") or []
    assert any(str(m).startswith("wr_labeled") for m in missing)
    blob = str(body).lower()
    assert "p25" not in body
    assert "p50" not in body
    assert "p75" not in body
    assert "mae" not in blob
    assert "composite" not in blob
    assert "$" not in blob


def test_prescribe_ignores_evidence_pack_while_gate_closed(monkeypatch) -> None:
    called = {"n": 0}

    def fake_run(query: str, cue: str | None = None):
        called["n"] += 1
        return {
            "drills": [
                {
                    "id": "drill_invented",
                    "name": "priced wall drill",
                    "p25": 25000,
                    "p50": 50000,
                    "p75": 75000,
                    "mae": 0.12,
                    "composite": 88,
                }
            ],
            "comps": [{"p50": 1}],
            "citations": ["chk_fake"],
            "grounded": True,
        }

    aid = _assessment_id()
    monkeypatch.setattr(app_mod.EVIDENCE, "run", fake_run)
    body = client.get(f"/prescribe/{aid}").json()
    assert called["n"] == 0, "closed gate must not call evidence for prescription"
    assert body["status"] == "blocked_on_golden_set"
    assert body["drills"] == []
    assert body.get("p25") is None or "p25" not in body
    assert body.get("p50") is None or "p50" not in body
    assert body.get("p75") is None or "p75" not in body
