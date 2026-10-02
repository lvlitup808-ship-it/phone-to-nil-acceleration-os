"""Honesty: share links are access tokens, not valuation payloads.

A share link may name an athlete and an expiry. It must not carry
p25/p50/p75, confidence, MAE, a dollar amount, or a composite.
Revoke returns the same row with revoked=true — still no band.
"""

from __future__ import annotations

import re

from fastapi.testclient import TestClient

from services.api.app import app

client = TestClient(app)

_BAND_KEYS = {"p25", "p50", "p75", "confidence", "mae", "composite", "nil_band", "scenarios"}
_DOLLAR = re.compile(r"\$\s*\d")
_ALLOWED = {"token", "athlete_id", "recipient", "expires_at", "revoked"}


def _assert_no_valuation(body: dict) -> None:
    assert set(body) <= _ALLOWED
    assert _BAND_KEYS.isdisjoint(body)
    blob = " ".join(str(v) for v in body.values())
    assert _DOLLAR.search(blob) is None
    assert "mae" not in blob.lower()
    assert "composite" not in blob.lower()


def test_share_link_payload_has_no_nil_band():
    body = client.post(
        "/share-link",
        json={"athlete_id": "ath_share_nil", "recipient": "coach@x.test", "ttl_days": 7},
    ).json()
    assert body["athlete_id"] == "ath_share_nil"
    assert body["revoked"] is False
    assert body["token"].startswith("shr_")
    _assert_no_valuation(body)


def test_share_link_revoke_still_has_no_nil_band():
    created = client.post(
        "/share-link",
        json={"athlete_id": "ath_share_revoke_nil", "recipient": "coach@x.test", "ttl_days": 2},
    ).json()
    revoked = client.post(f"/share-link/{created['token']}/revoke").json()
    assert revoked["revoked"] is True
    assert revoked["token"] == created["token"]
    _assert_no_valuation(revoked)
