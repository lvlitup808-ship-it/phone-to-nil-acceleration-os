"""Honesty pin: a non-object manifest must not crash or open the gate.

GET /gates/golden loads manifest.json. A hand-edited file that is an array,
string, or number is truthy, so `or {}` does not replace it and `.get` raises.
A clip row or camera object that is not a JSON object must be skipped, not raise.
A sibling object clip with a real label still counts. Gate stays closed.
"""

from __future__ import annotations

import json

from services.api import gates
from services.golden_set.labels import CUES, EVENTS


def _label() -> dict:
    return {
        "clip_id": "c1",
        "coach_id": "coach_a",
        "labeling_protocol_version": "1.0.0",
        "events": {name: {"t_ms": 100} for name in EVENTS["release"]},
        "cues": {name: {"value": 1.0, "disputed": False} for name in CUES["release"]},
    }


def _film(tmp_path) -> None:
    (tmp_path / "labels").mkdir()
    (tmp_path / "clips").mkdir()
    (tmp_path / "clips" / "c1.mp4").write_bytes(b"\x00\x00\x00\x18ftypisom\x00\x00\x00\x00film")
    (tmp_path / "labels" / "c1_coach_a.json").write_text(json.dumps(_label()))


def test_array_manifest_does_not_crash_or_count(tmp_path):
    _film(tmp_path)
    (tmp_path / "manifest.json").write_text(json.dumps([{"clip_id": "c1"}]))
    progress = gates.get_progress(tmp_path)
    assert progress["wr_labeled"] == 0
    assert progress["db_labeled"] == 0
    assert progress["inter_rater_clips"] == 0


def test_string_manifest_does_not_crash(tmp_path):
    _film(tmp_path)
    (tmp_path / "manifest.json").write_text(json.dumps("pending"))
    progress = gates.get_progress(tmp_path)
    assert progress["wr_labeled"] == 0


def test_non_object_clip_row_is_skipped(tmp_path):
    _film(tmp_path)
    (tmp_path / "manifest.json").write_text(
        json.dumps(
            {
                "labeling_protocol_version": "1.0.0",
                "clips": [
                    "clip_id",
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
            }
        )
    )
    progress = gates.get_progress(tmp_path)
    assert progress["wr_labeled"] == 1


def test_non_object_camera_does_not_count_as_film(tmp_path):
    _film(tmp_path)
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
                        "camera_side": "clips/c1.mp4",
                        "camera_45": ["present", True],
                    }
                ],
            }
        )
    )
    progress = gates.get_progress(tmp_path)
    assert progress["wr_labeled"] == 0
    assert not gates.has_film(
        {
            "camera_side": "clips/c1.mp4",
            "camera_45": ["present"],
        },
        tmp_path,
    )
