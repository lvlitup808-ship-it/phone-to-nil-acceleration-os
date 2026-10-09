"""Honesty pin: case variants do not inflate golden-set progress.

Hand-written labels can spell the same coach, athlete, surface, or lighting
two ways. Distinct counts must not treat that as inter-rater or mix diversity.
"""

from __future__ import annotations

import json

from services.api import gates
from services.golden_set.labels import CUES, EVENTS


def _complete():
    return {
        "events": {name: {"t_ms": 100} for name in EVENTS["release"]},
        "cues": {name: {"value": 1.0, "disputed": False} for name in CUES["release"]},
    }


def _clip(clip_id: str, athlete_id: str, surface: str, lighting: str) -> dict:
    return {
        "clip_id": clip_id,
        "position_target": "WR",
        "movement": "release",
        "athlete_id": athlete_id,
        "surface": surface,
        "lighting": lighting,
        "camera_side": {"path": f"clips/{clip_id}.mp4", "present": True},
    }


def test_case_variant_coach_ids_do_not_inflate_inter_rater(tmp_path):
    (tmp_path / "labels").mkdir()
    (tmp_path / "clips").mkdir()
    (tmp_path / "clips" / "c1.mp4").write_bytes(b"\x00\x00\x00\x10ftypisom\x00\x00\x00\x00x")
    (tmp_path / "manifest.json").write_text(json.dumps({"clips": [_clip("c1", "ath_1", "turf", "day")]}))
    complete = _complete()
    (tmp_path / "labels" / "a.json").write_text(
        json.dumps({"clip_id": "c1", "coach_id": "coach_a", **complete})
    )
    (tmp_path / "labels" / "b.json").write_text(
        json.dumps({"clip_id": "c1", "coach_id": "Coach_A", **complete})
    )
    progress = gates.get_progress(tmp_path)
    assert progress["wr_labeled"] == 1
    assert progress["inter_rater_clips"] == 0
    assert progress["inter_rater_done"] is False


def test_case_variant_mix_fields_do_not_inflate_diversity(tmp_path):
    (tmp_path / "labels").mkdir()
    (tmp_path / "clips").mkdir()
    clips = [
        _clip("c1", "ath_1", "turf", "day"),
        _clip("c2", "Ath_1", "Turf", "Day"),
    ]
    for clip in clips:
        (tmp_path / "clips" / f"{clip['clip_id']}.mp4").write_bytes(b"\x00\x00\x00\x10ftypisom\x00\x00\x00\x00" + clip["clip_id"].encode())
    (tmp_path / "manifest.json").write_text(json.dumps({"clips": clips}))
    complete = _complete()
    for clip in clips:
        (tmp_path / "labels" / f"{clip['clip_id']}.json").write_text(
            json.dumps({"clip_id": clip["clip_id"], "coach_id": "coach_a", **complete})
        )
    progress = gates.get_progress(tmp_path)
    assert progress["wr_labeled"] == 2
    assert progress["wr_athletes"] == 1
    assert progress["surfaces"] == 1
    assert progress["lighting_conditions"] == 1
