"""Honesty: /nil-band returns null percentiles while the golden-set gate is closed.

The engine may not invent dollars. A closed gate forces p25/p50/p75 and confidence to None.
"""

from fastapi.testclient import TestClient

from services.api.app import app

client = TestClient(app)


def test_nil_band_closed_gate_nulls_percentiles():
    res = client.get("/nil-band/ath_guard")
    assert res.status_code == 200
    body = res.json()
    assert body.get("status") == "blocked_on_golden_set"
    assert body.get("p25") is None
    assert body.get("p50") is None
    assert body.get("p75") is None
    assert body.get("confidence") is None
    assert body.get("comp_cluster_ids") == []
    assert body.get("counterfactuals") == {}
    # No invented numbers of any kind.
    for key in ("p25", "p50", "p75", "confidence"):
        assert body[key] is None
