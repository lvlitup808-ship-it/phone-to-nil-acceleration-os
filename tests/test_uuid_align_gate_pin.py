"""Honesty pin: a spacer box off a 4-byte boundary is not a phone spacer.

ISO BMFF box sizes are 4-byte claims. A uuid, free, skip, or wide whose size
is not a multiple of 4 is a partial box, not padding a phone wrote. It must
not raise wr_labeled even when an mdat follows. Gate stays closed.
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
    cases = (
        b"\x00\x00\x00\x19uuid" + b"0123456789abcdef" + b"Z",
        b"\x00\x00\x00\x09freex",
        b"\x00\x00\x00\x09skipx",
        b"\x00\x00\x00\x09widex",
    )
    for extra in cases:
        _seed(tmp_path, HEADER + extra + MDAT)
        assert gates.get_progress(tmp_path)["wr_labeled"] == 0, extra


def test_aligned_spacer_then_mdat_still_counts(tmp_path):
    extra = b"\x00\x00\x00\x18uuid" + b"0123456789abcdef"
    _seed(tmp_path, HEADER + extra + MDAT)
    assert gates.get_progress(tmp_path)["wr_labeled"] == 1
    _seed(tmp_path, HEADER + b"\x00\x00\x00\x08free" + MDAT)
    assert gates.get_progress(tmp_path)["wr_labeled"] == 1
