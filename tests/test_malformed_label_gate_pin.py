"""Honesty pin: a non-object file in labels/ must not crash or count.

get_progress walks every labels/*.json. A list, string, or number would
raise AttributeError on .get and take GET /gates/golden down. A downed gate
is not a closed gate. Malformed files are skipped and do not add progress.
"""

from __future__ import annotations

import json

from services.api import gates
from services.golden_set.labels import CUES, EVENTS


def _film(tmp_path):
    (tmp_path / "labels").mkdir()
    (tmp_path / "clips").mkdir()
    (tmp_path / "clips" / "c1.mp4").write_bytes(b"x")
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
                ]
            }
        )
    )


def test_non_object_label_file_does_not_crash_or_count(tmp_path):
    _film(tmp_path)
    (tmp_path / "labels" / "array.json").write_text("[]")
    (tmp_path / "labels" / "string.json").write_text('"coach_a"')
    (tmp_path / "labels" / "number.json").write_text("1")
    progress = gates.get_progress(tmp_path)
    assert progress["wr_labeled"] == 0
    assert progress["db_labeled"] == 0
    assert progress["inter_rater_clips"] == 0
    assert gates.prescription_enabled(progress) is False


def test_non_object_beside_a_real_label_does_not_inflate(tmp_path):
    _film(tmp_path)
    (tmp_path / "labels" / "array.json").write_text("[]")
    (tmp_path / "labels" / "string.json").write_text('"coach_a"')
    complete = {
        "events": {name: {"t_ms": 100} for name in EVENTS["release"]},
        "cues": {name: {"value": 1.0} for name in CUES["release"]},
    }
    (tmp_path / "labels" / "real.json").write_text(
        json.dumps({"clip_id": "c1", "coach_id": "coach_a", **complete})
    )
    progress = gates.get_progress(tmp_path)
    assert progress["wr_labeled"] == 1
    assert progress["inter_rater_clips"] == 0
