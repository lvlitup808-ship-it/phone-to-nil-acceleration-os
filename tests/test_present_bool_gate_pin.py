"""Honesty pin: present must be boolean true before a file counts as film.

has_film used to treat any truthy present as film. A hand-edited manifest can
set present to 1 or "true" and, with a file on disk, inflate wr_labeled.
Only JSON true counts.
"""

from __future__ import annotations

import json

from services.api import gates
from services.golden_set.labels import CUES, EVENTS


def _seed(tmp_path, present):
    (tmp_path / "labels").mkdir()
    (tmp_path / "clips").mkdir()
    (tmp_path / "clips" / "c1.mp4").write_bytes(b"\x00\x00\x00\x10ftypisom\x00\x00\x00\x00x")
    clip = {
        "clip_id": "c1",
        "position_target": "WR",
        "movement": "release",
        "athlete_id": "ath_1",
        "surface": "turf",
        "lighting": "day",
        "camera_side": {"path": "clips/c1.mp4", "present": present},
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


def test_present_integer_does_not_count(tmp_path):
    _seed(tmp_path, 1)
    clip = json.loads((tmp_path / "manifest.json").read_text())["clips"][0]
    assert gates.has_film(clip, tmp_path) is False
    progress = gates.get_progress(tmp_path)
    assert progress["wr_labeled"] == 0
    assert progress["surfaces"] == 0


def test_present_string_does_not_count(tmp_path):
    _seed(tmp_path, "true")
    progress = gates.get_progress(tmp_path)
    assert progress["wr_labeled"] == 0


def test_present_boolean_true_still_counts(tmp_path):
    _seed(tmp_path, True)
    progress = gates.get_progress(tmp_path)
    assert progress["wr_labeled"] == 1
