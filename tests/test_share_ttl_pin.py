"""Share-link TTL honesty: cap at 30 days, floor at 1. Never invent longer access."""

from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient

from services.api.app import app

client = TestClient(app)


def _expires(body: dict) -> datetime:
    raw = body["expires_at"]
    return datetime.fromisoformat(raw.replace("Z", "+00:00"))


def test_share_link_requested_90_days_caps_at_30():
    before = datetime.now(UTC)
    body = client.post(
        "/share-link",
        json={"athlete_id": "ath_ttl", "recipient": "coach@x.test", "ttl_days": 90},
    ).json()
    after = datetime.now(UTC)
    exp = _expires(body)
    assert exp <= after + timedelta(days=30, seconds=5)
    assert exp >= before + timedelta(days=29)


def test_share_link_default_is_30_days():
    before = datetime.now(UTC)
    body = client.post(
        "/share-link",
        json={"athlete_id": "ath_ttl_default", "recipient": "coach@x.test"},
    ).json()
    exp = _expires(body)
    assert exp <= datetime.now(UTC) + timedelta(days=30, seconds=5)
    assert exp >= before + timedelta(days=29)


def test_share_link_zero_ttl_floors_at_one_day():
    before = datetime.now(UTC)
    body = client.post(
        "/share-link",
        json={"athlete_id": "ath_ttl_floor", "recipient": "coach@x.test", "ttl_days": 0},
    ).json()
    exp = _expires(body)
    assert exp >= before + timedelta(hours=23)
    assert exp <= datetime.now(UTC) + timedelta(days=1, seconds=5)
