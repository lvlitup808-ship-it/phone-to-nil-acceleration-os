"""Regressions for findings from the code review of the audit pass."""

import json

from fastapi.testclient import TestClient

from services.api import gates
from services.api.app import STORE, app
from services.cv_worker.calibration.field_line import Calibration
from services.cv_worker.events.detector import Event
from services.cv_worker.features.wr_release import extract_wr
from services.cv_worker.pose.fixture_adapter import FixturePoseAdapter

client = TestClient(app)


def test_pose_assess_with_revoked_consent_writes_nothing(tmp_path, monkeypatch):
    monkeypatch.setenv("ARTIFACTS_DIR", str(tmp_path))
    cid = client.post("/consent", json={"athlete_id": "rf1", "consent_scope": ["capture"]}).json()["consent_id"]
    client.post(f"/consent/{cid}/revoke")
    res = client.post(
        "/pose/assess",
        json={"athlete_id": "rf1", "clip_id": "clp_rf1", "movement": "release", "consent_id": cid},
    )
    assert res.status_code == 403
    assert not (tmp_path / "clp_rf1").exists()


def test_pose_assess_with_unknown_consent_is_rejected(tmp_path, monkeypatch):
    monkeypatch.setenv("ARTIFACTS_DIR", str(tmp_path))
    res = client.post(
        "/pose/assess",
        json={"athlete_id": "rf2", "clip_id": "clp_rf2", "movement": "release", "consent_id": "cns_nope"},
    )
    assert res.status_code == 404
    assert not (tmp_path / "clp_rf2").exists()


def test_gct_below_floor_is_not_reported_as_the_floor():
    seq = FixturePoseAdapter().infer(None)
    cal = Calibration(mode="field_line", confidence=0.8, meters_per_pixel=0.01, debug_points=[])
    events = [Event("first_step", 580, 0.75, 35), Event("second_step", 700, 0.7, 42)]
    cue = {c["name"]: c for c in extract_wr(seq, events, cal, "c", side_clip=True)}["ground_contact_time_first_step"]
    assert cue["value"] is None
    assert cue["cue_status"] == "insufficient_data"


def test_revoke_removes_athlete_clips_uploaded_without_consent_id():
    up = client.post("/upload", json={"athlete_id": "rf3", "angle": "side", "uri": "demo://rf3"}).json()
    cid = client.post("/consent", json={"athlete_id": "rf3", "consent_scope": ["capture"]}).json()["consent_id"]
    receipt = client.post(f"/consent/{cid}/revoke").json()
    assert up["clip_id"] not in STORE["clips"]
    assert receipt["deleted_counts"]["clips"] == 1


def test_prescribe_on_empty_cues_does_not_500(monkeypatch):
    from services.api import app as app_module

    monkeypatch.setattr(app_module, "gate_state", lambda: {"status": "open", "missing": [], "progress": {}})
    STORE["assessments"]["empty1"] = {"id": "empty1", "athlete_id": "rf4", "cues": []}
    res = client.get("/prescribe/empty1")
    assert res.status_code == 200
    assert res.json()["drills"] == []


def _dir(tmp_path, clips, labels):
    (tmp_path / "labels").mkdir()
    (tmp_path / "clips").mkdir()
    (tmp_path / "manifest.json").write_text(json.dumps({"clips": clips}))
    for i, lab in enumerate(labels):
        (tmp_path / "labels" / f"l{i}.json").write_text(json.dumps(lab))
    return tmp_path


def test_labels_without_coach_id_do_not_count(tmp_path):
    clips = [{"clip_id": "c1", "position_target": "WR", "camera_side": {"path": "clips/c1.mp4", "present": True}}]
    d = _dir(tmp_path, clips, [{"clip_id": "c1"}])
    (d / "clips/c1.mp4").write_bytes(b"x")
    assert gates.get_progress(d)["wr_labeled"] == 0


def test_film_outside_golden_dir_does_not_count(tmp_path):
    outside = tmp_path / "outside.mp4"
    outside.write_bytes(b"x")
    gd = tmp_path / "gd"
    gd.mkdir()
    clips = [{"clip_id": "c1", "position_target": "WR", "camera_side": {"path": "../outside.mp4", "present": True}}]
    d = _dir(gd, clips, [{"clip_id": "c1", "coach_id": "a"}])
    assert gates.get_progress(d)["wr_labeled"] == 0


def test_harness_reports_pose_source_from_pipeline():
    from services.golden_set.harness import build_report

    text = build_report()
    assert "source=fixture" in text
    assert "mode: fixture" in text
