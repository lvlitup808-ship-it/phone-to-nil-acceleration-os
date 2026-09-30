"""Honesty: closed golden-set gate overrides valuation engine schema_only.

estimate_band() is schema_only with null bands. GET /nil-band on the product
API must still report blocked_on_golden_set while the gate is closed so a
client cannot treat the placeholder as an open valuation.
"""

from fastapi.testclient import TestClient

from services.api.app import app
from services.api.gates import gate_state, prescription_enabled
from services.valuation.engine import estimate_band

client = TestClient(app)


def test_engine_stays_schema_only_with_nulls():
    band = estimate_band("ath_gate_override")
    assert band.status == "schema_only"
    assert band.p25 is None and band.p50 is None and band.p75 is None


def test_product_nil_band_uses_gate_status_when_closed():
    assert prescription_enabled() is False
    live = gate_state()
    assert live["status"] == "blocked_on_golden_set"
    body = client.get("/nil-band/ath_gate_override").json()
    assert body["status"] == "blocked_on_golden_set"
    assert body["p25"] is None
    assert body["p50"] is None
    assert body["p75"] is None
    assert body.get("confidence") is None
    assert body.get("comp_cluster_ids", []) == []
    missing = body.get("missing") or []
    assert any(str(m).startswith("wr_labeled") for m in missing)
    assert any(str(m).startswith("db_labeled") for m in missing)


def test_product_nil_band_does_not_leave_schema_only_while_gate_closed():
    body = client.get("/nil-band/ath_gate_override").json()
    assert body["status"] != "schema_only"
    assert body["status"] != "open"
