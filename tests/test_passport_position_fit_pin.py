"""Honesty: passport and position-fit stay empty while golden-set gate is closed.

Status alone is not enough — assessments / clusters must be [].
Prevents a future change from returning fixture or inventing profiles
before real labeled film exists.
"""

from fastapi.testclient import TestClient

from services.api.app import app
from services.api.gates import get_progress, prescription_enabled

client = TestClient(app)


def test_gate_still_closed():
    assert prescription_enabled(get_progress()) is False
    body = client.get("/gates/golden").json()
    assert body["status"] == "blocked_on_golden_set"


def test_passport_assessments_empty_while_gate_closed():
    body = client.get("/passport/ath_honesty_pin").json()
    assert body["status"] == "blocked_on_golden_set"
    assert body["assessments"] == []
    assert body["athlete_id"] == "ath_honesty_pin"
    assert "consent" in body


def test_position_fit_clusters_empty_while_gate_closed():
    body = client.get("/position-fit/ath_honesty_pin").json()
    assert body["status"] == "blocked_on_golden_set"
    assert body.get("clusters", body.get("fits", [])) == []
