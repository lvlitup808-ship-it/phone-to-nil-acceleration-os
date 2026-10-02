"""Honesty: consent grant and revoke receipt are not a valuation.

A grant returns scope and attestation only. A revoke returns a signed purge
receipt. Neither payload may carry NIL bands, percentiles, MAE, or a composite
while the golden-set gate is closed.
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
            assert not (isinstance(value, str) and "$" in value and any(c.isdigit() for c in value))
            _assert_no_valuation(value)
    elif isinstance(body, list):
        for item in body:
            _assert_no_valuation(item)


def test_consent_grant_is_scope_only() -> None:
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
    assert body["consent_scope"] == ["capture", "coach"]
    assert body["revoked"] is False
    assert body["parent_attested"] is True
    assert body["consent_id"].startswith("cns_")
    _assert_no_valuation(body)


def test_consent_revoke_receipt_has_no_nil_fields() -> None:
    granted = client.post(
        "/consent",
        json={"athlete_id": "ath_consent_revoke_pin", "consent_scope": ["capture"]},
    )
    assert granted.status_code == 200
    consent_id = granted.json()["consent_id"]
    response = client.post(f"/consent/{consent_id}/revoke")
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
    assert body["consent_id"] == consent_id
    assert body["athlete_id"] == "ath_consent_revoke_pin"
    assert body["deleted_artifacts"] == ["clips", "pose_debug", "passport_share"]
    assert body["receipt_id"].startswith("rcp_")
    assert isinstance(body["signature"], str) and len(body["signature"]) == 64
    _assert_no_valuation(body)
