"""Honesty pin: one camera file cannot count as two golden-set clips.

Two manifest rows that resolve to the same on-disk path (including path
aliases) must not inflate wr_labeled, athlete, or surface counts.
"""

from __future__ import annotations

import json

from services.api import gates
from services.golden_set.labels import CUES, EVENTS


def _label(clip_id: str) -> dict:
    return {
        "clip_id": clip_id,
        "coach_id": "coach_a",
        "events": {name: {"t_ms": 100} for name in EVENTS["release"]},
        "cues": {name: {"value": 1.0, "disputed": False} for name in CUES["release"]},
    }


def _clip(clip_id: str, path: str, athlete_id: str, surface: str) -> dict:
    return {
        "clip_id": clip_id,
        "position_target": "WR",
        "movement": "release",
        "athlete_id": athlete_id,
        "surface": surface,
        "lighting": "daylight",
        "camera_side": {"path": path, "present": True},
    }


def test_same_film_path_counts_once(tmp_path):
    (tmp_path / "clips").mkdir()
    (tmp_path / "labels").mkdir()
    (tmp_path / "clips" / "same.mp4").write_bytes(b"same-bytes")
    clips = [
        _clip("c1", "clips/same.mp4", "ath_1", "turf"),
        _clip("c2", "clips/same.mp4", "ath_2", "grass"),
    ]
    (tmp_path / "manifest.json").write_text(json.dumps({"clips": clips}))
    for clip in clips:
        (tmp_path / "labels" / f"{clip['clip_id']}.json").write_text(json.dumps(_label(clip["clip_id"])))
    progress = gates.get_progress(tmp_path)
    assert progress["wr_labeled"] == 1
    assert progress["wr_athletes"] == 1
    assert progress["surfaces"] == 1


def test_path_alias_of_same_file_counts_once(tmp_path):
    (tmp_path / "clips").mkdir()
    (tmp_path / "labels").mkdir()
    (tmp_path / "clips" / "same.mp4").write_bytes(b"same-bytes")
    clips = [
        _clip("c1", "clips/same.mp4", "ath_1", "turf"),
        _clip("c2", "clips/../clips/same.mp4", "ath_2", "grass"),
    ]
    (tmp_path / "manifest.json").write_text(json.dumps({"clips": clips}))
    for clip in clips:
        (tmp_path / "labels" / f"{clip['clip_id']}.json").write_text(json.dumps(_label(clip["clip_id"])))
    progress = gates.get_progress(tmp_path)
    assert progress["wr_labeled"] == 1
    assert progress["surfaces"] == 1
