"""Honesty pin: blank or padded coach ids do not inflate the gate.

Inter-rater is two distinct coaches on the same filmed clip. Whitespace-only
ids are not coaches, and padding must not split one coach into two.
"""

from __future__ import annotations

import json

from services.api import gates
from services.golden_set.labels import CUES, EVENTS


def test_whitespace_coach_id_does_not_inflate_inter_rater(tmp_path):
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
        "camera_side": {"path": "clips/c1.mp4", "present": True},
    }
    (tmp_path / "manifest.json").write_text(json.dumps({"clips": [clip]}))
    complete = {
        "events": {name: {"t_ms": 100} for name in EVENTS["release"]},
        "cues": {name: {"value": 1.0, "disputed": False} for name in CUES["release"]},
    }
    (tmp_path / "labels" / "blank.json").write_text(
        json.dumps({"clip_id": "c1", "coach_id": "   ", **complete})
    )
    (tmp_path / "labels" / "padded.json").write_text(
        json.dumps({"clip_id": "c1", "coach_id": " coach_a ", **complete})
    )
    (tmp_path / "labels" / "same.json").write_text(
        json.dumps({"clip_id": "c1", "coach_id": "coach_a", **complete})
    )
    progress = gates.get_progress(tmp_path)
    assert progress["wr_labeled"] == 1
    assert progress["inter_rater_clips"] == 0
    assert progress["inter_rater_done"] is False
