"""Honesty pin: VT, FF, and file-separator payloads are not camera film.

NUL, space, tab, CR, and LF already fail. Other ASCII controls in the
whitespace class (\\x0b, \\x0c, \\x1c-\\x1f) are the same padding, not
samples or a movie box. Gate stays closed. No NIL numbers.
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


def test_control_whitespace_payload_does_not_count(tmp_path):
    for extra in (
        b"\x00\x00\x00\x09mdat\x0b",
        b"\x00\x00\x00\x09mdat\x0c",
        b"\x00\x00\x00\x0cmdat" + bytes([0x0B, 0x0C, 0x1C, 0x1D]),
        b"\x00\x00\x00\x09moov\x0b",
        b"\x00\x00\x00\x0cmoov" + bytes([0x1E, 0x1F, 0x0B, 0x0C]),
    ):
        _seed(tmp_path, HEADER + extra)
        assert gates.get_progress(tmp_path)["wr_labeled"] == 0, extra


def test_noncontrol_mdat_payload_still_counts(tmp_path):
    _seed(tmp_path, HEADER + b"\x00\x00\x00\x09mdatx")
    assert gates.get_progress(tmp_path)["wr_labeled"] == 1
