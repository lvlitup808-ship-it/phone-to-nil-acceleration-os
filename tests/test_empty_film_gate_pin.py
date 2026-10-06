"""Honesty pin: a zero-byte camera file is not film.

has_film treated any on-disk file as film once present was JSON true.
A hand-edited manifest can point at an empty placeholder and inflate
wr_labeled. Empty files do not count. A non-empty file still does.
"""

from __future__ import annotations

import json

from services.api import gates
from services.golden_set.labels import CUES, EVENTS


def _seed(tmp_path, payload: bytes):
    (tmp_path / "labels").mkdir()
    (tmp_path / "clips").mkdir()
    (tmp_path / "clips" / "c1.mp4").write_bytes(payload)
    clip = {
        "clip_id": "c1",
        "position_target": "WR",
        "movement": "release",
        "athlete_id": "ath_1",
        "surface": "turf",
        "lighting": "day",
        "camera_side": {"path": "clips/c1.mp4", "present": True},
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


def test_empty_file_is_not_film(tmp_path):
    _seed(tmp_path, b"")
    clip = json.loads((tmp_path / "manifest.json").read_text())["clips"][0]
    assert gates.has_film(clip, tmp_path) is False
    progress = gates.get_progress(tmp_path)
    assert progress["wr_labeled"] == 0
    assert progress["surfaces"] == 0
    assert progress["wr_athletes"] == 0


def test_nonzero_file_still_counts(tmp_path):
    _seed(tmp_path, b"x")
    progress = gates.get_progress(tmp_path)
    assert progress["wr_labeled"] == 1
