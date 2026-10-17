"""Honesty: closed golden-set gate forces NIL band numerics to null.

Even if estimate_band is made to return invented dollars, GET /nil-band
must null them while the gate is closed. Does not invent numbers, does not
open the gate, does not start Slice 3.
"""

from __future__ import annotations

from unittest.mock import patch

from fastapi.testclient import TestClient

from services.api.app import app
from services.valuation.engine import estimate_band

client = TestClient(app)


def test_closed_gate_nulls_even_if_engine_lies():
    fake = estimate_band("ath_lie")
    # Force non-null numbers as if a bad engine update shipped.
    fake.p25 = 1000.0
    fake.p50 = 5000.0
    fake.p75 = 10000.0
    fake.confidence = 0.9
    fake.comp_cluster_ids = ["fake_cluster"]
    fake.status = "computed"
    fake.counterfactuals = {"plus_one_mph": 2000.0}

    with patch("services.valuation.engine.estimate_band", return_value=fake):
        body = client.get("/nil-band/ath_lie").json()

    assert body["status"] == "blocked_on_golden_set"
    assert body["p25"] is None
    assert body["p50"] is None
    assert body["p75"] is None
    assert body.get("confidence") is None
    assert body.get("comp_cluster_ids") == []
    assert body.get("counterfactuals") == {}
    assert "blocked_on_golden_set" in body.get("status", "")
