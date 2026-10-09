"""Honesty pin: a renamed non-video is not camera film.

The gate used to count any non-empty clips/*.mp4. A text file, JSON, or JPEG
renamed to .mp4 inflated wr_labeled. Only an ISO BMFF file with an ftyp box
in the first 32 bytes counts. Gate stays closed.
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


def test_text_renamed_to_mp4_does_not_count(tmp_path):
    _seed(tmp_path, b"this is a notes file, not a video")
    progress = gates.get_progress(tmp_path)
    assert progress["wr_labeled"] == 0


def test_jpeg_renamed_to_mp4_does_not_count(tmp_path):
    _seed(tmp_path, b"\xff\xd8\xff\xe0" + b"jpeg-not-film")
    progress = gates.get_progress(tmp_path)
    assert progress["wr_labeled"] == 0


def test_ftyp_box_still_counts(tmp_path):
    _seed(tmp_path, b"\x00\x00\x00\x10ftypisom\x00\x00\x00\x00\x00\x00\x00\x0cmdatfilm")
    progress = gates.get_progress(tmp_path)
    assert progress["wr_labeled"] == 1
