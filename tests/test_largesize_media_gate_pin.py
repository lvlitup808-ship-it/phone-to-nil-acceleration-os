"""Honesty pin: an mdat or moov whose size field is 1 is not camera film.

ISO BMFF size 1 is a 64-bit largesize marker, not an 8-byte box. A phone
capture does not use it on a media box. Gate must stay closed. No NIL numbers.
"""

from __future__ import annotations

import json

from services.api import gates
from services.golden_set.labels import CUES, EVENTS


def _seed(tmp_path, payload: bytes):
    (tmp_path / "labels").mkdir(exist_ok=True)
    (tmp_path / "clips").mkdir(exist_ok=True)
    (tmp_path / "clips" / "c1.mp4").write_bytes(payload)
    clip = {
        "clip_id": "c1",
        "position_target": "WR",
        "movement": "release",
        "athlete_id": "ath_1",
        "surface": "turf",
        "lighting": "day",
        "camera_side": {"path": "clips/c1.mp4", "present": True},
    }
    (tmp_path / "manifest.json").write_text(
        json.dumps({"clips": [clip], "labeling_protocol_version": "1.0.0"})
    )
    (tmp_path / "labels" / "ok.json").write_text(
        json.dumps(
            {
                "clip_id": "c1",
                "coach_id": "coach_a",
                "labeling_protocol_version": "1.0.0",
                "events": {name: {"t_ms": 100} for name in EVENTS["release"]},
                "cues": {name: {"value": 1.0, "disputed": False} for name in CUES["release"]},
            }
        )
    )


def test_largesize_media_box_is_not_film(tmp_path):
    # Minimal valid ftyp + mdat/moov with size field 1 (largesize marker).
    ftyp = b"\x00\x00\x00\x10ftypisom\x00\x00\x00\x00"
    # 8-byte "header" claiming size 1, plus some printable bytes that would
    # look like payload if the size were interpreted as 8.
    for kind in (b"mdat", b"moov"):
        media = b"\x00\x00\x00\x01" + kind + b"sample"
        _seed(tmp_path, ftyp + media)
        clip = json.loads((tmp_path / "manifest.json").read_text())["clips"][0]
        assert gates.has_film(clip, tmp_path) is False, kind
        progress = gates.get_progress(tmp_path)
        assert progress["wr_labeled"] == 0, kind


def test_normal_size_media_still_counts(tmp_path):
    ftyp = b"\x00\x00\x00\x10ftypisom\x00\x00\x00\x00"
    mdat_payload = b"sample"
    size = 8 + len(mdat_payload)
    mdat = size.to_bytes(4, "big") + b"mdat" + mdat_payload
    _seed(tmp_path, ftyp + mdat)
    progress = gates.get_progress(tmp_path)
    assert progress["wr_labeled"] == 1
