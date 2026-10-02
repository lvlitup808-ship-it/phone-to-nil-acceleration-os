"""Honesty: share links are access tokens, not valuation payloads.

While the golden-set gate is closed, POST /share-link and its revoke
must not attach a NIL band, percentile, MAE, composite, or dollar amount.
A future change that stuffs estimate_band() into the token row fails here.
"""

from __future__ import annotations

import re

from fastapi.testclient import TestClient

from services.api.app import app

client = TestClient(app)

_BANNED_KEYS = {
    "p25",
    "p50",
    "p75",
    "confidence",
    "mae",
    "composite",
    "nil_band",
    "valuation",
    "comp_cluster_ids",
    "scenarios",
}
_DOLLAR = re.compile(r"\$\s*\d")
_ALLOW = {"token", "athlete_id", "recipient", "expires_at", "revoked"}


def _assert_no_valuation(body: dict) -> None:
    assert set(body) <= _ALLOW, f"unexpected share-link keys: {sorted(set(body) - _ALLOW)}"
    lowered = {k.lower() for k in body}
    assert lowered.isdisjoint(_BANNED_KEYS)
    blob = " ".join(str(v) for v in body.values())
    assert _DOLLAR.search(blob) is None
    assert "mae" not in blob.lower()
    assert "composite" not in blob.lower()


def test_share_link_payload_is_token_only() -> None:
    body = client.post(
        "/share-link",
        json={"athlete_id": "ath_share_pin", "recipient": "coach@x.test", "ttl_days": 7},
    ).json()
    assert body["athlete_id"] == "ath_share_pin"
    assert body["revoked"] is False
    assert body["token"].startswith("shr_")
    _assert_no_valuation(body)


def test_share_link_revoke_stays_token_only() -> None:
    created = client.post(
        "/share-link",
        json={"athlete_id": "ath_share_revoke", "recipient": "coach@x.test", "ttl_days": 2},
    ).json()
    revoked = client.post(f"/share-link/{created['token']}/revoke").json()
    assert revoked["revoked"] is True
    assert revoked["token"] == created["token"]
    _assert_no_valuation(revoked)
