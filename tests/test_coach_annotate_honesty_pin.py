"""Honesty: /coach/annotate only stores a note. It cannot mint NIL or MAE.

A future "coach score" field on annotate would look like labeled film.
Keep the write path to coach_notes only.
"""

from fastapi.testclient import TestClient

from services.api.app import STORE, app

client = TestClient(app)

FORBIDDEN = ("p25", "p50", "p75", "mae", "composite", "nil_dollars", "confidence_band")


def _assessment() -> str:
    up = client.post(
        "/upload",
        json={"athlete_id": "ath_ann", "angle": "side", "uri": "demo://ann"},
    )
    assert up.status_code == 200
    assessed = client.post(
        "/assess",
        json={
            "clip_ids": [up.json()["clip_id"]],
            "athlete_id": "ath_ann",
            "template": "wr_release",
        },
    )
    assert assessed.status_code == 200
    return assessed.json()["id"]


def test_annotate_unknown_assessment_is_404():
    res = client.post(
        "/coach/annotate",
        json={"assessment_id": "missing", "coach_id": "c1", "note": "ok"},
    )
    assert res.status_code == 404


def test_annotate_appends_note_only():
    aid = _assessment()
    res = client.post(
        "/coach/annotate",
        json={"assessment_id": aid, "coach_id": "coach_a", "note": "late first step"},
    )
    assert res.status_code == 200
    body = res.json()
    assert body == {"ok": True, "count": 1}
    for key in FORBIDDEN:
        assert key not in body
    row = STORE["assessments"][aid]
    assert row["coach_notes"] == [{"coach_id": "coach_a", "note": "late first step"}]
    for key in FORBIDDEN:
        assert key not in row


def test_annotate_second_note_increments_count_not_scores():
    aid = _assessment()
    client.post(
        "/coach/annotate",
        json={"assessment_id": aid, "coach_id": "coach_a", "note": "one"},
    )
    res = client.post(
        "/coach/annotate",
        json={"assessment_id": aid, "coach_id": "coach_b", "note": "two"},
    )
    assert res.json()["count"] == 2
    row = STORE["assessments"][aid]
    assert [n["note"] for n in row["coach_notes"]] == ["one", "two"]
    cues = row.get("cues") or []
    for cue in cues:
        assert cue.get("value") is None
