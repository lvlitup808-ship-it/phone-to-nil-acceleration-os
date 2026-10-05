"""Honesty pin: only boolean True marks a camera as film.

cam.get("present") is truthy for the strings "false" and "true". A hand-edited
manifest can set present to a non-bool and drop a file under data/golden_set/.
That must not count toward wr_labeled. Fixture present flags stay boolean.
"""

from __future__ import annotations

import json

from services.api import gates
from services.golden_set.labels import CUES, EVENTS


def _seed(tmp_path, present):
    (tmp_path / "labels").mkdir()
    (tmp_path / "clips").mkdir()
    (tmp_path / "clips" / "c1.mp4").write_bytes(b"x")
    clip = {
        "clip_id": "c1",
        "position_target": "WR",
        "movement": "release",
        "athlete_id": "ath_1",
        "surface": "turf",
        "lighting": "day",
        "camera_side": {"path": "clips/c1.mp4", "present": present},
    }
    (tmp_path / "manifest.json").write_text(json.dumps({"clips": [clip]}))
    label = {
        "clip_id": "c1",
        "coach_id": "coach_a",
        "labeling_protocol_version": "1.0.0",
        "events": {name: {"t_ms": 100} for name in EVENTS["release"]},
        "cues": {name: {"value": 1.0, "disputed": False} for name in CUES["release"]},
    }
    (tmp_path / "labels" / "c1_coach_a.json").write_text(json.dumps(label))
    return clip


def test_string_false_present_with_file_is_not_film(tmp_path):
    clip = _seed(tmp_path, "false")
    assert gates.has_film(clip, tmp_path) is False
    progress = gates.get_progress(tmp_path)
    assert progress["wr_labeled"] == 0
    assert progress["surfaces"] == 0
    assert progress["wr_athletes"] == 0


def test_string_true_present_with_file_is_not_film(tmp_path):
    clip = _seed(tmp_path, "true")
    assert gates.has_film(clip, tmp_path) is False
    progress = gates.get_progress(tmp_path)
    assert progress["wr_labeled"] == 0


def test_bool_true_present_with_file_counts(tmp_path):
    clip = _seed(tmp_path, True)
    assert gates.has_film(clip, tmp_path) is True
    progress = gates.get_progress(tmp_path)
    assert progress["wr_labeled"] == 1
