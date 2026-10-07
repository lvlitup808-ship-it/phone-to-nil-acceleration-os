"""Honesty pin: non-object manifest clip rows do not crash the gate.

docs/film_first.md derives the gate from data/golden_set/manifest.json.
A clips value that is not a list, or a row that is not an object with a
string clip_id, is not film and must not crash GET /gates/golden.
A valid WR row in the same manifest still counts.
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


def _valid(clip_id: str) -> dict:
    return {
        "clip_id": clip_id,
        "position_target": "WR",
        "movement": "release",
        "athlete_id": "ath_1",
        "surface": "turf",
        "lighting": "day",
        "camera_side": {"path": f"clips/{clip_id}.mp4", "present": True},
    }


def test_non_object_clip_rows_do_not_crash_or_count(tmp_path):
    (tmp_path / "labels").mkdir()
    (tmp_path / "clips").mkdir()
    (tmp_path / "clips" / "c1.mp4").write_bytes(b"film")
    (tmp_path / "labels" / "c1.json").write_text(json.dumps(_label("c1")))
    (tmp_path / "manifest.json").write_text(
        json.dumps(
            {
                "clips": [
                    1,
                    "nope",
                    None,
                    {"position_target": "WR"},
                    {"clip_id": 1, "position_target": "WR"},
                    {"clip_id": ["c1"], "position_target": "WR"},
                    {"clip_id": "  ", "position_target": "WR"},
                    _valid("c1"),
                ],
                "labeling_protocol_version": "1.0.0",
            }
        )
    )
    progress = gates.get_progress(tmp_path)
    assert progress["wr_labeled"] == 1
    assert progress["wr_athletes"] == 1
    assert progress["surfaces"] == 1


def test_non_list_clips_does_not_crash_or_count(tmp_path):
    (tmp_path / "labels").mkdir()
    (tmp_path / "manifest.json").write_text(
        json.dumps({"clips": 1, "labeling_protocol_version": "1.0.0"})
    )
    progress = gates.get_progress(tmp_path)
    assert progress["wr_labeled"] == 0
    assert progress["db_labeled"] == 0
