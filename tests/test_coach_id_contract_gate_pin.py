"""Honesty pin: a coach id must match the label-save contract.

POST /golden/labels only accepts coach_[a-z0-9]{1,32}. The gate used to
count any ASCII token, so two hand-written files with coach ids "a" and "b"
marked a clip as double-labeled and could open inter-rater without a coach.
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


def _seed(tmp_path, coaches: list[str]) -> None:
    (tmp_path / "labels").mkdir()
    (tmp_path / "clips").mkdir()
    (tmp_path / "clips" / "c1.mp4").write_bytes(b"film")
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
    for coach in coaches:
        (tmp_path / "labels" / f"{coach}.json").write_text(
            json.dumps(_label("c1", coach))
        )


def test_junk_coach_ids_do_not_open_inter_rater(tmp_path):
    _seed(tmp_path, ["a", "b"])
    progress = gates.get_progress(tmp_path)
    assert progress["wr_labeled"] == 0
    assert progress["inter_rater_clips"] == 0


def test_contract_coach_ids_still_count(tmp_path):
    _seed(tmp_path, ["coach_a", "coach_b"])
    progress = gates.get_progress(tmp_path)
    assert progress["wr_labeled"] == 1
    assert progress["inter_rater_clips"] == 1


def test_casefolded_contract_id_counts_once(tmp_path):
    _seed(tmp_path, ["Coach_A", "coach_a"])
    progress = gates.get_progress(tmp_path)
    assert progress["wr_labeled"] == 1
    assert progress["inter_rater_clips"] == 0
