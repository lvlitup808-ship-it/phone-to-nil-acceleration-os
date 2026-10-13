"""Honesty pin: a high-bit-only mdat or moov payload is not camera film.

Bytes >= 0x80 sit outside the printable sample range (0x21-0x7E). has_film must
reject a payload of only those bytes so a high-bit stub cannot open the
golden-set gate. One byte in 0x21-0x7E still counts even beside high bits.
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


def test_highbit_only_payload_does_not_count(tmp_path):
    for kind in (b"mdat", b"moov"):
        extra = b"\x00\x00\x00\x0c" + kind + b"\x80\xff\x80\xff"
        _seed(tmp_path, HEADER + extra)
        assert gates.get_progress(tmp_path)["wr_labeled"] == 0, kind


def test_one_printable_with_highbit_still_counts(tmp_path):
    # 0x41 ('A') is inside the sample range. High bits beside it do not hide it.
    extra = b"\x00\x00\x00\x0cmdat" + b"\x80" + b"A" + b"\xff"
    _seed(tmp_path, HEADER + extra)
    assert gates.get_progress(tmp_path)["wr_labeled"] == 1
