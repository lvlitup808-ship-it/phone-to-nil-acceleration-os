"""Honesty pin: a symlink is not a coach label.

read_text() follows links, so labels/c1.json pointing at a complete label
would otherwise count. A link is not a label file on disk. A real label
still counts when a second coach file is only a symlink.
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


def _golden(tmp_path) -> None:
    (tmp_path / "labels").mkdir()
    (tmp_path / "clips").mkdir()
    (tmp_path / "clips" / "c1.mp4").write_bytes(b"\x00\x00\x00\x10ftypisom\x00\x00\x00\x00\x00\x00\x00\x0cmdatfilm")
    (tmp_path / "manifest.json").write_text(
        json.dumps(
            {
                "labeling_protocol_version": "1.0.0",
                "clips": [
                    {
                        "clip_id": "c1",
                        "position_target": "WR",
                        "movement": "release",
                        "athlete_id": "ath_1",
                        "surface": "turf",
                        "lighting": "day",
                        "camera_side": {"path": "clips/c1.mp4", "present": True},
                    }
                ],
            }
        )
    )


def test_symlink_label_does_not_count(tmp_path):
    _golden(tmp_path)
    real = tmp_path / "outside.json"
    real.write_text(json.dumps(_label("c1", "coach_a")))
    (tmp_path / "labels" / "c1_coach_a.json").symlink_to(real)
    progress = gates.get_progress(tmp_path)
    assert progress["wr_labeled"] == 0
    assert progress["wr_athletes"] == 0
    assert progress["inter_rater_clips"] == 0


def test_symlink_second_coach_does_not_count_as_inter_rater(tmp_path):
    _golden(tmp_path)
    (tmp_path / "labels" / "c1_coach_a.json").write_text(
        json.dumps(_label("c1", "coach_a"))
    )
    other = tmp_path / "outside.json"
    other.write_text(json.dumps(_label("c1", "coach_b")))
    (tmp_path / "labels" / "c1_coach_b.json").symlink_to(other)
    progress = gates.get_progress(tmp_path)
    assert progress["wr_labeled"] == 1
    assert progress["inter_rater_clips"] == 0


def test_regular_label_file_still_counts(tmp_path):
    _golden(tmp_path)
    (tmp_path / "labels" / "c1_coach_a.json").write_text(
        json.dumps(_label("c1", "coach_a"))
    )
    progress = gates.get_progress(tmp_path)
    assert progress["wr_labeled"] == 1
