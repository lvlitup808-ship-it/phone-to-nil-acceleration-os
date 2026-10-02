"""Honesty: consent receipts and default pose assess carry no NIL numbers.

Grant and revoke are consent operations. POST /pose/assess on the default
path is a fixture-pose cue dump, not a valuation. Neither payload may
publish p25/p50/p75, MAE, a composite, or a dollar band. Fixture cues are
not coach-labeled accuracy.
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


def test_consent_grant_and_revoke_have_no_nil_fields() -> None:
    granted = client.post(
        "/consent",
        json={"athlete_id": "ath_consent_pin", "consent_scope": ["capture", "coach"], "parent_attested": True},
    )
    assert granted.status_code == 200
    grant_body = granted.json()
    assert grant_body["athlete_id"] == "ath_consent_pin"
    assert grant_body["revoked"] is False
    assert "consent_id" in grant_body
    _assert_no_valuation(grant_body)

    revoked = client.post(f"/consent/{grant_body['consent_id']}/revoke")
    assert revoked.status_code == 200
    receipt = revoked.json()
    assert receipt["consent_id"] == grant_body["consent_id"]
    assert "signature" in receipt
    assert "receipt_id" in receipt
    assert receipt["deleted_counts"]["clips"] == 0
    _assert_no_valuation(receipt)


def test_default_pose_assess_is_fixture_and_not_a_valuation() -> None:
    response = client.post(
        "/pose/assess",
        json={"movement": "release", "clip_id": "clp_pose_nil_pin", "athlete_id": "ath_pose_nil_pin"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["pose_source"] == "fixture"
    assert body["golden_set"] == "pending"
    assert body["movement"] == "release"
    assert "mae" not in body
    assert body.get("nil_band") is None
    # Fixture cue numbers are not a published accuracy claim.
    for cue in body.get("cues", []):
        assert "mae" not in cue
        assert cue.get("coach_labeled") is not True
    _assert_no_valuation(body)
