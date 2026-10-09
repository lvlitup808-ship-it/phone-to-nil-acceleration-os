"""Honesty pin: a near-miss major brand is not camera film.

has_film counts clips/*.mp4 only when the ftyp major brand is one of
isom, iso2, mp41, mp42, avc1, mp71. iso3, mp43, avc3, mp4a, dash, and
uppercase ISOM/MP42 are not those brands. Gate stays closed.
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


def test_near_miss_brands_do_not_count(tmp_path):
    for brand in (b"iso3", b"mp43", b"avc3", b"mp4a", b"dash", b"ISOM", b"MP42"):
        _seed(tmp_path, b"\x00\x00\x00\x14ftyp" + brand + b"\x00\x00\x00\x00film")
        assert gates.get_progress(tmp_path)["wr_labeled"] == 0, brand


def test_phone_brand_still_counts(tmp_path):
    _seed(tmp_path, b"\x00\x00\x00\x14ftypisom\x00\x00\x00\x00film")
    assert gates.get_progress(tmp_path)["wr_labeled"] == 1
