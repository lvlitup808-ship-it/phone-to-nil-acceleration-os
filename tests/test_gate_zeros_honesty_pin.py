"""Honesty pin: golden-set gate reports zero labeled film and stays closed.

Fixture clips with present:false never count. GET /gates/golden must
return blocked_on_golden_set, wr_labeled == 0, db_labeled == 0, and must
not invent dollar bands, MAE, or composites. No real film exists.
"""

from fastapi.testclient import TestClient

from services.api.app import app
from services.api.gates import get_progress, prescription_enabled

client = TestClient(app)

BANNED = ("p25", "p50", "p75", "mae", "composite", "dollar", "nil_value")


def test_progress_zeros_and_gate_closed():
    progress = get_progress()
    assert progress["wr_labeled"] == 0
    assert progress["db_labeled"] == 0
    assert progress.get("inter_rater_done") is False
    assert prescription_enabled(progress) is False


def test_gates_endpoint_blocked_with_zeros_and_no_nil():
    body = client.get("/gates/golden").json()
    assert body["status"] == "blocked_on_golden_set"
    assert body.get("wr_labeled") == 0 or body.get("progress", {}).get("wr_labeled") == 0
    # tolerate either flat or nested; both must be zero if present
    prog = body.get("progress") or body
    assert prog.get("wr_labeled", 0) == 0
    assert prog.get("db_labeled", 0) == 0
    text = str(body).lower()
    assert "$" not in text
    for key in BANNED:
        assert key not in body
        assert key not in str(body).lower()
