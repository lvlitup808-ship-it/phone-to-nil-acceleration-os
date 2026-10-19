"""Honesty pin: position-fit stays blocked with empty clusters.

GET /position-fit/{athlete_id} must not invent cluster similarity or a position
claim while the golden-set gate is closed. Clusters stay empty. No composite,
no MAE, no dollar band.
"""

from __future__ import annotations

from fastapi.testclient import TestClient

from services.api.app import app

client = TestClient(app)


def test_position_fit_blocked_empty_clusters():
    res = client.get("/position-fit/ath_test")
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "blocked_on_golden_set"
    assert body["clusters"] == []
    assert body["athlete_id"] == "ath_test"
    note = body.get("note", "").lower()
    assert "will not say" in note or "not" in note
    assert "$" not in str(body)
    assert "mae" not in str(body).lower()
    assert "composite" not in str(body).lower()
