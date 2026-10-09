"""Honesty pin: a coerced or blank clip_id is not a golden-set clip.

get_progress used to accept any truthy string, including whitespace, and
str() a numeric label clip_id onto a manifest row. A hand edit could attach
a label to a row the intake form would never name. Gate stays closed.
"""

from __future__ import annotations

import json

from services.api import gates
from services.golden_set.labels import CUES, EVENTS


def _label(clip_id) -> dict:
    return {
        "clip_id": clip_id,
        "coach_id": "coach_a",
        "labeling_protocol_version": "1.0.0",
        "events": {name: {"t_ms": 100} for name in EVENTS["release"]},
        "cues": {name: {"value": 1.0, "disputed": False} for name in CUES["release"]},
    }


def _seed(tmp_path, clip_id, label_clip_id) -> None:
    (tmp_path / "labels").mkdir()
    (tmp_path / "clips").mkdir()
    (tmp_path / "clips" / "c1.mp4").write_bytes(b"x")
    (tmp_path / "labels" / "row.json").write_text(json.dumps(_label(label_clip_id)))
    (tmp_path / "manifest.json").write_text(
        json.dumps(
            {
                "clips": [
                    {
                        "clip_id": clip_id,
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


def test_blank_clip_id_does_not_count(tmp_path):
    _seed(tmp_path, "   ", "   ")
    assert gates.get_progress(tmp_path)["wr_labeled"] == 0


def test_numeric_label_clip_id_does_not_match(tmp_path):
    _seed(tmp_path, "1234", 1234)
    assert gates.get_progress(tmp_path)["wr_labeled"] == 0


def test_plain_clip_id_still_counts(tmp_path):
    _seed(tmp_path, "c1", "c1")
    progress = gates.get_progress(tmp_path)
    assert progress["wr_labeled"] == 1, progress
