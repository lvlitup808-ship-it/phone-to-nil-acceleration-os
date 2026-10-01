"""Honesty pin: retest does not open the gate; roster stays an empty stub.

/retest must link assessments without inventing drills or NIL numbers.
/roster is in-memory and empty until a real team is loaded.
"""

from fastapi.testclient import TestClient

from services.api.app import app

client = TestClient(app)


def _clip(athlete_id: str) -> str:
    up = client.post(
        "/upload",
        json={
            "athlete_id": athlete_id,
            "angle": "side",
            "quality_score": 0.9,
            "blur": 0.05,
            "uri": f"demo://{athlete_id}",
        },
    )
    assert up.status_code == 200, up.text
    return up.json()["clip_id"]


def test_retest_stays_blocked_and_does_not_invent_nil():
    clip_a = _clip("ath_retest")
    first = client.post(
        "/assess",
        json={"clip_ids": [clip_a], "athlete_id": "ath_retest", "template": "wr_release"},
    )
    assert first.status_code == 200
    prev_id = first.json()["id"]

    clip_b = _clip("ath_retest")
    nxt = client.post(
        "/retest",
        json={
            "athlete_id": "ath_retest",
            "previous_assessment_id": prev_id,
            "clip_ids": [clip_b],
            "template": "wr_release",
        },
    )
    assert nxt.status_code == 200, nxt.text
    body = nxt.json()
    assert body["previous_assessment_id"] == prev_id
    assert body["id"] != prev_id
    assert "p25" not in body
    assert "p50" not in body
    assert "p75" not in body

    prep = client.get(f"/prescribe/{body['id']}")
    assert prep.status_code == 200
    assert prep.json()["status"] == "blocked_on_golden_set"
    assert prep.json()["drills"] == []

    band = client.get("/nil-band/ath_retest").json()
    assert band["status"] == "blocked_on_golden_set"
    assert band["p25"] is None and band["p50"] is None and band["p75"] is None


def test_roster_stub_has_no_athletes():
    res = client.get("/roster/team_honesty")
    assert res.status_code == 200
    body = res.json()
    assert body["id"] == "team_honesty"
    assert body["athletes"] == []
