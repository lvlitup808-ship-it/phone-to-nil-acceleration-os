"""Pin: closed gate nulls NIL numbers even if the valuation engine lies.

No real comps exist. estimate_band returns nulls today. This test forces a lying engine and asserts GET /nil-band still returns p25/p50/p75 = null, confidence = null, empty clusters while the golden-set gate is closed.
"""

from __future__ import annotations

from unittest.mock import patch

from fastapi.testclient import TestClient

from packages.shared.models import NILBand
from services.api.app import app

client = TestClient(app)


def test_nil_band_nulls_lying_engine_while_gate_closed() -> None:
    lying = NILBand(
        athlete_id="a1",
        p25=10000.0,
        p50=25000.0,
        p75=50000.0,
        confidence=0.8,
        assumptions=["lying engine"],
        comp_cluster_ids=["fake"],
        disclaimer_version="test",
        counterfactuals={"fake": 1},
        status="open",
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
    # Gate fields must still be present
    assert "progress" in body or "wr_labeled" in body.get("progress", {})
