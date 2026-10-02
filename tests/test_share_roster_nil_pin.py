"""Honesty pin: share links and roster stubs never carry NIL numbers.

POST /share-link and GET /roster are film-first plumbing. They must not
echo p25/p50/p75, confidence, MAE, composites, or the historical invented
band (2500/6000/14000, confidence 0.41) from docs/audit/baseline.md.
"""

from __future__ import annotations

import json

from fastapi.testclient import TestClient

from services.api.app import app

client = TestClient(app)

FORBIDDEN_KEYS = ("p25", "p50", "p75", "mae", "composite", "nil_dollars", "confidence")
INVENTED = ("2500", "6000", "14000", "0.41")


def _blob(body: dict) -> str:
    return json.dumps(body)


def test_share_link_payload_has_no_nil_numbers():
    body = client.post(
        "/share-link",
        json={"athlete_id": "ath_share_nil", "recipient": "coach@x.test", "ttl_days": 7},
    ).json()
    assert set(body) <= {"token", "athlete_id", "recipient", "expires_at", "revoked"}
    for key in FORBIDDEN_KEYS:
        assert key not in body
    text = _blob(body)
    for needle in INVENTED:
        assert needle not in text


def test_revoked_share_link_still_has_no_nil_numbers():
    created = client.post(
        "/share-link",
        json={"athlete_id": "ath_share_revoke", "recipient": "coach@x.test", "ttl_days": 2},
    ).json()
    body = client.post(f"/share-link/{created['token']}/revoke").json()
    assert body["revoked"] is True
    for key in FORBIDDEN_KEYS:
        assert key not in body
    text = _blob(body)
    for needle in INVENTED:
        assert needle not in text


def test_roster_stub_has_no_nil_numbers():
    body = client.get("/roster/team_nil_pin").json()
    assert body["id"] == "team_nil_pin"
    assert body["athletes"] == []
    for key in FORBIDDEN_KEYS:
        assert key not in body
    text = _blob(body)
    for needle in INVENTED:
        assert needle not in text
