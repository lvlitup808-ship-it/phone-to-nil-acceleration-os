"""Honesty pin: a size-1 spacer is not an 8-byte phone box before mdat.

ISO BMFF size 1 means a 64-bit largesize follows the type. has_film must not
treat that marker as a short free/skip/wide and then count the next box as
mdat. Gate stays closed. No NIL numbers.
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
MDAT = b"\x00\x00\x00\x09mdatx"


def test_largesize_spacer_before_mdat_does_not_count(tmp_path):
    for extra in (
        b"\x00\x00\x00\x01free" + MDAT,
        b"\x00\x00\x00\x01skip" + MDAT,
        b"\x00\x00\x00\x01wide" + MDAT,
    ):
        _seed(tmp_path, HEADER + extra)
        assert gates.get_progress(tmp_path)["wr_labeled"] == 0, extra


def test_eight_byte_free_then_mdat_still_counts(tmp_path):
    _seed(tmp_path, HEADER + b"\x00\x00\x00\x08free" + MDAT)
    assert gates.get_progress(tmp_path)["wr_labeled"] == 1
