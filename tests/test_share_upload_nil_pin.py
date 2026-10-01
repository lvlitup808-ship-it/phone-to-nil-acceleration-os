"""Honesty: capture and share routes must not carry NIL bands.

POST /upload, POST /share-link, and share revoke are film/consent
surfaces. They must not echo p25/p50/p75, MAE, composites, or a band
while the golden set is pending. quality_score on upload is the client's
capture input, not a biomechanics measurement.
"""

from fastapi.testclient import TestClient

from services.api.app import app

client = TestClient(app)

NIL_KEYS = ("p25", "p50", "p75", "mae", "composite", "nil_dollars", "confidence")


def _assert_no_nil(body: dict) -> None:
    for key in NIL_KEYS:
        assert key not in body, key
    blob = str(body).lower()
    assert "composite" not in blob
    assert "mae" not in blob


def test_upload_accept_has_no_nil_band():
    res = client.post(
        "/upload",
        json={
            "athlete_id": "ath_upload_pin",
            "angle": "side",
            "quality_score": 0.8,
            "blur": 0.1,
            "uri": "file://local-pin.mp4",
            "fps": 60,
            "duration_s": 8,
            "stable_first_500ms": True,
        },
    )
    assert res.status_code == 200, res.text
    body = res.json()
    _assert_no_nil(body)
    assert "clip_id" in body
    assert set(body["quality"]) <= {"score", "usable", "reasons", "retake_instructions"}
    assert body["quality"]["score"] == 0.8
    assert body["quality"]["usable"] is True


def test_upload_reject_has_no_nil_band():
    res = client.post(
        "/upload",
        json={
            "athlete_id": "ath_upload_reject",
            "angle": "side",
            "quality_score": 0.8,
            "blur": 0.1,
            "uri": "file://local-pin.mp4",
            "fps": 10,
            "duration_s": 1,
            "stable_first_500ms": False,
        },
    )
    assert res.status_code == 422, res.text
    detail = res.json()["detail"]
    _assert_no_nil(detail)


def test_share_link_has_no_nil_or_assessments():
    body = client.post(
        "/share-link",
        json={"athlete_id": "ath_share_pin", "recipient": "coach@x.test", "ttl_days": 7},
    ).json()
    _assert_no_nil(body)
    assert set(body) == {"token", "athlete_id", "recipient", "expires_at", "revoked"}
    assert "assessments" not in body
    assert body["revoked"] is False
    revoked = client.post(f"/share-link/{body['token']}/revoke").json()
    _assert_no_nil(revoked)
    assert revoked["revoked"] is True
    assert "assessments" not in revoked
