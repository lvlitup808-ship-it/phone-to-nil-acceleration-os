"""Honesty pin: an ftyp header with no media box is not camera film.

has_film accepted clips/*.mp4 when bytes 4:8 were ftyp and the major brand
was a phone brand, even if the file ended there. A phone file has an mdat
or moov box after ftyp. Notes after the header are not film. Gate stays closed.
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


def test_ftyp_without_media_box_does_not_count(tmp_path):
    _seed(tmp_path, b"\x00\x00\x00\x10ftypisom\x00\x00\x00\x00film")
    assert gates.get_progress(tmp_path)["wr_labeled"] == 0


def test_ftyp_then_mdat_or_moov_still_counts(tmp_path):
    for extra in (b"\x00\x00\x00\x09mdatx", b"\x00\x00\x00\x09moovx"):
        _seed(tmp_path, b"\x00\x00\x00\x10ftypisom\x00\x00\x00\x00" + extra)
        assert gates.get_progress(tmp_path)["wr_labeled"] == 1, extra


def test_free_then_mdat_still_counts(tmp_path):
    extra = b"\x00\x00\x00\x08free" + b"\x00\x00\x00\x09mdatx"
    _seed(tmp_path, b"\x00\x00\x00\x10ftypisom\x00\x00\x00\x00" + extra)
    assert gates.get_progress(tmp_path)["wr_labeled"] == 1
