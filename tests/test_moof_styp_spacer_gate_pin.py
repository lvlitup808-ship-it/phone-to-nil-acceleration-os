"""Honesty pin: moof or styp before mdat is not a phone spacer.

ISO BMFF moof (movie fragment) and styp (segment type) are not free/skip/wide
placeholders a phone capture puts before media. has_film must reject them so a
forged header cannot open the golden-set gate. No NIL numbers.
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


HEADER = b"\x00\x00\x00\x10ftypisom\x00\x00\x00\x00"
MDAT = b"\x00\x00\x00\x09mdatx"


def test_moof_or_styp_before_mdat_does_not_count(tmp_path):
    for extra in (
        b"\x00\x00\x00\x08moof" + MDAT,
        b"\x00\x00\x00\x08styp" + MDAT,
    ):
        _seed(tmp_path, HEADER + extra)
        assert gates.get_progress(tmp_path)["wr_labeled"] == 0, extra


def test_free_then_mdat_still_counts(tmp_path):
    _seed(tmp_path, HEADER + b"\x00\x00\x00\x08free" + MDAT)
    assert gates.get_progress(tmp_path)["wr_labeled"] == 1
