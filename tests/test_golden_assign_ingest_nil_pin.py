"""Honesty: assignments, label spec, and ingest check carry no NIL numbers.

GET /golden/assignments is an unfilmed work order. GET /golden/labels/{id}/spec
lists events and frozen cues. POST /ingest/check returns accept/reasons only.
None of them may publish p25/p50/p75, MAE, a composite, or a dollar band.
Gate stays closed. No Slice 3.
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


def test_golden_assignments_are_unfilmed_and_not_a_valuation() -> None:
    response = client.get("/golden/assignments")
    assert response.status_code == 200
    body = response.json()
    assert body["dashboard"]["wr_labeled"] == "0/10"
    assert body["dashboard"]["db_labeled"] == "0/10"
    assert body["dashboard"]["inter_rater"] == "pending"
    assert body["assignments"]
    for row in body["assignments"]:
        assert row["status"] == "unfilmed"
        assert row.get("nil_band") is None
    _assert_no_valuation(body)


def test_label_spec_lists_frozen_cues_not_valuation() -> None:
    response = client.get("/golden/labels/clp_0001/spec")
    assert response.status_code == 200
    body = response.json()
    assert body["clip_id"] == "clp_0001"
    assert body["movement"] == "release"
    assert body["position_target"] == "WR"
    assert "motion_start" in body["events"]
    assert "first_step_separation" in body["cues"]
    assert "mae" not in body
    _assert_no_valuation(body)

    missing = client.get("/golden/labels/clp_9999/spec")
    assert missing.status_code == 404


def test_ingest_check_is_reasons_only() -> None:
    ok = client.post(
        "/ingest/check",
        json={
            "fps": 60,
            "duration_s": 8,
            "angles": ["side", "fortyfive"],
            "stable_first_500ms": True,
        },
    )
    assert ok.status_code == 200
    body = ok.json()
    assert body["accepted"] is True
    assert body["reasons"] == []
    assert "nil_band" not in body
    _assert_no_valuation(body)

    bad = client.post(
        "/ingest/check",
        json={"fps": 24, "duration_s": 8, "angles": ["side", "fortyfive"], "stable_first_500ms": True},
    )
    assert bad.status_code == 200
    rejected = bad.json()
    assert rejected["accepted"] is False
    assert "fps_below_30" in rejected["reasons"]
    _assert_no_valuation(rejected)
