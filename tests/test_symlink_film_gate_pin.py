"""Honesty pin: a symlink is not camera film.

resolve() follows a link, so a symlink to a non-empty file inside the golden
root would otherwise count as filmed. A link is not the clip on disk. A
symlink-only camera does not increment wr_labeled. A second row that is only
a symlink to the first clip's file does not add an athlete or a surface.
"""

from __future__ import annotations

import json

from services.api import gates
from services.golden_set.labels import CUES, EVENTS


def _label(clip_id: str, coach: str) -> dict:
    return {
        "clip_id": clip_id,
        "coach_id": coach,
        "labeling_protocol_version": "1.0.0",
        "events": {name: {"t_ms": 100} for name in EVENTS["release"]},
        "cues": {name: {"value": 1.0, "disputed": False} for name in CUES["release"]},
    }


def _clip(clip_id: str, path: str, athlete: str, surface: str) -> dict:
    return {
        "clip_id": clip_id,
        "position_target": "WR",
        "movement": "release",
        "athlete_id": athlete,
        "surface": surface,
        "lighting": "day",
        "camera_side": {"path": path, "present": True},
    }


def test_symlink_only_camera_does_not_count(tmp_path):
    (tmp_path / "labels").mkdir()
    (tmp_path / "clips").mkdir()
    real = tmp_path / "clips" / "bytes.mp4"
    real.write_bytes(b"\x00\x00\x00\x18ftypisom" + b"film")
    link = tmp_path / "clips" / "c1.mp4"
    link.symlink_to(real)
    clip = _clip("c1", "clips/c1.mp4", "ath_1", "turf")
    (tmp_path / "manifest.json").write_text(
        json.dumps({"clips": [clip], "labeling_protocol_version": "1.0.0"})
    )
    (tmp_path / "labels" / "c1.json").write_text(json.dumps(_label("c1", "coach_a")))
    progress = gates.get_progress(tmp_path)
    assert progress["wr_labeled"] == 0
    assert progress["wr_athletes"] == 0
    assert progress["surfaces"] == 0


def test_symlink_to_another_clip_does_not_count_twice(tmp_path):
    (tmp_path / "labels").mkdir()
    (tmp_path / "clips").mkdir()
    original = tmp_path / "clips" / "c1.mp4"
    original.write_bytes(b"\x00\x00\x00\x18ftypisom" + b"film")
    (tmp_path / "clips" / "c2.mp4").symlink_to(original)
    clips = [
        _clip("c1", "clips/c1.mp4", "ath_1", "turf"),
        _clip("c2", "clips/c2.mp4", "ath_2", "grass"),
    ]
    (tmp_path / "manifest.json").write_text(
        json.dumps({"clips": clips, "labeling_protocol_version": "1.0.0"})
    )
    for clip in clips:
        (tmp_path / "labels" / f"{clip['clip_id']}.json").write_text(
            json.dumps(_label(clip["clip_id"], "coach_a"))
        )
    progress = gates.get_progress(tmp_path)
    assert progress["wr_labeled"] == 1
    assert progress["wr_athletes"] == 1
    assert progress["surfaces"] == 1


def test_real_file_still_counts_when_other_angle_is_symlink(tmp_path):
    (tmp_path / "labels").mkdir()
    (tmp_path / "clips").mkdir()
    side = tmp_path / "clips" / "side.mp4"
    side.write_bytes(b"\x00\x00\x00\x18ftypisom" + b"film")
    (tmp_path / "clips" / "angle.mp4").symlink_to(side)
    clip = _clip("c1", "clips/side.mp4", "ath_1", "turf")
    clip["camera_45"] = {"path": "clips/angle.mp4", "present": True}
    (tmp_path / "manifest.json").write_text(
        json.dumps({"clips": [clip], "labeling_protocol_version": "1.0.0"})
    )
    (tmp_path / "labels" / "c1.json").write_text(json.dumps(_label("c1", "coach_a")))
    progress = gates.get_progress(tmp_path)
    assert progress["wr_labeled"] == 1
