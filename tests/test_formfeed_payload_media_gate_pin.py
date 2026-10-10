"""Honesty pin: form-feed or vertical-tab only mdat or moov payload is not camera film.

ASCII whitespace includes \\x0b and \\x0c. A payload of only those is padding, not samples or a movie box. Gate stays closed. No NIL numbers.
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


def test_formfeed_or_vtab_payload_media_does_not_count(tmp_path):
    for extra in (
        b"\x00\x00\x00\x09mdat" + b"\x0c",
        b"\x00\x00\x00\x0cmdat" + b"\x0b\x0c\x0b\x0c",
        b"\x00\x00\x00\x09moov" + b"\x0b",
        b"\x00\x00\x00\x0cmoov" + b"\x0c" * 4,
        b"\x00\x00\x00\x0cmdat" + b"\x00\x0b \x0c",
    ):
        _seed(tmp_path, HEADER + extra)
        assert gates.get_progress(tmp_path)["wr_labeled"] == 0, extra


def test_one_non_whitespace_still_counts(tmp_path):
    _seed(tmp_path, HEADER + b"\x00\x00\x00\x0amdat" + b"\x0c" + b"x")
    assert gates.get_progress(tmp_path)["wr_labeled"] == 1
