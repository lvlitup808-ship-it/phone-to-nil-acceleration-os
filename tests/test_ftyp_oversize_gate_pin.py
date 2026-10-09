"""Honesty pin: an ftyp box larger than the file is not camera film.

has_film accepted clips/*.mp4 when bytes 4:8 were ftyp, the brand was
alphanumeric, and the size field was >= 16, even if that size was bigger
than the bytes on disk. A phone file cannot declare a box it does not hold.
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


def test_ftyp_box_larger_than_file_does_not_count(tmp_path):
    # Size field says 32. The file is only the 16-byte header plus brand.
    _seed(tmp_path, b"\x00\x00\x00\x20ftypisom\x00\x00\x00\x00")
    assert gates.get_progress(tmp_path)["wr_labeled"] == 0


def test_ftyp_box_size_max_does_not_count(tmp_path):
    # 0xFFFFFFFF is not a box this file holds.
    _seed(tmp_path, b"\xff\xff\xff\xffftypisom" + b"\x00" * 8)
    assert gates.get_progress(tmp_path)["wr_labeled"] == 0


def test_ftyp_box_that_fits_still_counts(tmp_path):
    _seed(tmp_path, b"\x00\x00\x00\x10ftypisom\x00\x00\x00\x00\x00\x00\x00\x09mdat\x00")
    assert gates.get_progress(tmp_path)["wr_labeled"] == 1
