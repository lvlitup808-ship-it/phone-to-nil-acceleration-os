"""Honesty pin: C0/DEL control-character only mdat or moov payload is not camera film.

NUL and whitespace are already rejected. Other controls (BEL, BS, DEL, ...) are still padding, not samples or a movie. Gate stays closed. No NIL numbers.
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


def test_control_payload_media_does_not_count(tmp_path):
    for extra in (
        b"\x00\x00\x00\x09mdat" + b"\x07",          # BEL
        b"\x00\x00\x00\x0cmdat" + b"\x01\x02\x03\x04",
        b"\x00\x00\x00\x09moov" + b"\x7f",          # DEL
        b"\x00\x00\x00\x0cmoov" + b"\x1b" * 4,      # ESC
        b"\x00\x00\x00\x0cmdat" + b"\x00\x07\x1f\x7f",
    ):
        _seed(tmp_path, HEADER + extra)
        assert gates.get_progress(tmp_path)["wr_labeled"] == 0, extra


def test_one_printable_still_counts(tmp_path):
    _seed(tmp_path, HEADER + b"\x00\x00\x00\x0amdat" + b"\x07" + b"A")
    assert gates.get_progress(tmp_path)["wr_labeled"] == 1
