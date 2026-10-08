"""Honesty: the standalone valuation process must not look open while the gate is closed.

GET /nil-band on services.api overlays blocked_on_golden_set. services.valuation.app
is a separate process and used to return status schema_only with null bands.
A client of that process could treat schema_only as a finished valuation.
Numbers stay null. Status follows the gate.
"""

from __future__ import annotations

from fastapi.testclient import TestClient

from services.api.gates import gate_state, prescription_enabled
from services.valuation.app import app as valuation_app

client = TestClient(valuation_app)


def test_valuation_app_follows_closed_gate() -> None:
    assert prescription_enabled() is False
    live = gate_state()
    assert live["status"] == "blocked_on_golden_set"
    body = client.get("/nil-band/ath_val_gate").json()
    assert body["status"] == "blocked_on_golden_set"
    assert body["status"] != "schema_only"
    assert body["p25"] is None
    assert body["p50"] is None
    assert body["p75"] is None
    assert body.get("confidence") is None
    assert body.get("comp_cluster_ids", []) == []
    missing = body.get("missing") or []
    assert any(str(item).startswith("wr_labeled") for item in missing)
    assert any(str(item).startswith("db_labeled") for item in missing)
