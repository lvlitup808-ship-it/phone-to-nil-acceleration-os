"""Honesty pin: a coach note is not a golden-set label.

POST /coach/annotate stores a note on an in-memory assessment. It must
not write labels/, must not count as film, and must not move GET /gates/golden.
"""

from fastapi.testclient import TestClient

from services.api.app import app
from services.api.gates import GOLDEN_DIR, get_progress, gate_state

client = TestClient(app)


def _assessment() -> str:
    up = client.post(
        "/upload",
        json={"athlete_id": "ath_note_gate", "angle": "side", "uri": "demo://note-gate"},
    )
    assert up.status_code == 200
    assessed = client.post(
        "/assess",
        json={
            "clip_ids": [up.json()["clip_id"]],
            "athlete_id": "ath_note_gate",
            "template": "wr_release",
        },
    )
    assert assessed.status_code == 200
    return assessed.json()["id"]


def test_annotate_does_not_open_golden_gate():
    before = get_progress()
    labels = GOLDEN_DIR / "labels"
    before_names = sorted(p.name for p in labels.glob("*.json")) if labels.is_dir() else []
    aid = _assessment()
    res = client.post(
        "/coach/annotate",
        json={
            "assessment_id": aid,
            "coach_id": "coach_note",
            "note": "this note is not a film label",
        },
    )
    assert res.status_code == 200
    assert res.json() == {"ok": True, "count": 1}

    after = get_progress()
    assert after == before
    assert after["wr_labeled"] == 0
    assert after["db_labeled"] == 0
    state = gate_state()
    assert state["status"] == "blocked_on_golden_set"
    assert "mae" not in state
    assert "accuracy" not in state
    live = client.get("/gates/golden").json()
    assert live["status"] == "blocked_on_golden_set"
    assert live["progress"]["wr_labeled"] == 0
    assert live["progress"]["db_labeled"] == 0
    after_names = sorted(p.name for p in labels.glob("*.json")) if labels.is_dir() else []
    assert after_names == before_names
