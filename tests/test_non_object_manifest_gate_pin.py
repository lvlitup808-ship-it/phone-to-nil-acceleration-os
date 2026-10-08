"""Honesty pin: a non-object manifest clip or camera block is not film.

A string in clips contains the substring clip_id, and a string camera_side
has no .get. Either used to raise and 500 GET /gates/golden. Junk must be
skipped. A sibling object clip with a real camera file still counts.
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


def _write(tmp_path, clips: list) -> None:
    (tmp_path / "labels").mkdir()
    (tmp_path / "clips").mkdir()
    (tmp_path / "clips" / "c1.mp4").write_bytes(b"film")
    (tmp_path / "manifest.json").write_text(
        json.dumps({"labeling_protocol_version": "1.0.0", "clips": clips})
    )
    (tmp_path / "labels" / "c1_coach_a.json").write_text(
        json.dumps(_label("c1", "coach_a"))
    )


def test_string_and_int_clips_do_not_crash_or_count(tmp_path):
    _write(
        tmp_path,
        [
            "clip_id",
            1,
            ["clip_id"],
            None,
            {
                "clip_id": "c1",
                "position_target": "WR",
                "movement": "release",
                "athlete_id": "ath_1",
                "surface": "turf",
                "lighting": "day",
                "camera_side": {"path": "clips/c1.mp4", "present": True},
            },
        ],
    )
    progress = gates.get_progress(tmp_path)
    assert progress["wr_labeled"] == 1
    assert progress["wr_athletes"] == 1


def test_string_camera_block_is_not_film(tmp_path):
    _write(
        tmp_path,
        [
            {
                "clip_id": "c1",
                "position_target": "WR",
                "movement": "release",
                "athlete_id": "ath_1",
                "surface": "turf",
                "lighting": "day",
                "camera_side": "clips/c1.mp4",
                "camera_45": ["clips/c1.mp4"],
            }
        ],
    )
    progress = gates.get_progress(tmp_path)
    assert progress["wr_labeled"] == 0
    assert progress["wr_athletes"] == 0
    assert progress["surfaces"] == 0
