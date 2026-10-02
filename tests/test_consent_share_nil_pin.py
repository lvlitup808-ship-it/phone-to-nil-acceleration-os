"""Honesty: consent and share-link are access control, not valuation.

Grant, revoke receipt, and share-link rows may name an athlete and scopes.
They must not carry NIL bands, percentiles, MAE, or a composite.
"""

from __future__ import annotations

from fastapi.testclient import TestClient

from services.api.app import app

client = TestClient(app)

_FORBIDDEN = ("p25", "p50", "p75", "mae", "composite", "nil_band", "nil_dollars")


def _assert_no_valuation(body: object) -> None:
    if isinstance(body, dict):
        for key, value in body.items():
            assert key.lower() not in _FORBIDDEN, key
            assert "nil" not in key.lower()
            assert not (isinstance(value, str) and "$" in value and any(c.isdigit() for c in value))
            _assert_no_valuation(value)
    elif isinstance(body, list):
        for item in body:
            _assert_no_valuation(item)


def test_consent_grant_is_scopes_only() -> None:
    response = client.post(
        "/consent",
        json={"athlete_id": "ath_consent_pin", "consent_scope": ["capture", "coach"], "parent_attested": True},
    )
    assert response.status_code == 200
    body = response.json()
    assert set(body) == {
        "consent_id",
        "athlete_id",
        "consent_scope",
        "revoked",
        "parent_attested",
        "granted_at",
    }
    assert body["athlete_id"] == "ath_consent_pin"
    assert body["revoked"] is False
    assert body["consent_scope"] == ["capture", "coach"]
    _assert_no_valuation(body)


def test_consent_revoke_receipt_has_no_nil_fields() -> None:
    granted = client.post(
        "/consent",
        json={"athlete_id": "ath_revoke_pin", "consent_scope": ["capture"]},
    ).json()
    response = client.post(f"/consent/{granted['consent_id']}/revoke")
    assert response.status_code == 200
    body = response.json()
    assert set(body) == {
        "consent_id",
        "athlete_id",
        "deleted_artifacts",
        "deleted_counts",
        "revoked_at",
        "receipt_id",
        "signature",
    }
    assert body["athlete_id"] == "ath_revoke_pin"
    assert "clips" in body["deleted_artifacts"]
    _assert_no_valuation(body)


def test_share_link_row_has_no_nil_fields() -> None:
    response = client.post(
        "/share-link",
        json={"athlete_id": "ath_share_pin", "recipient": "coach@x.test", "ttl_days": 7},
    )
    assert response.status_code == 200
    body = response.json()
    assert set(body) == {"token", "athlete_id", "recipient", "expires_at", "revoked"}
    assert body["revoked"] is False
    assert body["athlete_id"] == "ath_share_pin"
    _assert_no_valuation(body)
