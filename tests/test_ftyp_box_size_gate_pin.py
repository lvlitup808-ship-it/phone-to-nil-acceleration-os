"""Honesty pin: an ftyp box that does not cover its brand is not camera film.

has_film used to accept any clips/*.mp4 whose bytes 4:8 were b'ftyp' and whose
bytes 8:12 looked like a brand, even when the box size ended before that brand
or those bytes were a 64-bit largesize. A phone file is an ISO BMFF ftyp box
whose declared size covers the major brand. Gate stays closed.
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
    (tmp_path / "manifest.json").write_text(
        json.dumps(
            {
                "labeling_protocol_version": "1.0.0",
                "clips": [
                    {
                        "clip_id": "c1",
                        "position_target": "WR",
                        "movement": "release",
                        "athlete_id": "ath_1",
                        "surface": "turf",
                        "lighting": "day",
                        "camera_side": {"path": "clips/c1.mp4", "present": True},
                    }
                ],
            }
        )
    )


def test_ftyp_size_shorter_than_brand_does_not_count(tmp_path):
    # size=8 ends at the type field. The brand bytes sit outside the box.
    _seed(tmp_path, b"\x00\x00\x00\x08ftypisom\x00\x00\x00\x00")
    assert gates.get_progress(tmp_path)["wr_labeled"] == 0


def test_ftyp_largesize_without_brand_does_not_count(tmp_path):
    # size=1 means the next 8 bytes are largesize, not a major brand.
    _seed(tmp_path, b"\x00\x00\x00\x01ftypisom\x00\x00\x00\x00")
    assert gates.get_progress(tmp_path)["wr_labeled"] == 0


def test_ftyp_size_covering_brand_still_counts(tmp_path):
    _seed(tmp_path, b"\x00\x00\x00\x18ftypisom\x00\x00\x00\x00film")
    assert gates.get_progress(tmp_path)["wr_labeled"] == 1


def test_ftyp_size_zero_to_eof_still_counts(tmp_path):
    # size=0 means the box extends to EOF, so the brand is inside the box.
    _seed(tmp_path, b"\x00\x00\x00\x00ftypisom\x00\x00\x00\x00")
    assert gates.get_progress(tmp_path)["wr_labeled"] == 1
