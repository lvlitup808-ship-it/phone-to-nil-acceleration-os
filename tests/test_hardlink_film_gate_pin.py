"""Honesty pin: a hardlink is the same film, not a second clip.

Path identity already stops two rows that resolve to the same path. A second
inode path that is a hardlink of the first camera file must not increment
wr_labeled, athletes, or surfaces. The first manifest row keeps the file.
"""

from __future__ import annotations

import json
import os

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


def _write(tmp_path) -> None:
    (tmp_path / "labels").mkdir()
    (tmp_path / "clips").mkdir()
    original = tmp_path / "clips" / "c1.mp4"
    original.write_bytes(b"film")
    os.link(original, tmp_path / "clips" / "c2.mp4")
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


def test_hardlink_of_camera_file_counts_once(tmp_path):
    _write(tmp_path)
    progress = gates.get_progress(tmp_path)
    assert progress["wr_labeled"] == 1
    assert progress["wr_athletes"] == 1
    assert progress["surfaces"] == 1


def test_same_clip_side_and_45_hardlink_still_counts(tmp_path):
    (tmp_path / "labels").mkdir()
    (tmp_path / "clips").mkdir()
    side = tmp_path / "clips" / "side.mp4"
    side.write_bytes(b"film")
    os.link(side, tmp_path / "clips" / "angle.mp4")
    clip = {
        "clip_id": "c1",
        "position_target": "WR",
        "movement": "release",
        "athlete_id": "ath_1",
        "surface": "turf",
        "lighting": "day",
        "camera_side": {"path": "clips/side.mp4", "present": True},
        "camera_45": {"path": "clips/angle.mp4", "present": True},
    }
    (tmp_path / "manifest.json").write_text(
        json.dumps({"clips": [clip], "labeling_protocol_version": "1.0.0"})
    )
    (tmp_path / "labels" / "c1.json").write_text(json.dumps(_label("c1", "coach_a")))
    progress = gates.get_progress(tmp_path)
    assert progress["wr_labeled"] == 1
