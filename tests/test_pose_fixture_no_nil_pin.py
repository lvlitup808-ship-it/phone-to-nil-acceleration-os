"""Honesty: default /pose/assess is fixture poses and must not publish NIL or MAE.

Fixture cues are not coach labels. While the golden-set gate is closed, the
default pose response may describe synthetic fixture mechanics. It must not
attach MAE, a composite, or p25/p50/p75 dollars, and it must not claim the
clip is labeled film.
"""

from __future__ import annotations

import json
import re

from fastapi.testclient import TestClient

from services.api.app import app

client = TestClient(app)

_DOLLAR = re.compile(r"\$\s*\d")
_FORBIDDEN_KEYS = {"mae", "accuracy", "composite", "p25", "p50", "p75", "nil_dollars"}


def _keys(obj: object, found: set[str] | None = None) -> set[str]:
    if found is None:
        found = set()
    if isinstance(obj, dict):
        for key, value in obj.items():
            found.add(str(key).lower())
            _keys(value, found)
    elif isinstance(obj, list):
        for item in obj:
            _keys(item, found)
    return found


def _post(movement: str) -> dict:
    res = client.post(
        "/pose/assess",
        json={"athlete_id": "ath_pose_pin", "clip_id": "clp_pose_pin", "movement": movement},
    )
    assert res.status_code == 200
    return res.json()


def test_default_pose_assess_is_fixture_and_pending() -> None:
    body = _post("release")
    assert body["pose_source"] == "fixture"
    assert body["golden_set"] == "pending"
    assert body.get("assessment_status") != "error"
    assert _keys(body).isdisjoint(_FORBIDDEN_KEYS)
    assert _DOLLAR.search(json.dumps(body)) is None
    assert "coach_label" not in _keys(body)
    assert "labeled_film" not in _keys(body)


def test_fixture_pose_does_not_claim_measured_accuracy() -> None:
    body = _post("break")
    assert body["pose_source"] == "fixture"
    blob = json.dumps(body).lower()
    assert "mae" not in blob
    assert "composite" not in blob
    assert body["cues"], "fixture path should still return frozen cues"
    for cue in body["cues"]:
        assert cue.get("coach_labeled") is not True
        assert "mae" not in json.dumps(cue).lower()
