"""Honesty pin: NaN and infinite cue values do not complete a coach label.

A hand-written label can set every cue value to NaN or Infinity. Those are
floats, so the gate treated the file as a full label and counted the clip.
A non-finite number is not a measurement.
"""

from __future__ import annotations

import json

from services.api import gates
from services.golden_set.labels import CUES, EVENTS


def _label(cue_value: float) -> dict:
    return {
        "clip_id": "c1",
        "coach_id": "coach_a",
        "events": {name: {"t_ms": 100} for name in EVENTS["release"]},
        "cues": {name: {"value": cue_value, "disputed": False} for name in CUES["release"]},
    }


def _golden(tmp_path, cue_value: float) -> None:
    (tmp_path / "labels").mkdir()
    (tmp_path / "clips").mkdir()
    (tmp_path / "clips" / "c1.mp4").write_bytes(b"\x00\x00\x00\x10ftypisom\x00\x00\x00\x00x")
    (tmp_path / "manifest.json").write_text(
        json.dumps(
            {
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
                ]
            }
        )
    )
    (tmp_path / "labels" / "c1_coach_a.json").write_text(
        json.dumps(_label(cue_value))
    )


def test_nan_cue_values_do_not_count_as_a_label(tmp_path):
    _golden(tmp_path, float("nan"))
    progress = gates.get_progress(tmp_path)
    assert progress["wr_labeled"] == 0
    assert progress["wr_athletes"] == 0
    assert progress["surfaces"] == 0


def test_infinite_cue_values_do_not_count_as_a_label(tmp_path):
    _golden(tmp_path, float("inf"))
    progress = gates.get_progress(tmp_path)
    assert progress["wr_labeled"] == 0
    assert progress["inter_rater_clips"] == 0


def test_finite_cue_value_still_counts(tmp_path):
    _golden(tmp_path, 1.0)
    progress = gates.get_progress(tmp_path)
    assert progress["wr_labeled"] == 1
