"""Honesty pin: a non-video path must not count as golden-set film.

has_film used to accept any file under the golden dir once present was true.
A hand-edited manifest can point camera_side at manifest.json or labels/*.json
and a complete coach label would then open wr_labeled without a phone clip.
Only a non-empty video directly in clips/ counts.
"""

from __future__ import annotations

import json

from services.api import gates
from services.golden_set.labels import CUES, EVENTS


def _label() -> dict:
    return {
        "clip_id": "c1",
        "coach_id": "coach_a",
        "events": {name: {"t_ms": 100} for name in EVENTS["release"]},
        "cues": {name: {"value": 1.0, "disputed": False} for name in CUES["release"]},
    }


def _tree(tmp_path, camera_path: str) -> None:
    (tmp_path / "labels").mkdir()
    (tmp_path / "clips").mkdir()
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
                        "camera_side": {"path": camera_path, "present": True},
                    }
                ]
            }
        )
    )
    (tmp_path / "labels" / "c1_coach_a.json").write_text(json.dumps(_label()))


def test_json_path_is_not_film(tmp_path):
    _tree(tmp_path, "manifest.json")
    assert gates.has_film(json.loads((tmp_path / "manifest.json").read_text())["clips"][0], tmp_path) is False
    progress = gates.get_progress(tmp_path)
    assert progress["wr_labeled"] == 0
    assert progress["surfaces"] == 0
    assert progress["wr_athletes"] == 0


def test_label_file_path_is_not_film(tmp_path):
    _tree(tmp_path, "labels/c1_coach_a.json")
    progress = gates.get_progress(tmp_path)
    assert progress["wr_labeled"] == 0


def test_empty_mp4_is_not_film(tmp_path):
    _tree(tmp_path, "clips/c1.mp4")
    (tmp_path / "clips" / "c1.mp4").write_bytes(b"")
    assert gates.has_film(json.loads((tmp_path / "manifest.json").read_text())["clips"][0], tmp_path) is False
    assert gates.get_progress(tmp_path)["wr_labeled"] == 0


def test_nonempty_mp4_in_clips_still_counts(tmp_path):
    _tree(tmp_path, "clips/c1.mp4")
    (tmp_path / "clips" / "c1.mp4").write_bytes(b"x")
    progress = gates.get_progress(tmp_path)
    assert progress["wr_labeled"] == 1
    assert progress["wr_athletes"] == 1
