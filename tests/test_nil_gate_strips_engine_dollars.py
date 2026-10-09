"""Honesty: a closed gate must not forward invented NIL dollars.

estimate_band() is null today. If a future engine returns p25/p50/p75,
confidence, clusters, or counterfactuals while the golden-set gate is closed,
GET /nil-band on the product API and the valuation service must still null
those fields. Status stays blocked_on_golden_set.
"""

from __future__ import annotations

from fastapi.testclient import TestClient

from services.api.app import app
from services.valuation.app import app as valuation_app

client = TestClient(app)
val_client = TestClient(valuation_app)


class _InventedBand:
    def model_dump(self) -> dict:
        return {
            "athlete_id": "ath_invented",
            "currency": "USD",
            "p25": 1000,
            "p50": 2500,
            "p75": 4000,
            "confidence": 0.82,
            "assumptions": ["invented comp set"],
            "comp_cluster_ids": ["cluster_wr_acc_hs_a"],
            "disclaimer_version": "2026-09-24",
            "counterfactuals": {"up": 500},
            "status": "schema_only",
        }


def _invented(_athlete_id: str, template: str = "wr_release", school_level: str = "hs"):
    return _InventedBand()


def _assert_null_band(body: dict) -> None:
    assert body["status"] == "blocked_on_golden_set"
    assert body["p25"] is None
    assert body["p50"] is None
    assert body["p75"] is None
    assert body.get("confidence") is None
    assert body.get("comp_cluster_ids") == []
    assert body.get("counterfactuals") in ({}, None)


def test_product_nil_band_strips_engine_dollars_while_gate_closed(monkeypatch):
    monkeypatch.setattr("services.valuation.engine.estimate_band", _invented)
    body = client.get("/nil-band/ath_invented").json()
    _assert_null_band(body)


def test_valuation_service_strips_engine_dollars_while_gate_closed(monkeypatch):
    monkeypatch.setattr("services.valuation.app.estimate_band", _invented)
    body = val_client.get("/nil-band/ath_invented").json()
    _assert_null_band(body)
