"""Honesty pin: case variants do not inflate the film-first gate.

Inter-rater is two coaches, not two spellings of one coach. Surfaces, lighting,
and athlete ids are the same condition when they differ only by case.
"""

from __future__ import annotations

import json

from services.api import gates


def test_case_variants_do_not_inflate_gate(tmp_path):
    (tmp_path / "labels").mkdir()
    (tmp_path / "clips").mkdir()
    (tmp_path / "clips" / "c1.mp4").write_bytes(b"x")
    (tmp_path / "clips" / "c2.mp4").write_bytes(b"x")
    clips = [
        {
            "clip_id": "c1",
            "position_target": "WR",
            "athlete_id": "Ath_1",
            "surface": "Turf",
            "lighting": "Day",
            "camera_side": {"path": "clips/c1.mp4", "present": True},
        },
        {
            "clip_id": "c2",
            "position_target": "WR",
            "athlete_id": "ath_1",
            "surface": "turf",
            "lighting": "day",
            "camera_side": {"path": "clips/c2.mp4", "present": True},
        },
    ]
    (tmp_path / "manifest.json").write_text(json.dumps({"clips": clips}))
    (tmp_path / "labels" / "a.json").write_text(
        json.dumps({"clip_id": "c1", "coach_id": "Coach_A"})
    )
    (tmp_path / "labels" / "b.json").write_text(
        json.dumps({"clip_id": "c1", "coach_id": "coach_a"})
    )
    (tmp_path / "labels" / "c.json").write_text(
        json.dumps({"clip_id": "c2", "coach_id": "coach_b"})
    )
    progress = gates.get_progress(tmp_path)
    assert progress["wr_labeled"] == 2
    assert progress["inter_rater_clips"] == 0
    assert progress["inter_rater_done"] is False
    assert progress["surfaces"] == 1
    assert progress["lighting_conditions"] == 1
    assert progress["wr_athletes"] == 1
