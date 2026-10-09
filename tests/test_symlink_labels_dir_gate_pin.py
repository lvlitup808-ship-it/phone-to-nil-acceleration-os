"""Honesty pin: a symlinked labels directory is not the coach-label store.

Path.glob follows a directory symlink, and read_text follows the files inside
it. A labels/ link at a complete label packet must not open the golden-set
gate. A real labels directory still counts.
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


def _manifest(tmp_path) -> None:
    (tmp_path / "clips").mkdir()
    (tmp_path / "clips" / "c1.mp4").write_bytes(b"\x00\x00\x00\x10ftypisom\x00\x00\x00\x00\x00\x00\x00\x1amdatfilm-not-a-fixture")
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


def test_symlinked_labels_dir_does_not_count(tmp_path):
    _manifest(tmp_path)
    outside = tmp_path / "outside_labels"
    outside.mkdir()
    (outside / "c1_coach_a.json").write_text(json.dumps(_label("c1", "coach_a")))
    (tmp_path / "labels").symlink_to(outside, target_is_directory=True)
    progress = gates.get_progress(tmp_path)
    assert progress["wr_labeled"] == 0
    assert progress["wr_athletes"] == 0
    assert progress["inter_rater_clips"] == 0


def test_real_labels_dir_still_counts(tmp_path):
    _manifest(tmp_path)
    (tmp_path / "labels").mkdir()
    (tmp_path / "labels" / "c1_coach_a.json").write_text(
        json.dumps(_label("c1", "coach_a"))
    )
    progress = gates.get_progress(tmp_path)
    assert progress["wr_labeled"] == 1
