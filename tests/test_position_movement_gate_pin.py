"""Honesty pin: a DB clip labeled as a WR release is not a DB golden clip.

film_first.md freezes WR release and DB break. The gate used to count any
movement in EVENTS toward that position's bar, so a DB row with release cues
inflated db_labeled, surfaces, and inter-rater. Only WR+release and DB+break
count. Gate stays closed.
"""

from __future__ import annotations

import json

from services.api import gates
from services.golden_set.labels import CUES, EVENTS


def _seed(tmp_path, position: str, movement: str, coaches: int = 1):
    (tmp_path / "labels").mkdir()
    (tmp_path / "clips").mkdir()
    (tmp_path / "clips" / "c1.mp4").write_bytes(b"\x00\x00\x00\x18ftypisom\x00\x00\x00\x00film")
    for i in range(coaches):
        label = {
            "clip_id": "c1",
            "coach_id": f"coach_{i}",
            "labeling_protocol_version": "1.0.0",
            "events": {name: {"t_ms": 100} for name in EVENTS[movement]},
            "cues": {name: {"value": 1} for name in CUES[movement]},
        }
        (tmp_path / "labels" / f"c1_coach_{i}.json").write_text(json.dumps(label))
    (tmp_path / "manifest.json").write_text(
        json.dumps(
            {
                "labeling_protocol_version": "1.0.0",
                "clips": [
                    {
                        "clip_id": "c1",
                        "position_target": position,
                        "movement": movement,
                        "athlete_id": "ath_1",
                        "surface": "turf",
                        "lighting": "day",
                        "camera_side": {"path": "clips/c1.mp4", "present": True, "fps": 60},
                    }
                ],
            }
        )
    )


def test_db_release_does_not_count(tmp_path):
    _seed(tmp_path, "DB", "release", coaches=2)
    progress = gates.get_progress(tmp_path)
    assert progress["db_labeled"] == 0
    assert progress["wr_labeled"] == 0
    assert progress["inter_rater_clips"] == 0
    assert progress["surfaces"] == 0
    assert progress["db_athletes"] == 0


def test_wr_break_does_not_count(tmp_path):
    _seed(tmp_path, "WR", "break")
    progress = gates.get_progress(tmp_path)
    assert progress["wr_labeled"] == 0
    assert progress["db_labeled"] == 0
    assert progress["surfaces"] == 0


def test_db_break_still_counts(tmp_path):
    _seed(tmp_path, "DB", "break", coaches=2)
    progress = gates.get_progress(tmp_path)
    assert progress["db_labeled"] == 1
    assert progress["inter_rater_clips"] == 1
    assert progress["db_athletes"] == 1
