"""Honesty pin: an unknown ftyp major brand is not camera film.

has_film counted any clips/*.mp4 whose bytes 4:8 were ftyp and whose bytes
8:12 were four alphanumeric characters. A notes file can spell ftypfilm or
ftypxxxx. A phone file writes a known ISO BMFF major brand (isom, mp42).
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


def test_unknown_ftyp_brand_does_not_count(tmp_path):
    _seed(tmp_path, b"\x00\x00\x00\x10ftypfilm\x00\x00\x00\x00xxxx")
    assert gates.get_progress(tmp_path)["wr_labeled"] == 0


def test_placeholder_ftyp_brand_does_not_count(tmp_path):
    _seed(tmp_path, b"\x00\x00\x00\x10ftypxxxx\x00\x00\x00\x00xxxx")
    assert gates.get_progress(tmp_path)["wr_labeled"] == 0


def test_phone_major_brand_still_counts(tmp_path):
    _seed(tmp_path, b"\x00\x00\x00\x10ftypisom\x00\x00\x00\x00film")
    assert gates.get_progress(tmp_path)["wr_labeled"] == 1


def test_mp42_major_brand_still_counts(tmp_path):
    _seed(tmp_path, b"\x00\x00\x00\x10ftypmp42\x00\x00\x00\x00film")
    assert gates.get_progress(tmp_path)["wr_labeled"] == 1
