"""Honesty pin: event and cue shells do not count as coach labels.

POST /golden/labels refuses a cue with no value unless it is disputed, and
requires each event to carry t_ms. A hand-written labels/*.json can still
list the right keys with empty shells. The gate must ignore those shells.
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


def test_empty_event_and_cue_shells_do_not_count(tmp_path):
    _clip(tmp_path)
    (tmp_path / "labels" / "shell.json").write_text(
        json.dumps(
            {
                "clip_id": "c1",
                "coach_id": "coach_a",
                "events": {name: {} for name in EVENTS["release"]},
                "cues": {name: {} for name in CUES["release"]},
            }
        )
    )
    progress = gates.get_progress(tmp_path)
    assert progress["wr_labeled"] == 0
    assert progress["inter_rater_clips"] == 0


def test_null_cue_without_dispute_does_not_count(tmp_path):
    _clip(tmp_path)
    (tmp_path / "labels" / "guess.json").write_text(
        json.dumps(
            {
                "clip_id": "c1",
                "coach_id": "coach_a",
                "events": {name: {"t_ms": 100} for name in EVENTS["release"]},
                "cues": {name: {"value": None, "disputed": False} for name in CUES["release"]},
            }
        )
    )
    progress = gates.get_progress(tmp_path)
    assert progress["wr_labeled"] == 0


def test_disputed_null_cue_still_counts(tmp_path):
    _clip(tmp_path)
    (tmp_path / "labels" / "unsure.json").write_text(
        json.dumps(
            {
                "clip_id": "c1",
                "coach_id": "coach_a",
                "events": {name: {"t_ms": 100} for name in EVENTS["release"]},
                "cues": {name: {"value": None, "disputed": True} for name in CUES["release"]},
            }
        )
    )
    progress = gates.get_progress(tmp_path)
    assert progress["wr_labeled"] == 1
