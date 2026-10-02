"""Honesty: standalone valuation service cannot look open while the gate is closed.

Product GET /nil-band already overlays gate_state(). services/valuation.app is a
separate process and used to return status schema_only with null bands. A client
hitting that process could treat the placeholder as a valuation. While the live
golden-set gate is closed, the route must report blocked_on_golden_set and keep
p25/p50/p75/confidence null. The engine itself stays schema_only.
"""

from fastapi.testclient import TestClient

from services.api.gates import gate_state, prescription_enabled
from services.valuation.app import app as valuation_app
from services.valuation.engine import estimate_band

val_client = TestClient(valuation_app)


def test_engine_stays_schema_only_without_gate_overlay():
    band = estimate_band("ath_val_gate")
    assert band.status == "schema_only"
    assert band.p25 is None and band.p50 is None and band.p75 is None
    assert band.confidence is None


def test_valuation_service_blocked_while_gate_closed():
    assert prescription_enabled() is False
    live = gate_state()
    assert live["status"] == "blocked_on_golden_set"
    body = val_client.get("/nil-band/ath_val_gate").json()
    assert body["status"] == "blocked_on_golden_set"
    assert body["status"] != "schema_only"
    assert body["status"] != "open"
    assert body["p25"] is None
    assert body["p50"] is None
    assert body["p75"] is None
    assert body.get("confidence") is None
    assert body.get("comp_cluster_ids", []) == []
    missing = body.get("missing") or []
    assert any(str(m).startswith("wr_labeled") for m in missing)
    assert any(str(m).startswith("db_labeled") for m in missing)
    assert "no comp dataset" in " ".join(body.get("assumptions", [])).lower()
