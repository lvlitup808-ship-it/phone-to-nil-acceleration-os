"""Honesty pin: /nil-band and estimate_band never emit dollar numbers while the golden-set gate is closed.

No invented NIL numbers, composites, or MAE. Gate stays CLOSED.
"""

from __future__ import annotations

from fastapi.testclient import TestClient

from services.api.app import app
from services.valuation.engine import estimate_band

client = TestClient(app)


def test_nil_band_endpoint_forces_nulls_on_closed_gate() -> None:
    res = client.get("/nil-band/athlete_test")
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "blocked_on_golden_set"
    assert body["p25"] is None
    assert body["p50"] is None
    assert body["p75"] is None
    assert body["confidence"] is None
    assert body["comp_cluster_ids"] == []
    assert body["counterfactuals"] == {}


def test_estimate_band_returns_schema_only_nulls() -> None:
    band = estimate_band("athlete_test")
    assert band.status == "schema_only"
    assert band.p25 is None
    assert band.p50 is None
    assert band.p75 is None
    assert band.confidence is None
    assert band.comp_cluster_ids == []
