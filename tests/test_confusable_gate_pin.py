"""Honesty pin: Unicode lookalikes do not inflate golden-set progress.

NFKC, casefold, and mark stripping still leave Cyrillic homoglyphs. A coach
id or surface spelled with U+043E (cyrillic o) must not count as a second
coach or a new mix value.
"""

from __future__ import annotations

import json

from services.api import gates
from services.golden_set.labels import CUES, EVENTS

CYRILLIC_O = "\u043e"


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


def test_confusable_coach_ids_do_not_inflate_inter_rater(tmp_path):
    (tmp_path / "labels").mkdir()
    (tmp_path / "clips").mkdir()
    (tmp_path / "clips" / "c1.mp4").write_bytes(b"x")
    (tmp_path / "manifest.json").write_text(
        json.dumps({"clips": [_clip("c1", "ath_1", "turf", "day")]})
    )
    complete = _complete()
    (tmp_path / "labels" / "a.json").write_text(
        json.dumps({"clip_id": "c1", "coach_id": "coach_a", **complete})
    )
    (tmp_path / "labels" / "b.json").write_text(
        json.dumps({"clip_id": "c1", "coach_id": f"c{CYRILLIC_O}ach_a", **complete})
    )
    progress = gates.get_progress(tmp_path)
    assert progress["wr_labeled"] == 1
    assert progress["inter_rater_clips"] == 0
    assert progress["inter_rater_done"] is False


def test_confusable_mix_fields_do_not_inflate_diversity(tmp_path):
    (tmp_path / "labels").mkdir()
    (tmp_path / "clips").mkdir()
    clips = [
        _clip("c1", "ath_1", "turf", "day"),
        _clip("c2", f"ath_{CYRILLIC_O}1", f"tur{CYRILLIC_O}", f"day{CYRILLIC_O}"),
    ]
    for clip in clips:
        (tmp_path / "clips" / f"{clip['clip_id']}.mp4").write_bytes(b"x")
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
