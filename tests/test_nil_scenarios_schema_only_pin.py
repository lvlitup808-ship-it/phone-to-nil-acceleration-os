"""Honesty: NIL scenarios stay schema_only and empty while the golden-set gate is closed.

No numbers are invented. scenarios is an empty list. status is schema_only.
Does not open the gate or start Slice 3.
"""

from __future__ import annotations

from fastapi.testclient import TestClient

from services.api.app import app
from services.api.gates import gate_state

client = TestClient(app)


def test_nil_scenarios_is_schema_only_with_empty_list():
    assert gate_state()["status"] == "blocked_on_golden_set"
    body = client.get("/nil-band/ath_scenarios/scenarios").json()
    assert body["status"] == "schema_only"
    assert body["scenarios"] == []
    assert body.get("athlete_id") == "ath_scenarios"
    # No dollar-like keys or numeric band fields.
    for key in ("p25", "p50", "p75", "confidence", "comp_cluster_ids"):
        assert key not in body or body.get(key) in (None, [], {})
    assert "note" in body
    assert "No numbers invented" in body["note"]
