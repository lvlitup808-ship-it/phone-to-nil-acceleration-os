"""Honesty: POST /upload is a capture contract, not a valuation.

A rejected clip returns reason codes only. A accepted clip returns a clip id
and quality judgment. Neither payload may carry NIL bands, percentiles, MAE,
or a composite. quality_score is the caller's input, not a computed dollar.
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
            assert not (isinstance(value, str) and "$" in value and any(c.isdigit() for c in value))
            _assert_no_valuation(value)
    elif isinstance(body, list):
        for item in body:
            _assert_no_valuation(item)


def test_upload_accept_has_no_nil_fields() -> None:
    response = client.post(
        "/upload",
        json={"athlete_id": "ath_upload_pin", "angle": "side", "uri": "demo://upload-pin", "fps": 60, "duration_s": 8},
    )
    assert response.status_code == 200
    body = response.json()
    assert set(body) == {"clip_id", "quality"}
    assert body["quality"]["usable"] is True
    assert "nil" not in body["quality"]
    _assert_no_valuation(body)


def test_upload_reject_is_reason_codes_only() -> None:
    response = client.post(
        "/upload",
        json={
            "athlete_id": "ath_upload_reject",
            "angle": "side",
            "uri": "demo://upload-reject",
            "fps": 12,
            "duration_s": 8,
        },
    )
    assert response.status_code == 422
    detail = response.json()["detail"]
    assert "fps_below_30" in detail["reasons"]
    assert "retake_instruction" in detail
    assert "p25" not in detail
    assert "p50" not in detail
    assert "p75" not in detail
    _assert_no_valuation(detail)
