"""Honesty pin: a non-video file is not film.

has_film treated any non-empty file under the golden dir as film. A hand-edited
manifest can point camera_side.path at manifest.json or a label file, both
non-empty, and inflate wr_labeled. Only phone-video suffixes count.
"""

from __future__ import annotations

import json

from services.api import gates
from services.golden_set.labels import CUES, EVENTS


def _seed(tmp_path, rel_path: str, payload: bytes = b"not-a-video"):
    (tmp_path / "labels").mkdir()
    target = tmp_path / rel_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(payload)
    clip = {
        "clip_id": "c1",
        "position_target": "WR",
        "movement": "release",
        "athlete_id": "ath_1",
        "surface": "turf",
        "lighting": "day",
        "camera_side": {"path": rel_path, "present": True},
    }
    (tmp_path / "manifest.json").write_text(
        json.dumps({"clips": [clip], "labeling_protocol_version": "1.0.0"})
    )
    (tmp_path / "labels" / "ok.json").write_text(
        json.dumps(
            {
                "clip_id": "c1",
                "coach_id": "coach_a",
                "labeling_protocol_version": "1.0.0",
                "events": {name: {"t_ms": 100} for name in EVENTS["release"]},
                "cues": {name: {"value": 1.0, "disputed": False} for name in CUES["release"]},
            }
        )
    )


def test_json_path_is_not_film(tmp_path):
    _seed(tmp_path, "labels/decoy.json")
    clip = json.loads((tmp_path / "manifest.json").read_text())["clips"][0]
    assert gates.has_film(clip, tmp_path) is False
    progress = gates.get_progress(tmp_path)
    assert progress["wr_labeled"] == 0
    assert progress["surfaces"] == 0
    assert progress["wr_athletes"] == 0


def test_mp4_suffix_still_counts(tmp_path):
    _seed(tmp_path, "clips/c1.mp4", b"x")
    progress = gates.get_progress(tmp_path)
    assert progress["wr_labeled"] == 1


def test_mov_suffix_counts_case_insensitive(tmp_path):
    _seed(tmp_path, "clips/c1.MOV", b"x")
    assert gates.has_film(
        json.loads((tmp_path / "manifest.json").read_text())["clips"][0], tmp_path
    ) is True
