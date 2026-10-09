"""Honesty pin: event keys without timestamps do not open the golden-set gate.

POST /golden/labels requires each event to carry t_ms. A hand-written
labels/*.json can list the five event names as empty objects. The gate must
not count that as a coach label.
"""

from __future__ import annotations

import json

from services.api import gates
from services.golden_set.labels import CUES, EVENTS


def _clip(tmp_path):
    (tmp_path / "labels").mkdir()
    (tmp_path / "clips").mkdir()
    (tmp_path / "clips" / "c1.mp4").write_bytes(b"\x00\x00\x00\x18ftypisom\x00\x00\x00\x00x")
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


def test_events_without_timestamps_do_not_count(tmp_path):
    _clip(tmp_path)
    (tmp_path / "labels" / "empty_events.json").write_text(
        json.dumps(
            {
                "clip_id": "c1",
                "coach_id": "coach_a",
                "events": {name: {} for name in EVENTS["release"]},
                "cues": {name: {"value": 1.0, "disputed": False} for name in CUES["release"]},
            }
        )
    )
    progress = gates.get_progress(tmp_path)
    assert progress["wr_labeled"] == 0
    assert progress["inter_rater_clips"] == 0


def test_cues_without_value_or_dispute_do_not_count(tmp_path):
    _clip(tmp_path)
    (tmp_path / "labels" / "empty_cues.json").write_text(
        json.dumps(
            {
                "clip_id": "c1",
                "coach_id": "coach_a",
                "events": {name: {"t_ms": 100} for name in EVENTS["release"]},
                "cues": {name: {} for name in CUES["release"]},
            }
        )
    )
    progress = gates.get_progress(tmp_path)
    assert progress["wr_labeled"] == 0
