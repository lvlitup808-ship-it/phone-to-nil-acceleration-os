"""Honesty pin: a share link is a public card, not a side effect of capture.

docs/legal/consent.md says public sharing defaults to NO. Minting a link
without an unrevoked public scope, or after that scope is revoked, would
share an athlete who did not agree. Capture and coach scopes are not enough.
"""

from fastapi.testclient import TestClient

from services.api.app import app

client = TestClient(app)


def test_share_link_without_consent_is_forbidden():
    res = client.post(
        "/share-link",
        json={"athlete_id": "no_share", "recipient": "coach@x.test", "ttl_days": 7},
    )
    assert res.status_code == 403
    assert "public" in res.json()["detail"]


def test_capture_and_coach_scopes_do_not_mint_a_share():
    client.post(
        "/consent",
        json={"athlete_id": "coach_only", "consent_scope": ["capture", "coach"]},
    )
    res = client.post(
        "/share-link",
        json={"athlete_id": "coach_only", "recipient": "coach@x.test"},
    )
    assert res.status_code == 403


def test_revoked_public_scope_does_not_mint_a_new_share():
    granted = client.post(
        "/consent",
        json={"athlete_id": "revoked_share", "consent_scope": ["public"]},
    )
    cid = granted.json()["consent_id"]
    ok = client.post(
        "/share-link",
        json={"athlete_id": "revoked_share", "recipient": "coach@x.test", "ttl_days": 90},
    )
    assert ok.status_code == 200
    assert ok.json()["revoked"] is False
    client.post(f"/consent/{cid}/revoke")
    again = client.post(
        "/share-link",
        json={"athlete_id": "revoked_share", "recipient": "coach@x.test"},
    )
    assert again.status_code == 403
