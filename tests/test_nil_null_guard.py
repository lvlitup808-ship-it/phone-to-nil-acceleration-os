"""NIL honesty: no invented dollars, composites, or MAE.

Band numerics stay null until a sourced comp dataset exists and the
golden-set gate opens. This file fails if any route or the engine
returns non-null p25/p50/p75/confidence or non-empty scenarios.
"""

from fastapi.testclient import TestClient

from services.api.app import app
from services.valuation.app import app as valuation_app
from services.valuation.engine import estimate_band

client = TestClient(app)
val_client = TestClient(valuation_app)


def test_engine_estimate_band_all_numerics_null():
    band = estimate_band("ath_honesty")
    assert band.p25 is None
    assert band.p50 is None
    assert band.p75 is None
    assert band.confidence is None
    assert band.comp_cluster_ids == []
    assert band.status == "schema_only"
    assert "no comp dataset" in " ".join(band.assumptions).lower()


def test_nil_band_route_never_returns_numbers():
    body = client.get("/nil-band/ath_honesty").json()
    assert body["p25"] is None
    assert body["p50"] is None
    assert body["p75"] is None
    assert body.get("confidence") is None
    assert body.get("status") in ("schema_only", "blocked_on_golden_set")
    assert body.get("comp_cluster_ids", []) == []


def test_nil_scenarios_always_empty():
    body = client.get("/nil-band/ath_honesty/scenarios").json()
    assert body["scenarios"] == []
    assert body["status"] == "schema_only"
    assert "invented" in body.get("note", "").lower() or "no numbers" in body.get("note", "").lower()


def test_standalone_valuation_service_never_returns_numbers():
    """services/valuation.app is a separate process; pin it too (audit Q27)."""
    body = val_client.get("/nil-band/ath_honesty").json()
    assert body["p25"] is None
    assert body["p50"] is None
    assert body["p75"] is None
    assert body.get("confidence") is None
    assert body.get("status") == "blocked_on_golden_set"
    assert body.get("comp_cluster_ids", []) == []
    assert body["p25"] is None
    assert "no comp dataset" in " ".join(body.get("assumptions", [])).lower()
