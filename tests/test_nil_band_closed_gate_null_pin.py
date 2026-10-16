"""Honesty: closed golden-set gate forces NIL band numbers to null.

GET /nil-band/{athlete_id} must not forward engine dollars while the gate is
closed. The endpoint zeros p25/p50/p75/confidence/clusters/counterfactuals
even if estimate_band is patched to lie. No numbers are invented; gate stays
CLOSED until real labeled film meets docs/film_first.md.
"""

from __future__ import annotations

from unittest.mock import patch

from fastapi.testclient import TestClient

from packages.shared.models import NILBand
from services.api.app import app

client = TestClient(app)


def test_nil_band_closed_gate_overrides_lying_engine() -> None:
    lying = NILBand(
        athlete_id="ath_nil_null_pin",
        p25=1000,
        p50=2500,
        p75=4000,
        confidence=0.9,
        assumptions=["this is a test lie"],
        comp_cluster_ids=["fake_cluster"],
        disclaimer_version="test",
        counterfactuals={"if_open": 999},
        status="computed",
    )

    with patch("services.valuation.engine.estimate_band", return_value=lying):
        response = client.get("/nil-band/ath_nil_null_pin")

    assert response.status_code == 200
    body = response.json()
    assert body["athlete_id"] == "ath_nil_null_pin"
    assert body.get("status") == "blocked_on_golden_set"
    assert body["p25"] is None
    assert body["p50"] is None
    assert body["p75"] is None
    assert body["confidence"] is None
    assert body["comp_cluster_ids"] == []
    assert body["counterfactuals"] == {}
    # The lie must not leak through any other numeric field.
    assert 1000 not in body.values()
    assert 2500 not in body.values()
    assert 4000 not in body.values()
