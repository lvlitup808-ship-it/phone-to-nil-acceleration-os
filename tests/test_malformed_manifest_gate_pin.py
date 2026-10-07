"""Honesty pin: a malformed manifest does not crash or open the gate.

GET /gates/golden reads data/golden_set/manifest.json. clips must be a list of
objects with a string clip_id. A dict, a string, or a non-object row is not a
filmed clip and must not raise.
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


def _film(tmp_path, clip_id: str) -> None:
    (tmp_path / "labels").mkdir(exist_ok=True)
    (tmp_path / "clips").mkdir(exist_ok=True)
    (tmp_path / "clips" / f"{clip_id}.mp4").write_bytes(b"film")
    (tmp_path / "labels" / f"{clip_id}.json").write_text(json.dumps(_label(clip_id)))


def test_non_list_clips_do_not_crash_or_count(tmp_path):
    _film(tmp_path, "c1")
    (tmp_path / "manifest.json").write_text(
        json.dumps(
            {
                "clips": {"clip_id": "c1", "position_target": "WR"},
                "labeling_protocol_version": "1.0.0",
            }
        )
    )
    progress = gates.get_progress(tmp_path)
    assert progress["wr_labeled"] == 0
    assert progress["db_labeled"] == 0
    assert gates.prescription_enabled(progress) is False


def test_non_object_clip_rows_do_not_crash_or_count(tmp_path):
    _film(tmp_path, "c1")
    good = {
        "clip_id": "c1",
        "position_target": "WR",
        "movement": "release",
        "athlete_id": "ath_1",
        "surface": "turf",
        "lighting": "day",
        "camera_side": {"path": "clips/c1.mp4", "present": True},
    }
    (tmp_path / "manifest.json").write_text(
        json.dumps(
            {
                "clips": ["c1", 1, None, {"position_target": "WR"}, good],
                "labeling_protocol_version": "1.0.0",
            }
        )
    )
    progress = gates.get_progress(tmp_path)
    assert progress["wr_labeled"] == 1
    assert progress["wr_athletes"] == 1


def test_non_string_clip_id_does_not_count(tmp_path):
    _film(tmp_path, "1")
    (tmp_path / "manifest.json").write_text(
        json.dumps(
            {
                "clips": [
                    {
                        "clip_id": 1,
                        "position_target": "WR",
                        "movement": "release",
                        "athlete_id": "ath_1",
                        "surface": "turf",
                        "lighting": "day",
                        "camera_side": {"path": "clips/1.mp4", "present": True},
                    }
                ],
                "labeling_protocol_version": "1.0.0",
            }
        )
    )
    progress = gates.get_progress(tmp_path)
    assert progress["wr_labeled"] == 0
