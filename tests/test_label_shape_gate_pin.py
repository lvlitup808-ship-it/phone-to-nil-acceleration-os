"""Honesty pin: key-shaped stubs are not coach labels.

POST /golden/labels requires each event to carry t_ms >= 0 and each cue to
carry a number or an explicit disputed flag. A hand-written labels/*.json can
still list the right keys with empty objects. Those must not count toward the
golden-set gate.
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


def _write(tmp_path, label):
    (tmp_path / "labels" / "shaped.json").write_text(json.dumps(label))


def test_empty_event_objects_do_not_count(tmp_path):
    _clip(tmp_path)
    _write(
        tmp_path,
        {
            "clip_id": "c1",
            "coach_id": "coach_a",
            "events": {name: {} for name in EVENTS["release"]},
            "cues": {name: {"value": 1.0, "disputed": False} for name in CUES["release"]},
        },
    )
    progress = gates.get_progress(tmp_path)
    assert progress["wr_labeled"] == 0


def test_cue_without_value_or_dispute_does_not_count(tmp_path):
    _clip(tmp_path)
    _write(
        tmp_path,
        {
            "clip_id": "c1",
            "coach_id": "coach_a",
            "events": {name: {"t_ms": 100} for name in EVENTS["release"]},
            "cues": {name: {} for name in CUES["release"]},
        },
    )
    progress = gates.get_progress(tmp_path)
    assert progress["wr_labeled"] == 0


def test_integer_timestamps_and_valued_cues_still_count(tmp_path):
    _clip(tmp_path)
    _write(
        tmp_path,
        {
            "clip_id": "c1",
            "coach_id": "coach_a",
            "events": {name: {"t_ms": 100} for name in EVENTS["release"]},
            "cues": {name: {"value": 1.0, "disputed": False} for name in CUES["release"]},
        },
    )
    progress = gates.get_progress(tmp_path)
    assert progress["wr_labeled"] == 1
