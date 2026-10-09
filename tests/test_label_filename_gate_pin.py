"""Honesty pin: a label file whose name is not the save path is not a rater.

save() writes labels/<clip_id>_<coach_id>.json. get_progress used to count
every labels/*.json whose body named a filmed clip. A hand-dropped notes.json
with a second coach_id inflated inter_rater_clips without an append-only save.
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


def _seed(tmp_path):
    (tmp_path / "labels").mkdir()
    (tmp_path / "clips").mkdir()
    (tmp_path / "clips" / "c1.mp4").write_bytes(b"film-one")
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
    (tmp_path / "labels" / "c1_coach_a.json").write_text(json.dumps(_label("c1", "coach_a")))
    return clip


def test_mismatched_label_name_is_not_a_second_rater(tmp_path):
    _seed(tmp_path)
    (tmp_path / "labels" / "notes.json").write_text(json.dumps(_label("c1", "coach_b")))
    progress = gates.get_progress(tmp_path)
    assert progress["wr_labeled"] == 1
    assert progress["inter_rater_clips"] == 0


def test_only_a_mismatched_name_does_not_label(tmp_path):
    _seed(tmp_path)
    (tmp_path / "labels" / "c1_coach_a.json").unlink()
    (tmp_path / "labels" / "notes.json").write_text(json.dumps(_label("c1", "coach_a")))
    progress = gates.get_progress(tmp_path)
    assert progress["wr_labeled"] == 0


def test_save_path_and_clip_stem_still_count(tmp_path):
    _seed(tmp_path)
    (tmp_path / "labels" / "c1_coach_b.json").write_text(json.dumps(_label("c1", "coach_b")))
    progress = gates.get_progress(tmp_path)
    assert progress["wr_labeled"] == 1
    assert progress["inter_rater_clips"] == 1

    (tmp_path / "labels" / "c1_coach_a.json").unlink()
    (tmp_path / "labels" / "c1_coach_b.json").unlink()
    (tmp_path / "labels" / "c1.json").write_text(json.dumps(_label("c1", "coach_a")))
    progress = gates.get_progress(tmp_path)
    assert progress["wr_labeled"] == 1
    assert progress["inter_rater_clips"] == 0
