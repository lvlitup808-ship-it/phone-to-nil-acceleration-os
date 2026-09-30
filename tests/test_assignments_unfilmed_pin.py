"""Honesty pin: GET /golden/assignments stays unfilmed with 0/10 dashboards.

Fixture manifest clips are not filmed athletes. The assignments file must
not claim wr/db labeled progress or mark an assignment filmed/labeled
while the live gate is still blocked_on_golden_set and progress is zero.
"""

from fastapi.testclient import TestClient

from services.api.app import app
from services.api.gates import get_progress, prescription_enabled

client = TestClient(app)


def test_gate_still_closed():
    assert prescription_enabled(get_progress()) is False
    assert get_progress()["wr_labeled"] == 0
    assert get_progress()["db_labeled"] == 0


def test_assignments_dashboard_zeros_and_unfilmed():
    body = client.get("/golden/assignments").json()
    dash = body["dashboard"]
    assert dash["wr_labeled"] == "0/10"
    assert dash["db_labeled"] == "0/10"
    assert dash["inter_rater"] == "pending"
    rows = body["assignments"]
    assert rows, "assignments list should exist so coaches have a queue"
    for row in rows:
        assert row["status"] == "unfilmed"
        assert row.get("clip_id") in (None, "", missing := None) or "clip_id" not in row
        assert row["status"] != "labeled"
        assert row["status"] != "filmed"
