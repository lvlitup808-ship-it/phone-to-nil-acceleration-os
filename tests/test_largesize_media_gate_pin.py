"""Honesty pin: a size-1 media box is not camera film.

ISO BMFF size 1 means a 64-bit largesize follows the type. A phone capture
does not use that marker on mdat or moov. A well-formed largesize plus a
payload byte must not raise wr_labeled, and neither must a uuid spacer
whose size field is 1 in front of a real mdat. Gate stays closed.
No NIL numbers.
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
# size 1, type, 64-bit largesize 17 (8 header + 8 largesize + 1 payload), one byte.
LARGESIZE_MDAT = b"\x00\x00\x00\x01mdat" + (17).to_bytes(8, "big") + b"x"
LARGESIZE_MOOV = b"\x00\x00\x00\x01moov" + (17).to_bytes(8, "big") + b"x"
MDAT = b"\x00\x00\x00\x09mdatx"


def test_largesize_media_box_does_not_count(tmp_path):
    for extra in (LARGESIZE_MDAT, LARGESIZE_MOOV):
        _seed(tmp_path, HEADER + extra)
        assert gates.get_progress(tmp_path)["wr_labeled"] == 0, extra


def test_largesize_uuid_then_mdat_does_not_count(tmp_path):
    # size 1 uuid must not be skipped as an 8-byte spacer before a real mdat.
    extra = b"\x00\x00\x00\x01uuid" + MDAT
    _seed(tmp_path, HEADER + extra)
    assert gates.get_progress(tmp_path)["wr_labeled"] == 0


def test_eight_byte_header_plus_payload_still_counts(tmp_path):
    _seed(tmp_path, HEADER + MDAT)
    assert gates.get_progress(tmp_path)["wr_labeled"] == 1
