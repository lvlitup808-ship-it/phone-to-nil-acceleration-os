"""Honesty pin: consent grant and revoke receipts never carry NIL numbers.

POST /consent and POST /consent/{id}/revoke are film-first plumbing.
They must stay scope/receipt metadata only: no p25/p50/p75, confidence,
MAE, composite, or the historical invented band from docs/audit/baseline.md.
"""

from __future__ import annotations

import json

from fastapi.testclient import TestClient

from services.api.app import app

client = TestClient(app)

FORBIDDEN_KEYS = ("p25", "p50", "p75", "mae", "composite", "nil_dollars", "confidence")
INVENTED = ("2500", "6000", "14000", "0.41")
GRANT_KEYS = {
    "consent_id",
    "athlete_id",
    "consent_scope",
    "revoked",
    "parent_attested",
    "granted_at",
}
REVOKE_KEYS = {
    "consent_id",
    "athlete_id",
    "deleted_artifacts",
    "deleted_counts",
    "revoked_at",
    "receipt_id",
    "signature",
}


def _blob(body: dict) -> str:
    return json.dumps(body)


def test_consent_grant_has_no_nil_numbers():
    body = client.post(
        "/consent",
        json={"athlete_id": "ath_cns_nil", "consent_scope": ["capture"], "parent_attested": True},
    ).json()
    assert body["revoked"] is False
    assert body["parent_attested"] is True
    assert set(body) <= GRANT_KEYS
    for key in FORBIDDEN_KEYS:
        assert key not in body
    text = _blob(body)
    for needle in INVENTED:
        assert needle not in text


def test_consent_revoke_receipt_has_no_nil_numbers():
    granted = client.post(
        "/consent",
        json={"athlete_id": "ath_cns_revoke", "consent_scope": ["capture", "coach"]},
    ).json()
    body = client.post(f"/consent/{granted['consent_id']}/revoke").json()
    assert body["athlete_id"] == "ath_cns_revoke"
    assert "receipt_id" in body and "signature" in body
    assert set(body) <= REVOKE_KEYS
    for key in FORBIDDEN_KEYS:
        assert key not in body
    text = _blob(body)
    for needle in INVENTED:
        assert needle not in text
    assert "nil" not in text.lower()
