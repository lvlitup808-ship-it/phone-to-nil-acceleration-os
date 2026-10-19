"""Honesty pin: mixed C0 controls plus one printable sample is camera film.

A payload of only controls is padding. One byte in 0x21-0x7E is a sample.
has_film must count the mixed box so a real capture is not rejected, and
must still reject the pure-control case. Gate stays closed. No NIL numbers.
"""

from __future__ import annotations

import json

from services.api import gates
from services.golden_set.labels import CUES, EVENTS


def _seed(tmp_path, payload: bytes):
    (tmp_path / "labels").mkdir(exist_ok=True)
    (tmp_path / "clips").mkdir(exist_ok=True)
    (tmp_path / "clips" / "c1.mp4").write_bytes(payload)
    label = {
        "clip_id": "c1",
        "coach_id": "coach_a",
        "labeling_protocol_version": "1.0.0",
        "events": {name: {"t_ms": 100} for name in EVENTS["release"]},
        "cues": {name: {"value": 1} for name in CUES["release"]},
    }
    (tmp_path / "labels" / "c1_coach_a.json").write_text(json.dumps(label))
    (tmp_path / "manifest.json").write_text(json.dumps({
        "labeling_protocol_version": "1.0.0",
        "clips": [{
            "clip_id": "c1",
            "position_target": "WR",
            "movement": "release",
            "athlete_id": "ath_1",
            "surface": "turf",
            "lighting": "day",
            "camera_side": {"path": "clips/c1.mp4", "present": True},
        }],
    }))


HEADER = b"\x00\x00\x00\x10ftypisom\x00\x00\x00\x00"


def test_mixed_control_and_printable_counts(tmp_path):
    # NUL, US, space, then '!' (0x21). One printable is enough.
    extra = b"\x00\x00\x00\x0cmdat\x00\x1f !"
    _seed(tmp_path, HEADER + extra)
    assert gates.get_progress(tmp_path)["wr_labeled"] == 1


def test_pure_controls_still_do_not_count(tmp_path):
    extra = b"\x00\x00\x00\x0cmdat\x00\x1f \x09"
    _seed(tmp_path, HEADER + extra)
    assert gates.get_progress(tmp_path)["wr_labeled"] == 0
