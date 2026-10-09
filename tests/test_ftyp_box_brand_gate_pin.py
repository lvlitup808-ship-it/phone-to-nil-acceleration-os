"""Honesty pin: a box-type name is not an ftyp major brand.

has_film accepted clips/*.mp4 when bytes 4:8 were ftyp and the next four
bytes were alphanumeric, including mdat, moov, free, skip, and wide. Those
are box types, not brands a phone file writes. Gate stays closed.
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


def test_ftyp_brand_mdat_does_not_count(tmp_path):
    _seed(tmp_path, b"\x00\x00\x00\x14ftypmdat\x00\x00\x00\x00film")
    assert gates.get_progress(tmp_path)["wr_labeled"] == 0


def test_ftyp_brand_moov_free_skip_wide_do_not_count(tmp_path):
    for brand in (b"moov", b"free", b"skip", b"wide", b"ftyp"):
        _seed(tmp_path, b"\x00\x00\x00\x14ftyp" + brand + b"\x00\x00\x00\x00film")
        assert gates.get_progress(tmp_path)["wr_labeled"] == 0, brand


def test_ftyp_brand_isom_still_counts(tmp_path):
    _seed(tmp_path, b"\x00\x00\x00\x14ftypisom\x00\x00\x00\x00film\x00\x00\x00\x08mdat")
    assert gates.get_progress(tmp_path)["wr_labeled"] == 1
