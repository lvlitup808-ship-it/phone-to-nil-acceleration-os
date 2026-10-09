"""Honesty pin: an empty mdat or moov box is not camera film.

has_film accepted clips/*.mp4 when an 8-byte mdat or moov followed ftyp.
That box has a type and no payload. A phone file carries media bytes after
the box header. Gate stays closed.
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


def test_empty_mdat_or_moov_does_not_count(tmp_path):
    header = b"\x00\x00\x00\x10ftypisom\x00\x00\x00\x00"
    for extra in (b"\x00\x00\x00\x08mdat", b"\x00\x00\x00\x08moov"):
        _seed(tmp_path, header + extra)
        assert gates.get_progress(tmp_path)["wr_labeled"] == 0, extra


def test_size_zero_mdat_with_no_payload_does_not_count(tmp_path):
    # size 0 means "to EOF". Eight bytes left is still an empty box.
    header = b"\x00\x00\x00\x10ftypisom\x00\x00\x00\x00"
    _seed(tmp_path, header + b"\x00\x00\x00\x00mdat")
    assert gates.get_progress(tmp_path)["wr_labeled"] == 0


def test_mdat_with_payload_still_counts(tmp_path):
    header = b"\x00\x00\x00\x10ftypisom\x00\x00\x00\x00"
    extra = b"\x00\x00\x00\x09mdat" + b"\x00"
    _seed(tmp_path, header + extra)
    assert gates.get_progress(tmp_path)["wr_labeled"] == 1
