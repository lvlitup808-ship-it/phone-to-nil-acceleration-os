"""Honesty pin: a label file cannot name a different coach than its body.

POST /golden/labels writes labels/<clip_id>_<coach_id>.json. A file whose
stem is that clip plus another coach, with a different coach_id inside, is
not a coach label and must not move wr_labeled. A matching save still counts.
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


def _manifest(tmp_path) -> None:
    (tmp_path / "clips").mkdir()
    (tmp_path / "clips" / "c1.mp4").write_bytes(b"film-not-a-fixture")
    (tmp_path / "labels").mkdir()
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


def test_filename_coach_must_match_body(tmp_path):
    _manifest(tmp_path)
    (tmp_path / "labels" / "c1_coach_b.json").write_text(json.dumps(_label("c1", "coach_a")))
    progress = gates.get_progress(tmp_path)
    assert progress["wr_labeled"] == 0
    assert progress["inter_rater_clips"] == 0


def test_save_contract_filename_still_counts(tmp_path):
    _manifest(tmp_path)
    (tmp_path / "labels" / "c1_coach_a.json").write_text(json.dumps(_label("c1", "coach_a")))
    progress = gates.get_progress(tmp_path)
    assert progress["wr_labeled"] == 1
