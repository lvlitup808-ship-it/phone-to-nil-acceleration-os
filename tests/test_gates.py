import json

from fastapi.testclient import TestClient

from services.api import app as app_module
from services.api import gates
from services.api.app import app

client = TestClient(app)

OPEN = {
    "wr_labeled": 10,
    "db_labeled": 10,
    "inter_rater_done": True,
    "disputed": 0,
    "inter_rater_clips": 4,
    "surfaces": 3,
    "lighting_conditions": 2,
    "wr_athletes": 3,
    "db_athletes": 3,
}


def _golden_dir(tmp_path, clips, labels):
    (tmp_path / "labels").mkdir()
    (tmp_path / "clips").mkdir()
    for c in clips:
        for cam in ("camera_side", "camera_45"):
            if c.get(cam, {}).get("present"):
                (tmp_path / c[cam]["path"]).write_bytes(b"x")
    (tmp_path / "manifest.json").write_text(json.dumps({"clips": clips}))
    (tmp_path / "labels" / "_template.json").write_text(json.dumps({"clip_id": clips[0]["clip_id"], "coach_id": "t"}))
    for i, lab in enumerate(labels):
        (tmp_path / "labels" / f"l{i}.json").write_text(json.dumps(lab))
    return tmp_path


def test_repo_golden_set_counts_zero():
    p = gates.get_progress()
    assert p["wr_labeled"] == 0 and p["db_labeled"] == 0
    assert p["inter_rater_done"] is False


def test_fixture_labels_without_film_never_count(tmp_path):
    clips = [{"clip_id": "c1", "position_target": "WR", "camera_side": {"path": "clips/c1.mp4", "present": False}}]
    d = _golden_dir(tmp_path, clips, [{"clip_id": "c1", "coach_id": "a"}])
    assert gates.get_progress(d)["wr_labeled"] == 0


def test_real_labels_count_and_inter_rater(tmp_path):
    clips = [
        {
            "clip_id": f"c{i}", "position_target": "WR", "athlete_id": f"ath_{i}",
            "camera_side": {"path": f"clips/c{i}.mp4", "present": True},
        }
        for i in range(5)
    ]
    labels = [{"clip_id": f"c{i}", "coach_id": "a"} for i in range(5)]
    labels += [{"clip_id": f"c{i}", "coach_id": "b"} for i in range(4)]
    labels += [{"clip_id": "c4", "coach_id": "b", "disputed": True}]
    p = gates.get_progress(_golden_dir(tmp_path, clips, labels))
    assert p["wr_labeled"] == 4
    assert p["disputed"] == 1
    assert p["inter_rater_done"] is True
    assert gates.prescription_enabled(p) is False


def test_gate_requires_every_condition():
    assert gates.prescription_enabled(OPEN) is True
    for key, bad in [("wr_labeled", 9), ("db_labeled", 9), ("inter_rater_done", False), ("disputed", 3),
                     ("surfaces", 2), ("lighting_conditions", 1), ("wr_athletes", 2), ("db_athletes", 2)]:
        assert gates.prescription_enabled({**OPEN, key: bad}) is False, key


def test_gate_route_reports_real_state():
    body = client.get("/gates/golden").json()
    assert body["status"] == "blocked_on_golden_set"
    assert body["progress"] == gates.get_progress()


def test_blocked_routes_return_blocked_status_not_empty_200():
    for path in ("/passport/a1", "/nil-band/a1", "/position-fit/a1"):
        body = client.get(path).json()
        assert body["status"] == "blocked_on_golden_set", path


def test_passport_consent_is_looked_up_not_asserted():
    body = client.get("/passport/nobody").json()
    assert body["consent"] == {"capture": False, "coach": False, "public": False}
    cid = client.post("/consent", json={"athlete_id": "pp1", "consent_scope": ["capture"]}).json()["consent_id"]
    assert client.get("/passport/pp1").json()["consent"]["capture"] is True
    client.post(f"/consent/{cid}/revoke")
    assert client.get("/passport/pp1").json()["consent"]["capture"] is False


def test_prescribe_opens_only_when_gate_opens(monkeypatch):
    up = client.post("/upload", json={"athlete_id": "g1", "angle": "side", "uri": "demo://g"}).json()
    aid = client.post("/assess", json={"clip_ids": [up["clip_id"]], "athlete_id": "g1"}).json()["id"]
    assert client.get(f"/prescribe/{aid}").json()["drills"] == []
    monkeypatch.setattr(app_module, "gate_state", lambda: {"status": "open", "missing": [], "progress": OPEN})
    body = client.get(f"/prescribe/{aid}").json()
    assert body["status"] == "open"
    assert all(d.get("coach_reviewed") is not False for d in body["drills"])
    band = client.get("/nil-band/g1").json()
    assert band["p50"] is None, "gate open still has no comp data, so still no numbers"
