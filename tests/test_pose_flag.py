"""Real-frame pose is off by default and behind POSE_REAL_FRAMES; it never falls back to fixtures."""

import json

import cv2
import numpy as np
import pytest
from fastapi.testclient import TestClient

from services.api import app as app_module
from services.api.app import app
from services.cv_worker import pipeline_v2
from services.cv_worker.ingest import frames as frames_mod
from services.cv_worker.pipeline_v2 import run_pose_assessment
from services.cv_worker.pose.fixture_adapter import FixturePoseAdapter

client = TestClient(app)
SIDE = "ath_0042_WR_release_side_20260925.mp4"
BODY = {"athlete_id": "ath_0042", "clip_id": "clp_0100", "movement": "release"}


class FakeModel:
    """Stands in for a real pose model: returns the synthetic sequence but is not the fixture adapter."""

    model_id = "fake_model"
    model_version = "fake_v0"

    def infer(self, frames, fps=60.0):
        seq = FixturePoseAdapter().infer(None)
        seq.model_id, seq.model_version = self.model_id, self.model_version
        return seq


def _write_mp4(path, n=12, fps=30):
    vw = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*"mp4v"), fps, (64, 48))
    for i in range(n):
        vw.write(np.full((48, 64, 3), i * 10, dtype=np.uint8))
    vw.release()


@pytest.fixture
def golden(tmp_path, monkeypatch):
    (tmp_path / "clips").mkdir()
    _write_mp4(tmp_path / "clips" / SIDE)
    clip = {
        "clip_id": "clp_0100", "athlete_id": "ath_0042", "position_target": "WR", "movement": "release",
        "surface": "turf", "lighting": "daylight",
        "camera_side": {"path": f"clips/{SIDE}", "fps": 30, "present": True},
    }
    (tmp_path / "manifest.json").write_text(json.dumps({"golden_set": "pending", "clips": [clip]}))
    monkeypatch.setattr(frames_mod, "GOLDEN_DIR", tmp_path)
    monkeypatch.setattr(app_module, "artifacts_dir_for", lambda clip_id: tmp_path / "artifacts" / clip_id)
    return tmp_path


def test_default_is_fixture_even_with_flag_on(golden, monkeypatch):
    monkeypatch.setenv("POSE_REAL_FRAMES", "1")
    out = client.post("/pose/assess", json=BODY).json()
    assert out["pose_source"] == "fixture"


def test_real_frames_refused_without_flag(golden, monkeypatch):
    monkeypatch.delenv("POSE_REAL_FRAMES", raising=False)
    r = client.post("/pose/assess", json={**BODY, "use_real_frames": True})
    assert r.status_code == 409
    assert "POSE_REAL_FRAMES" in r.json()["detail"]


def test_real_frames_unknown_clip_is_404(golden, monkeypatch):
    monkeypatch.setenv("POSE_REAL_FRAMES", "1")
    r = client.post("/pose/assess", json={**BODY, "clip_id": "clp_9999", "use_real_frames": True})
    assert r.status_code == 404


def test_real_frames_missing_angle_is_404(golden, monkeypatch):
    monkeypatch.setenv("POSE_REAL_FRAMES", "1")
    r = client.post("/pose/assess", json={**BODY, "side_clip": False, "use_real_frames": True})
    assert r.status_code == 404


def test_real_frames_with_model_is_model(golden, monkeypatch):
    monkeypatch.setenv("POSE_REAL_FRAMES", "1")
    monkeypatch.setattr(pipeline_v2, "get_adapter", lambda: FakeModel())
    out = client.post("/pose/assess", json={**BODY, "use_real_frames": True}).json()
    assert out["pose_source"] == "model"
    assert out["versions"]["pose_model_version"] == "fake_v0"
    assert out["assessment_status"] != "error"


def test_real_frames_adapter_throws_is_error(golden, monkeypatch):
    monkeypatch.setenv("POSE_REAL_FRAMES", "1")
    monkeypatch.setenv("POSE_ADAPTER", "rtmpose")
    out = client.post("/pose/assess", json={**BODY, "use_real_frames": True}).json()
    assert out["assessment_status"] == "error"
    assert out["pose_source"] == "error"
    assert out["cues"] == [] and out["events"] == []


def test_real_frames_never_fall_back_to_fixture_adapter(monkeypatch):
    """No model available (POSE_ADAPTER=fixture, or mediapipe missing) must be an error for real frames."""
    monkeypatch.setenv("POSE_ADAPTER", "fixture")
    frames = [np.zeros((48, 64, 3), dtype=np.uint8) for _ in range(10)]
    out = run_pose_assessment(movement="release", clip_id="c", frames=frames)
    assert out["assessment_status"] == "error"
    assert out["pose_source"] == "error"
    assert out["cues"] == []


def test_mediapipe_missing_falls_to_error_not_fixture(monkeypatch):
    monkeypatch.setattr(pipeline_v2, "get_adapter", lambda: FixturePoseAdapter())
    frames = [np.zeros((48, 64, 3), dtype=np.uint8) for _ in range(10)]
    out = run_pose_assessment(movement="release", clip_id="c", frames=frames)
    assert out["pose_source"] == "error"


def test_frame_loader_reads_rgb_frames_and_fps(golden):
    frames, fps = frames_mod.load_clip_frames("clp_0100", side_clip=True)
    assert len(frames) == 12 and frames[0].shape == (48, 64, 3)
    assert fps == 30


def test_frame_loader_refuses_paths_outside_golden_dir(golden):
    m = json.loads((golden / "manifest.json").read_text())
    m["clips"][0]["camera_side"]["path"] = "../outside.mp4"
    (golden / "manifest.json").write_text(json.dumps(m))
    _write_mp4(golden.parent / "outside.mp4")
    with pytest.raises(frames_mod.FilmNotFound):
        frames_mod.load_clip_frames("clp_0100", side_clip=True)
