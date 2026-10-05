"""Honesty pin: a non-object label file must not crash or open the gate.

Hand-dropped labels/*.json can be a JSON array or string. get_progress must
skip those files. A crash would 500 GET /gates/golden; treating them as labels
would inflate wr_labeled.
"""

from __future__ import annotations

import json

from services.api import gates
from services.golden_set.labels import CUES, EVENTS


def _clip(tmp_path):
    (tmp_path / "labels").mkdir()
    (tmp_path / "clips").mkdir()
    (tmp_path / "clips" / "c1.mp4").write_bytes(b"x")
    clip = {
        "clip_id": "c1",
        "position_target": "WR",
        "movement": "release",
        "athlete_id": "ath_1",
        "surface": "turf",
        "lighting": "day",
        "camera_side": {"path": "clips/c1.mp4", "present": True},
    }
    (tmp_path / "manifest.json").write_text(json.dumps({"clips": [clip]}))
    return clip


def test_array_label_does_not_count_or_raise(tmp_path):
    _clip(tmp_path)
    (tmp_path / "labels" / "array.json").write_text(
        json.dumps([{"clip_id": "c1", "coach_id": "coach_a"}])
    )
    progress = gates.get_progress(tmp_path)
    assert progress["wr_labeled"] == 0
    assert progress["inter_rater_clips"] == 0


def test_string_label_does_not_count_or_raise(tmp_path):
    _clip(tmp_path)
    (tmp_path / "labels" / "string.json").write_text(json.dumps("c1"))
    progress = gates.get_progress(tmp_path)
    assert progress["wr_labeled"] == 0


def test_object_label_still_counts_beside_junk(tmp_path):
    _clip(tmp_path)
    (tmp_path / "labels" / "array.json").write_text(json.dumps([1, 2]))
    (tmp_path / "labels" / "full.json").write_text(
        json.dumps(
            {
                "clip_id": "c1",
                "coach_id": "coach_a",
                "events": {name: {"t_ms": 100} for name in EVENTS["release"]},
                "cues": {name: {"value": 1.0, "disputed": False} for name in CUES["release"]},
            }
        )
    )
    progress = gates.get_progress(tmp_path)
    assert progress["wr_labeled"] == 1
