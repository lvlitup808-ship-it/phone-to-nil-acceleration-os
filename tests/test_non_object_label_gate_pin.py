"""Honesty pin: a non-object labels file must not crash or open the gate.

GET /gates/golden walks every labels/*.json. A hand-written file that is an
array, a string, or a number has no clip_id. It must be skipped, not raise,
and a complete sibling label must still count.
"""

from __future__ import annotations

import json

from services.api import gates
from services.golden_set.labels import CUES, EVENTS


def _clip(tmp_path):
    (tmp_path / "labels").mkdir()
    (tmp_path / "clips").mkdir()
    (tmp_path / "clips" / "c1.mp4").write_bytes(b"\x00\x00\x00\x10ftypisom\x00\x00\x00\x00\x00\x00\x00\x09mdatx")
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


def _complete():
    return {
        "clip_id": "c1",
        "coach_id": "coach_a",
        "events": {name: {"t_ms": 100} for name in EVENTS["release"]},
        "cues": {name: {"value": 1.0, "disputed": False} for name in CUES["release"]},
    }


def test_non_object_label_does_not_raise_or_count(tmp_path):
    _clip(tmp_path)
    (tmp_path / "labels" / "array.json").write_text(json.dumps(["c1", "coach_a"]))
    progress = gates.get_progress(tmp_path)
    assert progress["wr_labeled"] == 0
    assert progress["inter_rater_clips"] == 0


def test_scalar_label_does_not_raise(tmp_path):
    _clip(tmp_path)
    (tmp_path / "labels" / "scalar.json").write_text(json.dumps("c1"))
    progress = gates.get_progress(tmp_path)
    assert progress["wr_labeled"] == 0


def test_junk_label_does_not_hide_a_complete_sibling(tmp_path):
    _clip(tmp_path)
    (tmp_path / "labels" / "array.json").write_text(json.dumps([{"clip_id": "c1"}]))
    (tmp_path / "labels" / "full.json").write_text(json.dumps(_complete()))
    progress = gates.get_progress(tmp_path)
    assert progress["wr_labeled"] == 1
