"""Pin POST /ingest/check so retake payloads stay codes, not NIL.

Validator codes are already pinned in test_ingest_codes_pin.py. This file
pins the HTTP response: only accepted / reasons / retake_instruction, every
reason is a documented retake heading, and the body never carries a band,
percentile, MAE, or composite.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from fastapi.testclient import TestClient

from services.api.app import app

client = TestClient(app)
ROOT = Path(__file__).resolve().parents[1]
DOC = (ROOT / "docs/film_first/retake_templates.md").read_text()
DOC_CODES = set(re.findall(r"^## Reason:\s*(\S+)", DOC, flags=re.M))

ALLOWED_KEYS = {"accepted", "reasons", "retake_instruction"}
NIL_KEYS = {
    "p25",
    "p50",
    "p75",
    "confidence",
    "mae",
    "composite",
    "nil_band",
    "valuation",
    "comp_cluster_ids",
}


def _check(**over) -> dict:
    body = {
        "fps": 60,
        "duration_s": 8,
        "angles": ["side", "fortyfive"],
        "stable_first_500ms": True,
    }
    body.update(over)
    res = client.post("/ingest/check", json=body)
    assert res.status_code == 200, res.text
    return res.json()


def _assert_no_nil(payload: dict) -> None:
    assert set(payload) == ALLOWED_KEYS
    assert NIL_KEYS.isdisjoint(payload)
    blob = json.dumps(payload)
    assert not re.search(r"\$\s*\d", blob)
    assert not re.search(r"\bMAE\b", blob, flags=re.I)
    assert "composite" not in blob.lower()
    assert "p25" not in blob and "p50" not in blob and "p75" not in blob


def test_accepted_ingest_has_no_nil_and_empty_reasons() -> None:
    body = _check()
    assert body["accepted"] is True
    assert body["reasons"] == []
    assert body["retake_instruction"] is None
    _assert_no_nil(body)


def test_route_emits_each_documented_retake_code() -> None:
    cases = [
        {"fps": 24},
        {"duration_s": 2},
        {"angles": ["side"]},
        {"stable_first_500ms": False},
        {"filename": "clip.mp4"},
    ]
    emitted: set[str] = set()
    for over in cases:
        body = _check(**over)
        assert body["accepted"] is False
        assert body["reasons"]
        assert body["retake_instruction"]
        _assert_no_nil(body)
        unknown = set(body["reasons"]) - DOC_CODES
        assert not unknown, f"undocumented reason codes: {sorted(unknown)}"
        emitted.update(body["reasons"])
    missing = DOC_CODES - emitted
    assert not missing, f"route did not emit: {sorted(missing)}"
