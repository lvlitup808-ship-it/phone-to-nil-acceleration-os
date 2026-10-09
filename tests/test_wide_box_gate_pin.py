"""Honesty pin: a wide box that is not 8 bytes is not a phone spacer.

has_film treated any wide box of 8 bytes or more as something that may sit
between ftyp and mdat. QuickTime wide is an 8-byte placeholder. A longer
wide must not raise wr_labeled. Gate stays closed.
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


def test_long_wide_before_mdat_does_not_count(tmp_path):
    for extra in (b"\x00\x00\x00\x0cwidepad!", b"\x00\x00\x00\x10wide" + b"pad!"):
        _seed(tmp_path, HEADER + extra + MDAT)
        assert gates.get_progress(tmp_path)["wr_labeled"] == 0, extra


def test_wide_with_payload_only_does_not_count(tmp_path):
    # A wide box is not mdat. Payload inside wide is not camera film.
    _seed(tmp_path, HEADER + b"\x00\x00\x00\x09widex")
    assert gates.get_progress(tmp_path)["wr_labeled"] == 0


def test_eight_byte_wide_then_mdat_still_counts(tmp_path):
    _seed(tmp_path, HEADER + b"\x00\x00\x00\x08wide" + MDAT)
    assert gates.get_progress(tmp_path)["wr_labeled"] == 1


def test_skip_longer_than_eight_then_mdat_still_counts(tmp_path):
    _seed(tmp_path, HEADER + b"\x00\x00\x00\x0cskippad!" + MDAT)
    assert gates.get_progress(tmp_path)["wr_labeled"] == 1
