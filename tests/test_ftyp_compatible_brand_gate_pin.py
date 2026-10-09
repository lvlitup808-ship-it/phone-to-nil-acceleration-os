"""Honesty pin: a non-phone compatible brand is not camera film.

has_film accepted clips/*.mp4 when the major brand was isom and the next
four bytes after the minor version were film, test, or note. Those are not
compatible brands a phone file writes. Gate stays closed.
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


def test_compatible_brand_film_test_note_do_not_count(tmp_path):
    for brand in (b"film", b"test", b"note", b"mdat", b"xxxx"):
        _seed(tmp_path, b"\x00\x00\x00\x14ftypisom\x00\x00\x00\x00" + brand)
        assert gates.get_progress(tmp_path)["wr_labeled"] == 0, brand


def test_phone_compatible_brand_still_counts(tmp_path):
    for brand in (b"isom", b"iso2", b"mp41", b"mp42", b"avc1", b"mp71"):
        _seed(tmp_path, b"\x00\x00\x00\x14ftypisom\x00\x00\x00\x00" + brand)
        assert gates.get_progress(tmp_path)["wr_labeled"] == 1, brand
