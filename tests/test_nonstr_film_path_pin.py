"""Honesty pin: a camera path that is not a real file inside the golden root does not count.

A non-string path is a hand edit, not film, and must not crash GET /gates/golden.
A directory is not film. A path that resolves outside the golden root is not film.
None of those inflate wr_labeled, athletes, or surfaces.
"""

from __future__ import annotations

import json

from services.api import gates
from services.golden_set.labels import CUES, EVENTS


def _label(clip_id: str) -> dict:
    return {
        "clip_id": clip_id,
        "coach_id": "coach_a",
        "labeling_protocol_version": "1.0.0",
        "events": {name: {"t_ms": 100} for name in EVENTS["release"]},
        "cues": {name: {"value": 1.0, "disputed": False} for name in CUES["release"]},
    }


def _clip(clip_id: str, path, athlete: str, surface: str) -> dict:
    return {
        "clip_id": clip_id,
        "position_target": "WR",
        "movement": "release",
        "athlete_id": athlete,
        "surface": surface,
        "lighting": "day",
        "camera_side": {"path": path, "present": True},
    }


def _write(tmp_path, clips: list[dict]) -> None:
    (tmp_path / "labels").mkdir()
    (tmp_path / "manifest.json").write_text(
        json.dumps({"clips": clips, "labeling_protocol_version": "1.0.0"})
    )
    for clip in clips:
        (tmp_path / "labels" / f"{clip['clip_id']}.json").write_text(
            json.dumps(_label(clip["clip_id"]))
        )


def test_non_string_camera_path_does_not_crash_or_count(tmp_path):
    clips = [
        _clip("c_list", ["clips", "c.mp4"], "ath_1", "turf"),
        _clip("c_num", 1, "ath_2", "grass"),
    ]
    _write(tmp_path, clips)
    progress = gates.get_progress(tmp_path)
    assert progress["wr_labeled"] == 0
    assert progress["wr_athletes"] == 0
    assert progress["surfaces"] == 0


def test_directory_camera_path_does_not_count(tmp_path):
    (tmp_path / "clips").mkdir()
    (tmp_path / "clips" / "c1.mp4").mkdir()
    _write(tmp_path, [_clip("c1", "clips/c1.mp4", "ath_1", "turf")])
    progress = gates.get_progress(tmp_path)
    assert progress["wr_labeled"] == 0
    assert progress["wr_athletes"] == 0
    assert progress["surfaces"] == 0


def test_path_outside_golden_root_does_not_count(tmp_path):
    outside = tmp_path.parent / "outside-film.mp4"
    outside.write_bytes(b"film")
    _write(tmp_path, [_clip("c1", "../outside-film.mp4", "ath_1", "turf")])
    progress = gates.get_progress(tmp_path)
    assert progress["wr_labeled"] == 0
    assert progress["wr_athletes"] == 0
    assert progress["surfaces"] == 0
    outside.unlink(missing_ok=True)


def test_real_file_still_counts_beside_a_bad_path(tmp_path):
    (tmp_path / "clips").mkdir()
    (tmp_path / "clips" / "c_ok.mp4").write_bytes(b"film")
    clips = [
        _clip("c_bad", ["clips", "nope.mp4"], "ath_1", "turf"),
        _clip("c_ok", "clips/c_ok.mp4", "ath_2", "grass"),
    ]
    _write(tmp_path, clips)
    progress = gates.get_progress(tmp_path)
    assert progress["wr_labeled"] == 1
    assert progress["wr_athletes"] == 1
    assert progress["surfaces"] == 1
