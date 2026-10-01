"""Honesty pin: NIL scenario route stays schema-only and empty.

GET /nil-band/{id}/scenarios is Slice 4 schema. It must not invent
projected bands, percentiles, or dollars while the golden set is pending.
"""

from fastapi.testclient import TestClient

from services.api.app import app

client = TestClient(app)

BANNED_KEYS = ("p25", "p50", "p75", "mae", "composite", "dollar", "nil_value", "amount")


def test_nil_scenarios_schema_only_and_empty():
    body = client.get("/nil-band/ath_scenario_pin/scenarios").json()
    assert body["athlete_id"] == "ath_scenario_pin"
    assert body["status"] == "schema_only"
    assert body["scenarios"] == []
    assert body.get("slice") == 4
    for key in BANNED_KEYS:
        assert key not in body


def test_nil_scenarios_do_not_open_the_gate():
    gate = client.get("/gates/golden").json()
    assert gate["status"] == "blocked_on_golden_set"
    body = client.get("/nil-band/ath_scenario_pin/scenarios").json()
    assert body["status"] != "open"
    assert body["scenarios"] == []
    text = str(body).lower()
    assert "$" not in text
    for banned in ("p25", "p50", "p75"):
        assert banned not in body
