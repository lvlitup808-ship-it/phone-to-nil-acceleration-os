"""Slice 1: an assessment inherits its clips' consent, so revoking that consent blanks it.

Before this fix /assess dropped the clip's consent_id: after revoke, GET /report still
returned cues and GET /prescribe still answered 200.
"""

from fastapi.testclient import TestClient

from services.api.app import app

client = TestClient(app)


def _consent(athlete):
    return client.post("/consent", json={"athlete_id": athlete, "consent_scope": ["capture", "coach"]}).json()[
        "consent_id"
    ]


def _clip(athlete, consent_id=None, uri="demo://c"):
    body = {"athlete_id": athlete, "angle": "side", "uri": uri}
    if consent_id:
        body["consent_id"] = consent_id
    return client.post("/upload", json=body).json()["clip_id"]


def _assess(athlete, clip_ids):
    return client.post("/assess", json={"clip_ids": clip_ids, "athlete_id": athlete})


def test_assessment_carries_clip_consent():
    cid = _consent("ath_cc1")
    body = _assess("ath_cc1", [_clip("ath_cc1", cid)]).json()
    assert body["consent_id"] == cid


def test_revoke_blanks_report_and_blocks_prescribe():
    cid = _consent("ath_cc2")
    aid = _assess("ath_cc2", [_clip("ath_cc2", cid)]).json()["id"]
    assert client.get(f"/report/{aid}").json()["cues"]
    client.post(f"/consent/{cid}/revoke")
    report = client.get(f"/report/{aid}").json()
    assert report["assessment_status"] == "scope_revoked"
    assert report["cues"] == [] and report["events"] == []
    assert client.get(f"/prescribe/{aid}").status_code == 403


def test_revoke_blanks_assessment_of_clip_uploaded_without_consent_id():
    """Revoke already purges the athlete's clips that had no consent_id; their assessments follow."""
    cid = _consent("ath_cc3")
    aid = _assess("ath_cc3", [_clip("ath_cc3")]).json()["id"]
    client.post(f"/consent/{cid}/revoke")
    report = client.get(f"/report/{aid}").json()
    assert report["assessment_status"] == "scope_revoked"
    assert report["cues"] == []
    assert client.get(f"/prescribe/{aid}").status_code == 403


def test_retest_inherits_consent():
    cid = _consent("ath_cc4")
    first = _assess("ath_cc4", [_clip("ath_cc4", cid, "demo://a")]).json()["id"]
    again = client.post(
        "/retest",
        json={
            "athlete_id": "ath_cc4",
            "previous_assessment_id": first,
            "clip_ids": [_clip("ath_cc4", cid, "demo://b")],
            "template": "wr_release",
        },
    )
    assert again.status_code == 200, again.text
    again = again.json()
    assert again["consent_id"] == cid
    client.post(f"/consent/{cid}/revoke")
    assert client.get(f"/report/{again['id']}").json()["cues"] == []


def test_clips_under_different_consents_are_refused():
    c1, c2 = _consent("ath_cc5"), _consent("ath_cc5")
    r = _assess("ath_cc5", [_clip("ath_cc5", c1, "demo://x"), _clip("ath_cc5", c2, "demo://y")])
    assert r.status_code == 409


def test_revoke_does_not_touch_another_athlete():
    mine, theirs = _consent("ath_cc6"), _consent("ath_cc7")
    other = _assess("ath_cc7", [_clip("ath_cc7", theirs)]).json()["id"]
    client.post(f"/consent/{mine}/revoke")
    report = client.get(f"/report/{other}").json()
    assert report.get("assessment_status") != "scope_revoked"
    assert report["cues"]
