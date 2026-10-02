"""Honesty: upload and the NIL disclaimer must not invent band numbers.

POST /upload is capture only. The legal disclaimer may describe the schema
but must not publish a dollar, percentile, MAE, or composite while the
golden-set gate is closed and p25/p50/p75 stay null.
"""

from __future__ import annotations

import re
from pathlib import Path

from fastapi.testclient import TestClient

from services.api.app import app
from services.api.gates import get_progress, prescription_enabled

client = TestClient(app)
ROOT = Path(__file__).resolve().parents[1]
DISCLAIMER = ROOT / "docs" / "legal" / "nil-disclaimer.md"

_DOLLAR = re.compile(r"\$\s*\d")
_PERCENTILE_VALUE = re.compile(r"\b(p25|p50|p75)\b\s*[:=]\s*\d", re.IGNORECASE)
_MAE = re.compile(r"\bMAE\b\s*[:=]\s*\d", re.IGNORECASE)
_NIL_KEYS = {"p25", "p50", "p75", "nil_band", "mae", "composite", "valuation"}


def test_gate_still_closed() -> None:
    assert prescription_enabled(get_progress()) is False


def test_upload_response_has_no_nil_fields() -> None:
    res = client.post(
        "/upload",
        json={
            "athlete_id": "ath_upload_honesty",
            "angle": "side",
            "quality_score": 0.9,
            "blur": 0.05,
            "uri": "demo://side-honesty",
            "fps": 60,
            "duration_s": 8,
            "stable_first_500ms": True,
        },
    )
    assert res.status_code == 200
    body = res.json()
    assert set(body) == {"clip_id", "quality"}
    assert _NIL_KEYS.isdisjoint(body)
    quality = body["quality"]
    assert _NIL_KEYS.isdisjoint(quality)
    blob = res.text
    assert _DOLLAR.search(blob) is None
    assert _PERCENTILE_VALUE.search(blob) is None
    assert _MAE.search(blob) is None
    assert "composite" not in blob.lower()


def test_nil_disclaimer_has_no_hardcoded_band_numbers() -> None:
    text = DISCLAIMER.read_text()
    assert _DOLLAR.search(text) is None
    assert _PERCENTILE_VALUE.search(text) is None
    assert _MAE.search(text) is None
    lowered = text.lower()
    assert "composite score" not in lowered
    assert "null" in lowered
    assert "golden" in lowered
    assert "no composite" in lowered
