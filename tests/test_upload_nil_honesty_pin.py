"""Honesty pin: /upload is ingest only. It must not publish NIL numbers.

Capture may accept or reject a clip. It must not emit a band, percentile,
MAE, or composite. A successful upload is not labeled film and does not
open the golden-set gate.
"""

from fastapi.testclient import TestClient

from services.api.app import app

client = TestClient(app)

_FORBIDDEN = ("p25", "p50", "p75", "mae", "composite", "nil_band", "currency")


def _assert_no_nil(payload: object) -> None:
    blob = str(payload).lower()
    for key in _FORBIDDEN:
        assert key not in blob
    assert "$" not in blob


def test_upload_accept_has_quality_only() -> None:
    res = client.post(
        "/upload",
        json={
            "athlete_id": "ath_upload_ok",
            "angle": "side",
            "quality_score": 0.9,
            "blur": 0.05,
            "uri": "demo://upload-ok",
            "fps": 60,
            "duration_s": 8,
            "stable_first_500ms": True,
        },
    )
    assert res.status_code == 200, res.text
    body = res.json()
    assert set(body) == {"clip_id", "quality"}
    assert set(body["quality"]) == {"score", "usable", "reasons", "retake_instructions"}
    assert body["quality"]["usable"] is True
    _assert_no_nil(body)


def test_upload_contract_reject_has_retake_not_nil() -> None:
    res = client.post(
        "/upload",
        json={
            "athlete_id": "ath_upload_fps",
            "angle": "side",
            "quality_score": 0.9,
            "blur": 0.05,
            "uri": "demo://upload-fps",
            "fps": 24,
            "duration_s": 8,
            "stable_first_500ms": True,
        },
    )
    assert res.status_code == 422
    detail = res.json()["detail"]
    assert "fps_below_30" in detail["reasons"]
    assert detail["retake_instruction"]
    _assert_no_nil(detail)


def test_upload_unusable_quality_has_no_nil() -> None:
    res = client.post(
        "/upload",
        json={
            "athlete_id": "ath_upload_bad",
            "angle": "side",
            "quality_score": 0.2,
            "blur": 0.4,
            "uri": "demo://upload-bad",
            "fps": 60,
            "duration_s": 8,
            "stable_first_500ms": True,
        },
    )
    assert res.status_code == 422
    detail = res.json()["detail"]
    assert detail["usable"] is False
    assert detail["retake_instructions"]
    _assert_no_nil(detail)
