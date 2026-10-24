"""Honesty pin: GET /gates/golden on the live app stays closed.

No real labeled film exists. The route must return blocked_on_golden_set
and zero labeled clips. Complements the function-level pin.
"""

from __future__ import annotations

from fastapi.testclient import TestClient

from services.api.app import app

client = TestClient(app)


def test_gates_golden_route_closed_with_zero_labels() -> None:
    res = client.get("/gates/golden")
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "blocked_on_golden_set"
    assert body["progress"]["wr_labeled"] == 0
    assert body["progress"]["db_labeled"] == 0
    assert "wr_labeled 0/10" in body["missing"]
