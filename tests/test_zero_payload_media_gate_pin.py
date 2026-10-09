"""Honesty pin: a zero-filled mdat or moov payload is not camera film.

has_film counted a later mdat or moov once the box was longer than its 8-byte
header. A payload of only NUL bytes is a placeholder, same family as an empty
header. One non-zero payload byte still counts. Gate stays closed.
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


def test_zero_payload_media_box_does_not_count(tmp_path):
    for extra in (
        b"\x00\x00\x00\x09mdat\x00",
        b"\x00\x00\x00\x09moov\x00",
        b"\x00\x00\x00\x10mdat\x00\x00\x00\x00\x00\x00\x00\x00",
        b"\x00\x00\x00\x00mdat\x00\x00",
    ):
        _seed(tmp_path, HEADER + extra)
        assert gates.get_progress(tmp_path)["wr_labeled"] == 0, extra


def test_nonzero_payload_byte_still_counts(tmp_path):
    for extra in (
        b"\x00\x00\x00\x09mdat\x01",
        b"\x00\x00\x00\x09moovx",
        b"\x00\x00\x00\x00mdat\x00x",
        b"\x00\x00\x00\x08free" + b"\x00\x00\x00\x0amdat\x00\x01",
    ):
        _seed(tmp_path, HEADER + extra)
        assert gates.get_progress(tmp_path)["wr_labeled"] == 1, extra
