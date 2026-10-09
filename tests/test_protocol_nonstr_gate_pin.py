"""Honesty pin: a non-string protocol does not disable the stamp check.

When the manifest declares labeling_protocol_version, only a matching string
stamp counts. A number, bool, or blank string is not a protocol. Those labels
must not open the golden-set gate.
"""

from __future__ import annotations

import json

from services.api import gates
from services.golden_set.labels import CUES, EVENTS


def _seed(tmp_path, protocol):
    (tmp_path / "labels").mkdir()
    (tmp_path / "clips").mkdir()
    (tmp_path / "clips" / "c1.mp4").write_bytes(b"\x00\x00\x00\x18ftypisom" + b"x")
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
        json.dumps({"clips": [clip], "labeling_protocol_version": protocol})
    )
    label = {
        "clip_id": "c1",
        "coach_id": "coach_a",
        "labeling_protocol_version": "1.0.0",
        "events": {name: {"t_ms": 100} for name in EVENTS["release"]},
        "cues": {name: {"value": 1.0, "disputed": False} for name in CUES["release"]},
    }
    (tmp_path / "labels" / "c1.json").write_text(json.dumps(label))


def test_numeric_protocol_does_not_count(tmp_path):
    _seed(tmp_path, 1)
    progress = gates.get_progress(tmp_path)
    assert progress["wr_labeled"] == 0
    assert progress["inter_rater_clips"] == 0


def test_bool_protocol_does_not_count(tmp_path):
    _seed(tmp_path, True)
    progress = gates.get_progress(tmp_path)
    assert progress["wr_labeled"] == 0


def test_blank_protocol_does_not_count(tmp_path):
    _seed(tmp_path, "   ")
    progress = gates.get_progress(tmp_path)
    assert progress["wr_labeled"] == 0
