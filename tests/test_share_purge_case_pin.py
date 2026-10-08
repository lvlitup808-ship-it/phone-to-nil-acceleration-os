"""Honesty pin: revoking consent must kill the share card.

A live link whose athlete id differs only by case is still that athlete.
Exact string match left the card revoked=false after consent revoke.
"""

from fastapi.testclient import TestClient

from services.api.app import app
from services.api.film import SHARE

client = TestClient(app)


def test_consent_revoke_purges_case_variant_share_link():
    granted = client.post(
        "/consent",
        json={"athlete_id": "Ath_Case", "consent_scope": ["public"]},
    )
    assert granted.status_code == 200
    cid = granted.json()["consent_id"]
    minted = client.post(
        "/share-link",
        json={"athlete_id": "Ath_Case", "recipient": "coach@x.test", "ttl_days": 7},
    )
    assert minted.status_code == 200
    token = minted.json()["token"]
    # Drift the stored id the way a hand edit or case-insensitive caller would.
    SHARE[token]["athlete_id"] = "ath_case"

    receipt = client.post(f"/consent/{cid}/revoke")
    assert receipt.status_code == 200
    assert receipt.json()["deleted_counts"]["passport_share"] == 1
    assert SHARE[token]["revoked"] is True


def test_consent_revoke_purges_the_minted_token():
    granted = client.post(
        "/consent",
        json={"athlete_id": "ath_purge", "consent_scope": ["public"]},
    )
    cid = granted.json()["consent_id"]
    minted = client.post(
        "/share-link",
        json={"athlete_id": "ath_purge", "recipient": "coach@x.test"},
    )
    token = minted.json()["token"]
    assert SHARE[token]["revoked"] is False
    client.post(f"/consent/{cid}/revoke")
    assert SHARE[token]["revoked"] is True
