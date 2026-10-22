"""Honesty pin: GET /nil-band never leaks invented dollars or MAE while gate is closed.

No real labeled film exists. The route must return blocked_on_golden_set,
null p25/p50/p75/confidence, empty clusters, and must not contain dollar
signs, MAE, or composite scores in the payload. Does not invent numbers.
"""

from __future__ import annotations

import json

from fastapi.testclient import TestClient

from services.api.app import app

client = TestClient(app)


def test_nil_band_route_nulls_and_no_dollars_while_gate_closed() -> None:
    res = client.get("/nil-band/ath_hourly_pin")
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "blocked_on_golden_set"
    assert body["athlete_id"] == "ath_hourly_pin"
    assert body["p25"] is None
    assert body["p50"] is None
    assert body["p75"] is None
    assert body["confidence"] is None
    assert body["comp_cluster_ids"] == []
    assert body["counterfactuals"] == {}
    # Gate progress must travel with the blocked response.
    assert "progress" in body
    assert body["progress"]["wr_labeled"] == 0
    assert body["progress"]["db_labeled"] == 0
    text = json.dumps(body).lower()
    assert "$" not in text
    assert "mae" not in text
    assert "composite" not in text
    # No numeric band values sneaked in as strings.
    assert "10000" not in text
    assert "25000" not in text
    assert "50000" not in text
