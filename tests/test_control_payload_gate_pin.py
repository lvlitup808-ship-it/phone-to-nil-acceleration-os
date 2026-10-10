"""Honesty pin: a media box of only ASCII control characters is not camera film.

has_film already rejects NUL and ASCII whitespace. Other controls (0x01-0x08,
0x0b, 0x0c, 0x0e-0x1f, 0x7f) are the same padding, not samples or a movie.
Gate stays closed.
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


def test_control_only_mdat_or_moov_does_not_count(tmp_path):
    controls = bytes(range(1, 9)) + b"\x0b\x0c" + bytes(range(14, 32)) + b"\x7f"
    for kind in (b"mdat", b"moov"):
        body = HEADER + (8 + len(controls)).to_bytes(4, "big") + kind + controls
        _seed(tmp_path, body)
        assert gates.get_progress(tmp_path)["wr_labeled"] == 0, kind


def test_mixed_control_and_sample_byte_still_counts(tmp_path):
    controls = bytes(range(1, 9)) + b"\x0b\x0c" + bytes(range(14, 32)) + b"\x7f"
    for kind in (b"mdat", b"moov"):
        body = HEADER + (9 + len(controls)).to_bytes(4, "big") + kind + controls + b"x"
        _seed(tmp_path, body)
        assert gates.get_progress(tmp_path)["wr_labeled"] == 1, kind
