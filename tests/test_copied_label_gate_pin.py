"""Honesty pin: a copied label packet is not a second coach.

Inter-rater is two coaches on the same filmed clip. Copying the events and
cues and changing coach_id used to inflate inter_rater_clips. Same
measurements are one annotation. A different timestamp still counts.
"""

from __future__ import annotations

import json

from services.api import gates
from services.golden_set.labels import CUES, EVENTS


def _label(clip_id: str, coach: str, t_ms: int) -> dict:
    return {
        "clip_id": clip_id,
        "coach_id": coach,
        "labeling_protocol_version": "1.0.0",
        "events": {name: {"t_ms": t_ms} for name in EVENTS["release"]},
        "cues": {name: {"value": 1.0, "disputed": False} for name in CUES["release"]},
    }


def _seed(tmp_path) -> None:
    (tmp_path / "clips").mkdir()
    (tmp_path / "labels").mkdir()
    (tmp_path / "clips" / "c1.mp4").write_bytes(b"film-not-a-fixture")
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


def test_copied_measurements_are_not_a_second_coach(tmp_path):
    _seed(tmp_path)
    (tmp_path / "labels" / "c1_coach_a.json").write_text(
        json.dumps(_label("c1", "coach_a", 100))
    )
    (tmp_path / "labels" / "c1_coach_b.json").write_text(
        json.dumps(_label("c1", "coach_b", 100))
    )
    progress = gates.get_progress(tmp_path)
    assert progress["wr_labeled"] == 1
    assert progress["inter_rater_clips"] == 0
    assert progress["inter_rater_done"] is False


def test_different_measurements_still_count_as_inter_rater(tmp_path):
    _seed(tmp_path)
    (tmp_path / "labels" / "c1_coach_a.json").write_text(
        json.dumps(_label("c1", "coach_a", 100))
    )
    (tmp_path / "labels" / "c1_coach_b.json").write_text(
        json.dumps(_label("c1", "coach_b", 240))
    )
    progress = gates.get_progress(tmp_path)
    assert progress["wr_labeled"] == 1
    assert progress["inter_rater_clips"] == 1
