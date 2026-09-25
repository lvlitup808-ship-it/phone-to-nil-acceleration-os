from fastapi.testclient import TestClient

from packages.capture.contract import validate_ingest
from packages.consent.store import ConsentStore
from services.api.app import app

client = TestClient(app)


def test_ingest_rejects_low_fps():
    d = validate_ingest(fps=24, duration_s=8, angles=["side", "fortyfive"], stable_first_500ms=True)
    assert d.accepted is False
    assert "fps_below_30" in d.reasons


def test_ingest_check_route():
    res = client.post(
        "/ingest/check",
        json={"fps": 60, "duration_s": 8, "angles": ["side", "fortyfive"], "stable_first_500ms": True},
    )
    assert res.status_code == 200
    assert res.json()["accepted"] is True


def test_consent_revoke_cascades():
    store = ConsentStore()
    c = store.grant("a1", ["capture", "coach"])
    assessment = {"id": "x", "cues": [{"name": "lean_at_release", "value": 1}], "events": [1]}
    store.attach(assessment, c["consent_id"])
    receipt = store.revoke(c["consent_id"], ["clips"])
    assert receipt["signature"]
    store.cascade(assessment)
    assert assessment["assessment_status"] == "scope_revoked"
    assert assessment["cues"] == []


def test_revoke_endpoint():
    granted = client.post("/consent", json={"athlete_id": "a1", "consent_scope": ["capture"]})
    assert granted.status_code == 200
    cid = granted.json()["consent_id"]
    gone = client.post(f"/consent/{cid}/revoke")
    assert gone.status_code == 200
    assert gone.json()["receipt_id"].startswith("rcp_")


def test_share_link_caps_ttl():
    res = client.post("/share-link", json={"athlete_id": "a1", "recipient": "coach@x.test", "ttl_days": 90})
    assert res.status_code == 200
    assert "expires_at" in res.json()


def test_position_fit_does_not_label():
    body = client.get("/position-fit/a1").json()
    assert body["status"] == "blocked_on_golden_set"


def test_nil_scenarios_schema_only():
    body = client.get("/nil-band/a1/scenarios").json()
    assert body["status"] == "schema_only"
    assert body["scenarios"] == []


def test_revoke_actually_deletes_what_the_receipt_lists(tmp_path, monkeypatch):
    monkeypatch.setenv("ARTIFACTS_DIR", str(tmp_path))
    cid = client.post("/consent", json={"athlete_id": "rv1", "consent_scope": ["capture", "coach"]}).json()["consent_id"]
    up = client.post("/upload", json={"athlete_id": "rv1", "angle": "side", "uri": "demo://rv", "consent_id": cid})
    assert up.status_code == 200
    pose = client.post(
        "/pose/assess",
        json={"athlete_id": "rv1", "clip_id": "clp_rv1", "movement": "release", "consent_id": cid},
    ).json()
    assert (tmp_path / "clp_rv1").is_dir()
    share = client.post("/share-link", json={"athlete_id": "rv1", "recipient": "c@x.test"}).json()

    receipt = client.post(f"/consent/{cid}/revoke").json()
    assert receipt["deleted_counts"] == {"clips": 1, "pose_debug": 1, "passport_share": 1}
    assert not (tmp_path / "clp_rv1").exists()
    report = client.get(f"/report/{pose['id']}").json()
    assert report["assessment_status"] == "scope_revoked"
    assert report["cues"] == []
    assert client.post(f"/share-link/{share['token']}/revoke").json()["revoked"] is True
