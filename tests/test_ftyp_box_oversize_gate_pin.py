"""Honesty pin: an ftyp size field above 32 that does not fit is not film.

has_film accepted a clips/*.mp4 whose size field was larger than both the
32-byte header read and the file, as long as bytes 4:12 looked like ftyp
plus an alphanumeric brand. A phone box that claims 256 bytes in a 16-byte
file is not camera film. Gate stays closed. A 24-byte declaration on a short
fixture still counts; older pins use that shape.
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


def test_ftyp_size_above_32_and_file_does_not_count(tmp_path):
    # Size field says 256. The file is 16 bytes.
    _seed(tmp_path, b"\x00\x00\x01\x00ftypisom\x00\x00\x00\x00")
    assert gates.get_progress(tmp_path)["wr_labeled"] == 0


def test_short_fixture_with_size_24_still_counts(tmp_path):
    _seed(tmp_path, b"\x00\x00\x00\x18ftypisom\x00\x00\x00\x00film")
    assert gates.get_progress(tmp_path)["wr_labeled"] == 1
