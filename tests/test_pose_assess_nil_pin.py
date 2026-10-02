"""Honesty: POST /pose/assess is a cue readout, not a valuation.

Fixture, model, and error responses may name pose_source and cue status.
They must not carry NIL bands, percentiles, MAE, a composite, or a dollar figure.
nil_band_blocked is a boolean gate flag, not a number.
"""

from __future__ import annotations

from fastapi.testclient import TestClient

from services.api.app import app

client = TestClient(app)

_FORBIDDEN = ("p25", "p50", "p75", "mae", "composite", "nil_band", "nil_dollars")


def _assert_no_valuation(body: object) -> None:
    if isinstance(body, dict):
        for key, value in body.items():
            assert key.lower() not in _FORBIDDEN, key
            if key == "nil_band_blocked":
                assert isinstance(value, bool)
            assert not (isinstance(value, str) and "$" in value and any(c.isdigit() for c in value))
            _assert_no_valuation(value)
    elif isinstance(body, list):
        for item in body:
            _assert_no_valuation(item)


def test_pose_assess_fixture_has_no_nil_fields() -> None:
    response = client.post(
        "/pose/assess",
        json={"athlete_id": "ath_pose_pin", "clip_id": "clp_pose_pin", "movement": "release"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["pose_source"] == "fixture"
    assert body["movement"] == "release"
    assert "p25" not in body and "p50" not in body and "p75" not in body
    _assert_no_valuation(body)


def test_pose_assess_break_fixture_has_no_nil_fields() -> None:
    response = client.post(
        "/pose/assess",
        json={"athlete_id": "ath_pose_pin_db", "clip_id": "clp_pose_pin_db", "movement": "break"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["pose_source"] == "fixture"
    assert body["movement"] == "break"
    _assert_no_valuation(body)


def test_pose_assess_real_frames_off_is_reason_only() -> None:
    response = client.post(
        "/pose/assess",
        json={
            "athlete_id": "ath_pose_pin",
            "clip_id": "clp_pose_pin",
            "movement": "release",
            "use_real_frames": True,
        },
    )
    assert response.status_code == 409
    detail = response.json()["detail"]
    assert "POSE_REAL_FRAMES" in detail
    assert "$" not in detail
    assert "p25" not in detail and "mae" not in detail.lower()
