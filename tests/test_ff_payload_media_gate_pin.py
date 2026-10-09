"""Honesty pin: an all-0xFF mdat or moov payload is not camera film.

NUL and ASCII whitespace were already rejected. 0xFF padding is the same stub.
Gate stays closed. No NIL numbers.
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


def test_ff_payload_media_does_not_count(tmp_path):
    for extra in (
        b"\x00\x00\x00\x09mdat" + b"\xff",
        b"\x00\x00\x00\x10mdat" + b"\xff" * 8,
        b"\x00\x00\x00\x09moov" + b"\xff",
        b"\x00\x00\x00\x10moov" + b"\xff" * 8,
    ):
        _seed(tmp_path, HEADER + extra)
        assert gates.get_progress(tmp_path)["wr_labeled"] == 0, extra


def test_sample_byte_still_counts(tmp_path):
    _seed(tmp_path, HEADER + b"\x00\x00\x00\x09mdatx")
    assert gates.get_progress(tmp_path)["wr_labeled"] == 1
