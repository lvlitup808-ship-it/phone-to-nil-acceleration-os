"""Honesty pin: manifest present:true without a file on disk is not film.

A clip that claims camera_side.present=true but has no bytes under
data/golden_set/ must not count toward wr_labeled / db_labeled. Fixture
paths and lying present flags never open the gate.
"""

from __future__ import annotations

import json

from services.api import gates
from services.golden_set.labels import CUES, EVENTS


def _dir(tmp_path, clips, labels):
    (tmp_path / "labels").mkdir()
    (tmp_path / "clips").mkdir()
    (tmp_path / "manifest.json").write_text(json.dumps({"clips": clips}))
    for i, lab in enumerate(labels):
        (tmp_path / "labels" / f"l{i}.json").write_text(json.dumps(lab))
    return tmp_path


def test_has_film_false_when_present_true_but_file_missing(tmp_path):
    clip = {
        "clip_id": "c_lie",
        "position_target": "WR",
        "athlete_id": "ath_x",
        "surface": "turf",
        "lighting": "daylight",
        "camera_side": {"path": "clips/c_lie.mp4", "present": True},
        "camera_45": {"path": "clips/c_lie_45.mp4", "present": False},
    }
    assert gates.has_film(clip, tmp_path) is False


def test_present_true_missing_file_label_does_not_count(tmp_path):
    clips = [
        {
            "clip_id": "c_lie",
            "position_target": "WR",
            "athlete_id": "ath_x",
            "surface": "turf",
            "lighting": "daylight",
            "camera_side": {"path": "clips/c_lie.mp4", "present": True},
        }
    ]
    labels = [{"clip_id": "c_lie", "coach_id": "coach_a"}]
    p = gates.get_progress(_dir(tmp_path, clips, labels))
    assert p["wr_labeled"] == 0
    assert p["wr_athletes"] == 0
    assert p["surfaces"] == 0


def test_present_true_and_file_on_disk_does_count(tmp_path):
    clips = [
        {
            "clip_id": "c_real",
            "position_target": "WR",
            "movement": "release",
            "athlete_id": "ath_x",
            "surface": "turf",
            "lighting": "daylight",
            "camera_side": {"path": "clips/c_real.mp4", "present": True},
        }
    ]
    (tmp_path / "clips").mkdir()
    (tmp_path / "clips" / "c_real.mp4").write_bytes(b"x")
    (tmp_path / "labels").mkdir()
    (tmp_path / "manifest.json").write_text(json.dumps({"clips": clips}))
    (tmp_path / "labels" / "l0.json").write_text(
        json.dumps({
            "clip_id": "c_real",
            "coach_id": "coach_a",
            "events": {name: {"t_ms": 100} for name in EVENTS["release"]},
            "cues": {name: {"value": 1.0, "disputed": False} for name in CUES["release"]},
        })
    )
    p = gates.get_progress(tmp_path)
    assert p["wr_labeled"] == 1
    assert p["wr_athletes"] == 1
    assert p["surfaces"] == 1
