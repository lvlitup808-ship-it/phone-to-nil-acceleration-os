"""Honesty pin: a .mp4 name is not camera film without an MP4 header.

Suffix checks already reject .txt and manifest.json. A notes file renamed
to clips/<id>.mp4 still has present: true and a non-empty size, so the gate
used to count it. ISO BMFF camera files carry an ftyp box in the header.
"""

from __future__ import annotations

import json

from services.api import gates
from services.golden_set.labels import CUES, EVENTS


def _label(clip_id: str) -> dict:
    return {
        "clip_id": clip_id,
        "coach_id": "coach_a",
        "labeling_protocol_version": "1.0.0",
        "events": {name: {"t_ms": 100} for name in EVENTS["release"]},
        "cues": {name: {"value": 1.0, "disputed": False} for name in CUES["release"]},
    }


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
    (tmp_path / "labels" / "c1.json").write_text(json.dumps(_label("c1")))
    return clip


def test_renamed_text_is_not_film(tmp_path):
    clip = _seed(tmp_path, b"coach notes, not a camera file")
    assert gates.has_film(clip, tmp_path) is False
    progress = gates.get_progress(tmp_path)
    assert progress["wr_labeled"] == 0
    assert progress["surfaces"] == 0
    assert progress["wr_athletes"] == 0


def test_ftyp_header_still_counts(tmp_path):
    _seed(tmp_path, b"\x00\x00\x00\x18ftypisom" + b"unique-shoot")
    progress = gates.get_progress(tmp_path)
    assert progress["wr_labeled"] == 1
    assert progress["surfaces"] == 1
