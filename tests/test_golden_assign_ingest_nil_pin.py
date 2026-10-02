"""Honesty: golden-set queue, label spec, and ingest check carry no NIL numbers.

Assignments and the label spec are coach workflow. Ingest check is a capture
contract. None of them is a valuation. Payloads must not publish p25/p50/p75,
MAE, a composite, or a dollar band while the golden set is still pending.
"""

from __future__ import annotations

from fastapi.testclient import TestClient

from services.api.app import app
from services.api.gates import get_progress, prescription_enabled

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


def test_gate_still_closed_before_queue_reads() -> None:
    assert prescription_enabled(get_progress()) is False
    assert get_progress()["wr_labeled"] == 0
    assert get_progress()["db_labeled"] == 0


def test_assignments_and_label_spec_are_not_a_valuation() -> None:
    assignments = client.get("/golden/assignments")
    assert assignments.status_code == 200
    body = assignments.json()
    assert body["dashboard"]["wr_labeled"] == "0/10"
    assert body["dashboard"]["db_labeled"] == "0/10"
    _assert_no_valuation(body)

    spec = client.get("/golden/labels/clp_0001/spec")
    assert spec.status_code == 200
    spec_body = spec.json()
    assert spec_body["clip_id"] == "clp_0001"
    assert spec_body["movement"] == "release"
    assert spec_body["events"]
    assert spec_body["cues"]
    assert "mae" not in spec_body
    _assert_no_valuation(spec_body)

    missing = client.get("/golden/labels/clp_not_real/spec")
    assert missing.status_code == 404
    _assert_no_valuation(missing.json())


def test_ingest_check_accept_and_reject_carry_no_nil_numbers() -> None:
    accepted = client.post(
        "/ingest/check",
        json={
            "filename": "ath_0042_WR_release_side_20260925.mp4",
            "fps": 60,
            "duration_s": 8,
            "angles": ["side", "fortyfive"],
            "stable_first_500ms": True,
            "pair_complete": True,
        },
    )
    assert accepted.status_code == 200
    ok = accepted.json()
    assert ok["accepted"] is True
    assert ok["reasons"] == []
    _assert_no_valuation(ok)

    rejected = client.post(
        "/ingest/check",
        json={
            "filename": "clip.mp4",
            "fps": 24,
            "duration_s": 2,
            "angles": ["side"],
            "stable_first_500ms": False,
            "pair_complete": False,
        },
    )
    assert rejected.status_code == 200
    bad = rejected.json()
    assert bad["accepted"] is False
    assert "bad_filename" in bad["reasons"]
    assert bad["retake_instruction"]
    assert "$" not in bad["retake_instruction"]
    _assert_no_valuation(bad)
