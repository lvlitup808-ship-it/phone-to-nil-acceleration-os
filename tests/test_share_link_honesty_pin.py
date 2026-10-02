"""Honesty: a share link is access metadata, not a valuation.

Two links for the same athlete on the same day must not overwrite each other,
or a revoke of the second token drops the first. The payload must not carry
NIL bands, MAE, assessments, or dollar fields while the gate is closed.
"""

from __future__ import annotations

from fastapi.testclient import TestClient

from services.api.app import app

client = TestClient(app)

_FORBIDDEN = {
    "p25",
    "p50",
    "p75",
    "mae",
    "MAE",
    "composite",
    "nil_band",
    "assessments",
    "currency",
    "comp_cluster_ids",
}


def test_share_links_same_day_do_not_collide() -> None:
    first = client.post(
        "/share-link",
        json={"athlete_id": "ath_share_pin", "recipient": "a@x.test", "ttl_days": 7},
    )
    second = client.post(
        "/share-link",
        json={"athlete_id": "ath_share_pin", "recipient": "b@x.test", "ttl_days": 7},
    )
    assert first.status_code == 200
    assert second.status_code == 200
    a, b = first.json(), second.json()
    assert a["token"] != b["token"]
    assert a["recipient"] == "a@x.test"
    revoked = client.post(f"/share-link/{b['token']}/revoke")
    assert revoked.status_code == 200
    assert revoked.json()["revoked"] is True
    # First link must still be the original row, not overwritten by the second.
    again = client.post(f"/share-link/{a['token']}/revoke")
    assert again.status_code == 200
    assert again.json()["recipient"] == "a@x.test"
    assert again.json()["token"] == a["token"]


def test_share_link_payload_has_no_nil_or_assessment() -> None:
    body = client.post(
        "/share-link",
        json={"athlete_id": "ath_share_nil", "recipient": "coach@x.test", "ttl_days": 3},
    ).json()
    assert _FORBIDDEN.isdisjoint(body.keys())
    blob = str(body).lower()
    assert "mae" not in blob
    assert "$" not in blob
    for key in ("p25", "p50", "p75"):
        assert key not in body
    assert set(body) == {"token", "athlete_id", "recipient", "expires_at", "revoked"}
