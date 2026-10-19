"""Honesty pin: an mdat/moov payload of only a UTF-8 BOM is not camera film.

EF BB BF are high-bit bytes with no printable ASCII (0x21-0x7E). They are a
text marker, not sample data. Gate must stay closed. No NIL numbers.
"""

from __future__ import annotations

import json

from services.api import gates
from services.golden_set.labels import CUES, EVENTS


def _seed(tmp_path, payload: bytes):
    (tmp_path / "labels").mkdir()
    (tmp_path / "clips").mkdir()
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


def test_bom_only_payload_is_not_film(tmp_path):
    # Minimal valid ftyp + mdat whose payload is only the UTF-8 BOM.
    ftyp = b"\x00\x00\x00\x10ftypisom\x00\x00\x00\x00"
    mdat_payload = b"\xEF\xBB\xBF"
    size = 8 + len(mdat_payload)
    mdat = size.to_bytes(4, "big") + b"mdat" + mdat_payload
    _seed(tmp_path, ftyp + mdat)
    clip = json.loads((tmp_path / "manifest.json").read_text())["clips"][0]
    assert gates.has_film(clip, tmp_path) is False
    progress = gates.get_progress(tmp_path)
    assert progress["wr_labeled"] == 0


def test_bom_plus_printable_still_counts(tmp_path):
    ftyp = b"\x00\x00\x00\x10ftypisom\x00\x00\x00\x00"
    mdat_payload = b"\xEF\xBB\xBFsample"
    size = 8 + len(mdat_payload)
    mdat = size.to_bytes(4, "big") + b"mdat" + mdat_payload
    _seed(tmp_path, ftyp + mdat)
    progress = gates.get_progress(tmp_path)
    assert progress["wr_labeled"] == 1
