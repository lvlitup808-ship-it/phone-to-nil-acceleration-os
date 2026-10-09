"""Honesty pin: an empty mdat or moov box is not camera film.

has_film treated a later box typed mdat or moov as film even when the box
was only its 8-byte header. A phone file carries sample or movie data in
that box. A size of 0 that ends on the header is the same empty box.
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


def test_empty_mdat_or_moov_does_not_count(tmp_path):
    for extra in (b"\x00\x00\x00\x08mdat", b"\x00\x00\x00\x08moov"):
        _seed(tmp_path, HEADER + extra)
        assert gates.get_progress(tmp_path)["wr_labeled"] == 0, extra


def test_size_zero_header_only_media_box_does_not_count(tmp_path):
    # size 0 means "to end of file"; the file ends on the 8-byte header.
    _seed(tmp_path, HEADER + b"\x00\x00\x00\x00mdat")
    assert gates.get_progress(tmp_path)["wr_labeled"] == 0


def test_media_box_with_one_payload_byte_still_counts(tmp_path):
    for extra in (b"\x00\x00\x00\x09mdatx", b"\x00\x00\x00\x09moovx"):
        _seed(tmp_path, HEADER + extra)
        assert gates.get_progress(tmp_path)["wr_labeled"] == 1, extra


def test_size_zero_media_box_with_payload_still_counts(tmp_path):
    _seed(tmp_path, HEADER + b"\x00\x00\x00\x00mdatx")
    assert gates.get_progress(tmp_path)["wr_labeled"] == 1


def test_empty_free_then_payload_mdat_still_counts(tmp_path):
    extra = b"\x00\x00\x00\x08free" + b"\x00\x00\x00\x09mdatx"
    _seed(tmp_path, HEADER + extra)
    assert gates.get_progress(tmp_path)["wr_labeled"] == 1
