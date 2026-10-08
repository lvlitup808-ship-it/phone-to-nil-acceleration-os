"""Consent honesty: a revoked share link must stay revoked.

POST /share-link used to key tokens as shr_<athlete>_<YYYYMMDD>. A second
grant the same day overwrote the revoked row and revived the old token.
"""

from __future__ import annotations

from fastapi.testclient import TestClient

from services.api.app import app
from services.api.film import SHARE

client = TestClient(app)


def test_same_day_regrant_does_not_revive_revoked_share_token() -> None:
    granted = client.post(
        "/consent",
        json={"athlete_id": "ath_share_revive", "consent_scope": ["public"]},
    )
    assert granted.status_code == 200
    created = client.post(
        "/share-link",
        json={"athlete_id": "ath_share_revive", "recipient": "coach@x.test", "ttl_days": 7},
    ).json()
    token = created["token"]
    revoked = client.post(f"/share-link/{token}/revoke").json()
    assert revoked["revoked"] is True

    again = client.post(
        "/share-link",
        json={"athlete_id": "ath_share_revive", "recipient": "other@x.test", "ttl_days": 7},
    ).json()
    assert again["token"] != token
    assert again["revoked"] is False
    assert SHARE[token]["revoked"] is True
    assert SHARE[token]["recipient"] == "coach@x.test"
