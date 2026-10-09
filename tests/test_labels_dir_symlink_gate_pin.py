"""Honesty pin: a symlinked labels directory is not coach labels on disk.

get_progress globs labels/*.json. Path.is_dir() follows a directory symlink,
and glob then reads the target. A link is not the label files under the golden
root. Those labels must not increment wr_labeled.
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


def test_symlinked_labels_directory_does_not_count(tmp_path):
    (tmp_path / "clips").mkdir()
    (tmp_path / "clips" / "c1.mp4").write_bytes(b"film")
    outside = tmp_path / "outside_labels"
    outside.mkdir()
    (outside / "c1.json").write_text(json.dumps(_label("c1", "coach_a")))
    (tmp_path / "labels").symlink_to(outside, target_is_directory=True)
    (tmp_path / "manifest.json").write_text(
        json.dumps(
            {
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
                "labeling_protocol_version": "1.0.0",
            }
        )
    )
    progress = gates.get_progress(tmp_path)
    assert progress["wr_labeled"] == 0
    assert progress["wr_athletes"] == 0
    assert progress["surfaces"] == 0
