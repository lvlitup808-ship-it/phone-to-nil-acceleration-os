"""Pin POST /upload and POST /share-link so capture and share stay valuation-free.

Upload quality is the caller-supplied capture score, not a biomechanics
measurement. A share link is a token. Neither route may emit p25/p50/p75,
MAE, a composite, or an NIL band.
"""

from __future__ import annotations

from typing import Any

from fastapi.testclient import TestClient

from services.api.app import app

client = TestClient(app)

FORBIDDEN_KEYS = {"p25", "p50", "p75", "mae", "composite", "nil_band", "confidence"}


def _keys(obj: Any) -> set[str]:
    found: set[str] = set()
    if isinstance(obj, dict):
        for key, value in obj.items():
            found.add(str(key).lower())
            found |= _keys(value)
    elif isinstance(obj, list):
        for item in obj:
            found |= _keys(item)
    return found


def test_upload_does_not_publish_nil_or_mae() -> None:
    response = client.post(
        "/upload",
        json={
            "athlete_id": "ath_honesty",
            "angle": "side",
            "quality_score": 0.8,
            "blur": 0.1,
            "uri": "file://fixture-not-film",
            "fps": 60,
            "duration_s": 8,
            "stable_first_500ms": True,
        },
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["quality"]["score"] == 0.8
    assert body["quality"]["usable"] is True
    leaked = _keys(body) & FORBIDDEN_KEYS
    assert not leaked, f"upload leaked valuation keys: {sorted(leaked)}"
    blob = str(body).lower()
    assert "mae" not in blob
    assert "$" not in blob


def test_share_link_is_token_only() -> None:
    response = client.post(
        "/share-link",
        json={"athlete_id": "ath_honesty", "recipient": "coach@example.com", "ttl_days": 7},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert set(body) <= {"token", "athlete_id", "recipient", "expires_at", "revoked"}
    assert body["revoked"] is False
    assert body["token"].startswith("shr_")
    leaked = _keys(body) & FORBIDDEN_KEYS
    assert not leaked, f"share-link leaked valuation keys: {sorted(leaked)}"
    assert "$" not in str(body)
