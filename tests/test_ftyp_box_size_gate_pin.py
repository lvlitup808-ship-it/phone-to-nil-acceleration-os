"""Honesty pin: an ftyp box whose size field is under 16 is not camera film.

has_film counted any clips/*.mp4 with bytes 4:8 equal to ftyp and an
alphanumeric brand at 8:12, even when the size field was 8 (brand outside
the box), 0 (to EOF), or 1 (largesize). A phone file declares a box size
of at least 16. Gate stays closed.
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


def test_ftyp_size_under_16_with_trailing_brand_does_not_count(tmp_path):
    # Size field says 8. Extra bytes make the file look branded, but the brand
    # sits outside the declared box.
    _seed(tmp_path, b"\x00\x00\x00\x08ftypisom\x00\x00\x00\x00")
    assert gates.get_progress(tmp_path)["wr_labeled"] == 0


def test_ftyp_size_zero_to_eof_does_not_count(tmp_path):
    _seed(tmp_path, b"\x00\x00\x00\x00ftypisom\x00\x00\x00\x00")
    assert gates.get_progress(tmp_path)["wr_labeled"] == 0


def test_ftyp_largesize_marker_does_not_count(tmp_path):
    _seed(tmp_path, b"\x00\x00\x00\x01ftypisom\x00\x00\x00\x00")
    assert gates.get_progress(tmp_path)["wr_labeled"] == 0


def test_bounded_ftyp_box_still_counts(tmp_path):
    _seed(tmp_path, b"\x00\x00\x00\x18ftypisom\x00\x00\x00\x00film")
    assert gates.get_progress(tmp_path)["wr_labeled"] == 1
