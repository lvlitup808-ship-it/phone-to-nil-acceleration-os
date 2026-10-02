"""Honesty: POST /upload must not publish an NIL point estimate.

Capture returns a clip id and a usability judgment. While the golden-set
gate is closed, the payload must not carry a dollar amount, a numeric
p25/p50/p75, MAE, or a composite. A 422 retake is the same rule.
"""

from __future__ import annotations

import json
import re

from fastapi.testclient import TestClient

from services.api.app import app

client = TestClient(app)

_DOLLAR = re.compile(r"\$\s*\d")
_PERCENTILE = re.compile(r"\b(p25|p50|p75)\b\s*[:=]\s*\d", re.IGNORECASE)
_MAE = re.compile(r"\bMAE\b\s*[:=]\s*\d", re.IGNORECASE)

_OK = {
    "athlete_id": "a1",
    "angle": "side",
    "quality_score": 0.9,
    "blur": 0.05,
    "uri": "demo://side",
}


def _assert_no_nil(payload: object) -> None:
    text = json.dumps(payload)
    lowered = text.lower()
    assert _DOLLAR.search(text) is None
    assert _PERCENTILE.search(text) is None
    assert _MAE.search(text) is None
    assert "composite" not in lowered
    assert "your nil is" not in lowered
    if isinstance(payload, dict):
        for key in ("p25", "p50", "p75", "mae", "nil_band", "valuation"):
            assert key not in payload


def test_upload_accept_has_clip_and_no_nil_numbers() -> None:
    res = client.post("/upload", json=_OK)
    assert res.status_code == 200
    body = res.json()
    assert "clip_id" in body
    assert set(body) <= {"clip_id", "quality"}
    quality = body["quality"]
    assert quality["usable"] is True
    assert "score" in quality
    _assert_no_nil(body)


def test_upload_reject_has_reasons_and_no_nil_numbers() -> None:
    res = client.post("/upload", json={**_OK, "fps": 10, "duration_s": 1})
    assert res.status_code == 422
    detail = res.json()["detail"]
    assert "reasons" in detail
    _assert_no_nil(detail)
