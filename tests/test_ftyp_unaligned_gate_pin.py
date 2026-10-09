"""Honesty pin: an ftyp box whose size is not a multiple of 4 is not camera film.

has_film counted clips/*.mp4 when bytes 4:8 were ftyp, the brand was
alphanumeric, and the size field fit the file, even if that size was 18.
ISO BMFF boxes are 4-byte aligned. A phone file does not write an odd box.
Gate stays closed.
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


def test_ftyp_box_size_18_does_not_count(tmp_path):
    # Size 18 holds the brand and two extra bytes, but it is not 4-aligned.
    _seed(tmp_path, b"\x00\x00\x00\x12ftypisom\x00\x00\x00\x00xx")
    assert gates.get_progress(tmp_path)["wr_labeled"] == 0


def test_ftyp_box_size_17_does_not_count(tmp_path):
    _seed(tmp_path, b"\x00\x00\x00\x11ftypisom\x00\x00\x00\x00x")
    assert gates.get_progress(tmp_path)["wr_labeled"] == 0


def test_aligned_ftyp_box_still_counts(tmp_path):
    _seed(tmp_path, b"\x00\x00\x00\x14ftypisom\x00\x00\x00\x00film")
    assert gates.get_progress(tmp_path)["wr_labeled"] == 1
