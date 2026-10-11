"""Honesty pin: a stub mdat or moov before a real media box is not camera film.

An 8-byte media header, or a media box whose payload has no printable sample
bytes, is padding. The gate must reject the file even when a later mdat or
moov carries real samples. Gate stays closed. No NIL numbers.
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
        "cues": {name: {"value": 1.0, "disputed": False} for name in CUES["release"]},
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


HEADER = b"\x00\x00\x00\x10ftypisom\x00\x00\x00\x00"


def test_stub_media_before_real_does_not_count(tmp_path):
    good_payload = b"sample"
    good = (8 + len(good_payload)).to_bytes(4, "big") + b"mdat" + good_payload
    for stub in (
        (8).to_bytes(4, "big") + b"mdat",  # empty header only
        (8).to_bytes(4, "big") + b"moov",
        (9).to_bytes(4, "big") + b"mdat" + b"\x00",  # NUL payload
        (12).to_bytes(4, "big") + b"mdat" + b"\x80\xFF\xA0\xC0",  # high-bit only
    ):
        _seed(tmp_path, HEADER + stub + good)
        assert gates.get_progress(tmp_path)["wr_labeled"] == 0, stub


def test_real_media_alone_still_counts(tmp_path):
    good_payload = b"sample"
    good = (8 + len(good_payload)).to_bytes(4, "big") + b"mdat" + good_payload
    _seed(tmp_path, HEADER + good)
    assert gates.get_progress(tmp_path)["wr_labeled"] == 1
