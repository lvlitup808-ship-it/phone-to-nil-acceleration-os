"""Honesty pin: one camera file cannot film two clips.

has_film used to accept any non-empty path. Two manifest rows that resolve
to the same file (same relative path, or a .. alias) must not both increment
wr_labeled. The first clip in manifest order may count; the duplicate does not.
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


def _write(tmp_path, clips: list[dict]) -> None:
    (tmp_path / "labels").mkdir()
    (tmp_path / "clips").mkdir()
    (tmp_path / "clips" / "shared.mp4").write_bytes(b"film")
    (tmp_path / "clips" / "other.mp4").write_bytes(b"other-film")
    (tmp_path / "manifest.json").write_text(
        json.dumps({"clips": clips, "labeling_protocol_version": "1.0.0"})
    )
    for clip in clips:
        (tmp_path / "labels" / f"{clip['clip_id']}.json").write_text(
            json.dumps(_label(clip["clip_id"], "coach_a"))
        )


def test_shared_camera_file_counts_once(tmp_path):
    _write(
        tmp_path,
        [
            _clip("c1", "clips/shared.mp4", "ath_1", "turf"),
            _clip("c2", "clips/shared.mp4", "ath_2", "grass"),
        ],
    )
    progress = gates.get_progress(tmp_path)
    assert progress["wr_labeled"] == 1
    assert progress["wr_athletes"] == 1
    assert progress["surfaces"] == 1


def test_path_alias_of_same_file_counts_once(tmp_path):
    _write(
        tmp_path,
        [
            _clip("c1", "clips/shared.mp4", "ath_1", "turf"),
            _clip("c2", "clips/../clips/shared.mp4", "ath_2", "grass"),
        ],
    )
    progress = gates.get_progress(tmp_path)
    assert progress["wr_labeled"] == 1
    assert progress["surfaces"] == 1


def test_distinct_camera_files_still_count(tmp_path):
    _write(
        tmp_path,
        [
            _clip("c1", "clips/shared.mp4", "ath_1", "turf"),
            _clip("c2", "clips/other.mp4", "ath_2", "grass"),
        ],
    )
    progress = gates.get_progress(tmp_path)
    assert progress["wr_labeled"] == 2
    assert progress["wr_athletes"] == 2
    assert progress["surfaces"] == 2
