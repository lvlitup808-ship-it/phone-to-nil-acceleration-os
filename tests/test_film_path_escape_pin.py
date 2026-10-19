"""Honesty pin: a film path outside the golden dir is not film.

present:true is not enough. Absolute paths and ../ escapes must not count
toward wr_labeled even when the bytes exist somewhere else on disk.
"""

from __future__ import annotations

import json

from services.api import gates


def _label(tmp_path, clip):
    (tmp_path / "labels").mkdir()
    (tmp_path / "manifest.json").write_text(json.dumps({"clips": [clip]}))
    (tmp_path / "labels" / "l0.json").write_text(
        json.dumps({"clip_id": "c1", "coach_id": "coach_a"})
    )


def test_path_escape_does_not_count_as_film(tmp_path):
    outside = tmp_path.parent / "outside_film.mp4"
    outside.write_bytes(b"x")
    golden = tmp_path / "golden"
    golden.mkdir()
    clip = {
        "clip_id": "c1",
        "position_target": "WR",
        "athlete_id": "ath_1",
        "surface": "turf",
        "lighting": "day",
        "camera_side": {"path": "../outside_film.mp4", "present": True},
    }
    _label(golden, clip)
    assert gates.has_film(clip, golden) is False
    progress = gates.get_progress(golden)
    assert progress["wr_labeled"] == 0
    assert progress["surfaces"] == 0
    outside.unlink(missing_ok=True)


def test_absolute_path_does_not_count_as_film(tmp_path):
    film = tmp_path / "real.mp4"
    film.write_bytes(b"x")
    golden = tmp_path / "golden"
    golden.mkdir()
    clip = {
        "clip_id": "c1",
        "position_target": "DB",
        "athlete_id": "ath_1",
        "surface": "grass",
        "lighting": "night",
        "camera_45": {"path": str(film), "present": True},
    }
    _label(golden, clip)
    assert gates.has_film(clip, golden) is False
    progress = gates.get_progress(golden)
    assert progress["db_labeled"] == 0
    assert progress["db_athletes"] == 0
