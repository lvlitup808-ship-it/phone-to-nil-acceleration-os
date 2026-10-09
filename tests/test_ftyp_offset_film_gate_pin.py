"""Honesty pin: the letters ftyp in a notes file are not an ftyp box.

has_film used to accept any clips/*.mp4 whose first 32 bytes contained
b'ftyp' anywhere. A text file that mentions ftyp still counted as film.
Only an ISO BMFF box with brand ftyp at offset 4 counts. Gate stays closed.
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


def test_ftyp_mention_in_notes_does_not_count(tmp_path):
    _seed(tmp_path, b"notes ftyp not a box")
    progress = gates.get_progress(tmp_path)
    assert progress["wr_labeled"] == 0
    assert progress["surfaces"] == 0
    assert progress["wr_athletes"] == 0


def test_ftyp_box_at_offset_4_still_counts(tmp_path):
    _seed(tmp_path, b"\x00\x00\x00\x18ftypisom\x00\x00\x00\x00film")
    assert gates.get_progress(tmp_path)["wr_labeled"] == 1
