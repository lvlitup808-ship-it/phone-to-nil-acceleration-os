"""Honesty pin: closed golden-set gate forces NIL band numbers to null.

Even if estimate_band were to emit dollars, GET /nil-band must still return
p25/p50/p75/confidence as None and empty clusters while the gate is closed.
Does not open the gate and does not invent numbers.
"""

from __future__ import annotations

from unittest.mock import patch

from fastapi.testclient import TestClient

from packages.shared.models import NILBand
from services.api.app import app
from services.valuation.engine import DISCLAIMER

client = TestClient(app)


def test_closed_gate_nulls_even_if_engine_lies():
    lying = NILBand(
        athlete_id="a1",
        p25=1000.0,
        p50=2500.0,
        p75=5000.0,
        confidence=0.8,
        assumptions=["lying engine"],
        comp_cluster_ids=["fake"],
        disclaimer_version=DISCLAIMER,
        counterfactuals={"x": 1},
        status="schema_only",
    )
    with patch("services.valuation.engine.estimate_band", return_value=lying):
        res = client.get("/nil-band/a1")
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "blocked_on_golden_set"
    assert body["p25"] is None
    assert body["p50"] is None
    assert body["p75"] is None
    assert body["confidence"] is None
    assert body["comp_cluster_ids"] == []
    assert body["counterfactuals"] == {}
    assert body["disclaimer_version"] == DISCLAIMER
