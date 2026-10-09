"""Honesty pin: a stub label file does not inflate the golden-set gate.

POST /golden/labels refuses a save that is missing the five events or the six
frozen cues. A hand-written labels/*.json can still skip that. The gate must
ignore it, the same way it ignores excluded labels and fixture clips.
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


def test_stub_label_does_not_count_toward_gate(tmp_path):
    _clip(tmp_path)
    (tmp_path / "labels" / "stub.json").write_text(
        json.dumps({"clip_id": "c1", "coach_id": "coach_a"})
    )
    progress = gates.get_progress(tmp_path)
    assert progress["wr_labeled"] == 0
    assert progress["inter_rater_clips"] == 0


def test_complete_label_still_counts(tmp_path):
    _clip(tmp_path)
    (tmp_path / "labels" / "full.json").write_text(
        json.dumps(
            {
                "clip_id": "c1",
                "coach_id": "coach_a",
                "events": {name: {"t_ms": 100} for name in EVENTS["release"]},
                "cues": {name: {"value": 1.0, "disputed": False} for name in CUES["release"]},
            }
        )
    )
    progress = gates.get_progress(tmp_path)
    assert progress["wr_labeled"] == 1
