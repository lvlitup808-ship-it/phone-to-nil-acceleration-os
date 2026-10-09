"""Honesty pin: a spacer box off a 4-byte boundary is not a phone spacer.

ISO BMFF boxes are 4-byte aligned. free, skip, wide, and uuid may sit between
ftyp and mdat only when their size is a multiple of 4. A short slide must not
land the next header on a forged mdat and raise wr_labeled. Gate stays closed.
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


def test_misaligned_spacer_before_mdat_does_not_count(tmp_path):
    spacers = (
        b"\x00\x00\x00\x09freeZ",
        b"\x00\x00\x00\x0askipZZ",
        b"\x00\x00\x00\x0bwideZZZ",
        b"\x00\x00\x00\x19uuid" + b"0123456789abcdefZ",
    )
    for extra in spacers:
        _seed(tmp_path, HEADER + extra + MDAT)
        assert gates.get_progress(tmp_path)["wr_labeled"] == 0, extra


def test_aligned_spacer_then_mdat_still_counts(tmp_path):
    spacers = (
        b"\x00\x00\x00\x08free",
        b"\x00\x00\x00\x0cfreeZZZZ",
        b"\x00\x00\x00\x08skip",
        b"\x00\x00\x00\x08wide",
        b"\x00\x00\x00\x18uuid" + b"0123456789abcdef",
    )
    for extra in spacers:
        _seed(tmp_path, HEADER + extra + MDAT)
        assert gates.get_progress(tmp_path)["wr_labeled"] == 1, extra
