"""Honesty pin: a symlinked manifest.json is not the golden-set manifest.

Path.read_text follows a file symlink. A manifest.json link at a complete
packet must not open progress on the golden-set gate. A real manifest file
still counts.
"""

from __future__ import annotations

import json

from services.api import gates
from services.golden_set.labels import CUES, EVENTS


def _label(clip_id: str, coach: str) -> dict:
    return {
        "clip_id": clip_id,
        "coach_id": coach,
        "labeling_protocol_version": "1.0.0",
        "events": {name: {"t_ms": 100} for name in EVENTS["release"]},
        "cues": {name: {"value": 1.0, "disputed": False} for name in CUES["release"]},
    }


def _packet(directory) -> None:
    (directory / "clips").mkdir()
    (directory / "clips" / "c1.mp4").write_bytes(b"\x00\x00\x00\x10ftypisom\x00\x00\x00\x00film-not-a-fixture")
    (directory / "labels").mkdir()
    (directory / "labels" / "c1_coach_a.json").write_text(
        json.dumps(_label("c1", "coach_a"))
    )


def _manifest() -> str:
    return json.dumps(
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


def test_symlinked_manifest_does_not_count(tmp_path):
    _packet(tmp_path)
    outside = tmp_path / "outside_manifest.json"
    outside.write_text(_manifest())
    (tmp_path / "manifest.json").symlink_to(outside)
    progress = gates.get_progress(tmp_path)
    assert progress["wr_labeled"] == 0
    assert progress["wr_athletes"] == 0
    assert progress["inter_rater_clips"] == 0


def test_real_manifest_file_still_counts(tmp_path):
    _packet(tmp_path)
    (tmp_path / "manifest.json").write_text(_manifest())
    progress = gates.get_progress(tmp_path)
    assert progress["wr_labeled"] == 1
