"""Honesty pin: a random 4-letter major brand is not camera film.

has_film accepted clips/*.mp4 when bytes 4:8 were ftyp and the next four
bytes were alphanumeric and not a box type. test, fake, note, and xxxx are
not brands a phone file writes. Gate stays closed.
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


def test_ftyp_brand_test_fake_note_do_not_count(tmp_path):
    for brand in (b"test", b"fake", b"note", b"xxxx", b"text"):
        _seed(tmp_path, b"\x00\x00\x00\x10ftyp" + brand + b"\x00\x00\x00\x00film")
        assert gates.get_progress(tmp_path)["wr_labeled"] == 0, brand


def test_phone_brands_still_count(tmp_path):
    for brand in (b"isom", b"iso2", b"mp41", b"mp42", b"avc1", b"mp71"):
        _seed(tmp_path, b"\x00\x00\x00\x10ftyp" + brand + b"\x00\x00\x00\x00" + b"\x00\x00\x00\x09mdat\x00")
        assert gates.get_progress(tmp_path)["wr_labeled"] == 1, brand
