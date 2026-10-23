"""Honesty pin: /nil-band returns nulls while the golden gate is closed.

Even if estimate_band were to return dollars, the route must null them.
No invented NIL numbers, no MAE, no composite. Gate stays CLOSED.
"""

from __future__ import annotations

import json
from unittest.mock import patch

from fastapi.testclient import TestClient

from packages.shared.models import NILBand
from services.api.app import app

client = TestClient(app)

FORBIDDEN = ("mae", "composite", "nil_dollars", "p25", "p50", "p75")
INVENTED = ("2500", "6000", "14000", "0.41")


def test_nil_band_nulls_while_gate_closed():
    body = client.get("/nil-band/ath_nil_guard").json()
    assert body["status"] == "blocked_on_golden_set"
    assert body["p25"] is None
    assert body["p50"] is None
    assert body["p75"] is None
    assert body.get("confidence") is None
    assert body.get("comp_cluster_ids") == []
    text = json.dumps(body)
    for needle in INVENTED:
        assert needle not in text
    assert "mae" not in text.lower()
    assert "composite" not in text.lower()


def test_nil_band_nulls_even_if_engine_lies():
    lying = NILBand(
        athlete_id="ath_lie",
        p25=2500,
        p50=6000,
        p75=14000,
        confidence=0.41,
        assumptions=["lying"],
        comp_cluster_ids=["fake"],
        disclaimer_version="test",
        counterfactuals={"up": 10000},
        status="computed",
    )
    with patch("services.valuation.engine.estimate_band", return_value=lying):
        body = client.get("/nil-band/ath_lie").json()
    assert body["status"] == "blocked_on_golden_set"
    assert body["p25"] is None
    assert body["p50"] is None
    assert body["p75"] is None
    assert body["confidence"] is None
    assert body["comp_cluster_ids"] == []
    assert body.get("counterfactuals") == {}
    text = json.dumps(body)
    for needle in INVENTED:
        assert needle not in text
