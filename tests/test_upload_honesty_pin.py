"""Honesty: POST /upload is capture-only.

A usable clip returns clip_id + quality. It must not invent NIL bands,
MAE, composites, or measured cue values. Reject payloads stay retake
reasons, not valuations.
"""

from __future__ import annotations

import json

from fastapi.testclient import TestClient

from services.api.app import app

client = TestClient(app)

FORBIDDEN = {
    "p25",
    "p50",
    "p75",
    "mae",
    "composite",
    "nil_band",
    "valuation",
    "confidence",
    "cue_value",
    "shin_angle",
}


def _flat_keys(obj: object) -> set[str]:
    found: set[str] = set()
    if isinstance(obj, dict):
        for key, value in obj.items():
            found.add(str(key).lower())
            found |= _flat_keys(value)
    elif isinstance(obj, list):
        for item in obj:
            found |= _flat_keys(item)
    return found


def test_upload_success_is_clip_and_quality_only():
    res = client.post(
        "/upload",
        json={
            "athlete_id": "ath_upload_pin",
            "angle": "side",
            "quality_score": 0.9,
            "blur": 0.05,
            "uri": "demo://ath_upload_pin",
            "fps": 60,
            "duration_s": 8,
            "stable_first_500ms": True,
        },
    )
    assert res.status_code == 200, res.text
    body = res.json()
    assert set(body.keys()) == {"clip_id", "quality"}
    assert body["quality"]["usable"] is True
    assert body["quality"]["score"] == 0.9
    leaked = _flat_keys(body) & FORBIDDEN
    assert leaked == set(), leaked
    blob = json.dumps(body).lower()
    assert "mae" not in blob
    assert "$" not in blob


def test_upload_reject_is_retake_not_valuation():
    res = client.post(
        "/upload",
        json={
            "athlete_id": "ath_upload_pin",
            "angle": "side",
            "quality_score": 0.9,
            "blur": 0.05,
            "uri": "demo://ath_upload_pin_reject",
            "fps": 24,
            "duration_s": 8,
            "stable_first_500ms": True,
        },
    )
    assert res.status_code == 422, res.text
    detail = res.json()["detail"]
    assert "fps_below_30" in detail["reasons"]
    leaked = _flat_keys(detail) & FORBIDDEN
    assert leaked == set(), leaked
    blob = json.dumps(detail).lower()
    assert "mae" not in blob
    assert "$" not in blob
    assert "p25" not in blob
