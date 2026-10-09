"""Honesty pin: off-position film does not fill the golden-set mix.

docs/film_first.md is a WR + DB gate. A hand-written label on a filmed
RB, OL, or other clip must not raise surfaces, lighting, or athlete
counts, and must not count as WR or DB labeled.
"""

from __future__ import annotations

import json

from services.api import gates
from services.golden_set.labels import CUES, EVENTS


def _label(clip_id: str) -> dict:
    return {
        "clip_id": clip_id,
        "coach_id": "coach_a",
        "events": {name: {"t_ms": 100} for name in EVENTS["release"]},
        "cues": {name: {"value": 1.0, "disputed": False} for name in CUES["release"]},
    }


def test_off_position_film_does_not_fill_mix(tmp_path):
    (tmp_path / "labels").mkdir()
    (tmp_path / "clips").mkdir()
    (tmp_path / "clips" / "rb.mp4").write_bytes(b"\x00\x00\x00\x10ftypisom\x00\x00\x00\x00\x00\x00\x00\x09mdatx")
    clip = {
        "clip_id": "c_rb",
        "position_target": "RB",
        "movement": "release",
        "athlete_id": "ath_rb",
        "surface": "turf",
        "lighting": "day",
        "camera_side": {"path": "clips/rb.mp4", "present": True},
    }
    (tmp_path / "manifest.json").write_text(json.dumps({"clips": [clip]}))
    (tmp_path / "labels" / "rb.json").write_text(json.dumps(_label("c_rb")))
    progress = gates.get_progress(tmp_path)
    assert progress["wr_labeled"] == 0
    assert progress["db_labeled"] == 0
    assert progress["surfaces"] == 0
    assert progress["lighting_conditions"] == 0
    assert progress["wr_athletes"] == 0
    assert progress["db_athletes"] == 0
    assert progress["inter_rater_clips"] == 0
