"""Honesty pin: clip_id spelling variants do not inflate the golden-set gate.

A second manifest row whose clip_id is the same after strip, casefold, NFKC,
and dropping format characters and combining marks is the same clip. A label
that uses that variant must not add wr_labeled or a second athlete.
"""

from __future__ import annotations

import json

from services.api import gates
from services.golden_set.labels import CUES, EVENTS

ZWSP = "\u200b"


def _complete():
    return {
        "events": {name: {"t_ms": 100} for name in EVENTS["release"]},
        "cues": {name: {"value": 1.0, "disputed": False} for name in CUES["release"]},
    }


def _clip(clip_id: str, athlete_id: str = "ath_1") -> dict:
    safe = clip_id.replace(ZWSP, "z").replace(" ", "_")
    return {
        "clip_id": clip_id,
        "position_target": "WR",
        "movement": "release",
        "athlete_id": athlete_id,
        "surface": "turf",
        "lighting": "day",
        "camera_side": {"path": f"clips/{safe}.mp4", "present": True},
    }


def _write(tmp_path, clips, labels):
    (tmp_path / "labels").mkdir()
    (tmp_path / "clips").mkdir()
    for clip in clips:
        safe = clip["clip_id"].replace(ZWSP, "z").replace(" ", "_")
        (tmp_path / "clips" / f"{safe}.mp4").write_bytes(b"x")
    (tmp_path / "manifest.json").write_text(json.dumps({"clips": clips}))
    complete = _complete()
    for name, clip_id, coach in labels:
        (tmp_path / "labels" / name).write_text(
            json.dumps({"clip_id": clip_id, "coach_id": coach, **complete})
        )


def test_spaced_clip_id_does_not_inflate_wr_labeled(tmp_path):
    _write(
        tmp_path,
        [_clip("c1"), _clip("c1 ", "ath_2")],
        [("a.json", "c1", "coach_a"), ("b.json", "c1 ", "coach_b")],
    )
    progress = gates.get_progress(tmp_path)
    assert progress["wr_labeled"] == 1
    assert progress["wr_athletes"] == 1
    assert progress["inter_rater_clips"] == 1


def test_zero_width_clip_id_does_not_inflate_wr_labeled(tmp_path):
    twin = f"c1{ZWSP}"
    _write(
        tmp_path,
        [_clip("c1"), _clip(twin, "ath_2")],
        [("a.json", "c1", "coach_a"), ("b.json", twin, "coach_b")],
    )
    progress = gates.get_progress(tmp_path)
    assert progress["wr_labeled"] == 1
    assert progress["wr_athletes"] == 1
    assert progress["inter_rater_clips"] == 1
