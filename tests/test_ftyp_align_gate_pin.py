"""Honesty pin: an ftyp box whose size is not 4-byte aligned is not camera film.

has_film counted any clips/*.mp4 whose size field was >= 16 and <= the file,
even when the size was 17, 18, or 19. ISO BMFF brands are 4 bytes. A partial
extra byte is not a box a phone wrote. A size of 20 (one compatible brand)
still counts. Gate stays closed.
"""

from __future__ import annotations

import json

from services.api import gates
from services.golden_set.labels import CUES, EVENTS


def _seed(tmp_path, payload: bytes):
    (tmp_path / "labels").mkdir()
    (tmp_path / "clips").mkdir()
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


def test_ftyp_size_17_does_not_count(tmp_path):
    _seed(tmp_path, b"\x00\x00\x00\x11ftypisom\x00\x00\x00\x00X")
    assert gates.get_progress(tmp_path)["wr_labeled"] == 0


def test_ftyp_size_18_does_not_count(tmp_path):
    _seed(tmp_path, b"\x00\x00\x00\x12ftypisom\x00\x00\x00\x00XY")
    assert gates.get_progress(tmp_path)["wr_labeled"] == 0


def test_ftyp_size_19_does_not_count(tmp_path):
    _seed(tmp_path, b"\x00\x00\x00\x13ftypisom\x00\x00\x00\x00XYZ")
    assert gates.get_progress(tmp_path)["wr_labeled"] == 0


def test_ftyp_size_20_compatible_brand_still_counts(tmp_path):
    _seed(tmp_path, b"\x00\x00\x00\x14ftypisom\x00\x00\x00\x00mp41")
    assert gates.get_progress(tmp_path)["wr_labeled"] == 1
