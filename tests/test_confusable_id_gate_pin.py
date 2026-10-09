"""Honesty pin: a lookalike coach id is not a second rater.

Inter-rater is two coaches on one filmed clip. NFKC does not fold Cyrillic
or other confusable letters into Latin, so a second file whose coach id only
differs by a non-ASCII lookalike must not open inter-rater or add a surface.
"""

from __future__ import annotations

import json

from services.api import gates
from services.golden_set.labels import CUES, EVENTS


def test_confusable_coach_id_does_not_inflate_inter_rater(tmp_path):
    (tmp_path / "labels").mkdir()
    (tmp_path / "clips").mkdir()
    (tmp_path / "clips" / "c1.mp4").write_bytes(b"\x00\x00\x00\x18ftypisom" + b"x")
    clip = {
        "clip_id": "c1",
        "position_target": "WR",
        "movement": "release",
        "athlete_id": "ath_1",
        "surface": "turf",
        "lighting": "day",
        "camera_side": {"path": "clips/c1.mp4", "present": True},
    }
    (tmp_path / "manifest.json").write_text(json.dumps({"clips": [clip]}))
    complete = {
        "events": {name: {"t_ms": 100} for name in EVENTS["release"]},
        "cues": {name: {"value": 1.0, "disputed": False} for name in CUES["release"]},
    }
    (tmp_path / "labels" / "c1_coach_a.json").write_text(
        json.dumps({"clip_id": "c1", "coach_id": "coach_a", **complete})
    )
    # Cyrillic с/о look like Latin c/o. Must not be a second coach.
    (tmp_path / "labels" / "c1_lookalike.json").write_text(
        json.dumps({"clip_id": "c1", "coach_id": "\u0441oach_a", **complete})
    )
    progress = gates.get_progress(tmp_path)
    assert progress["wr_labeled"] == 1
    assert progress["inter_rater_clips"] == 0
    assert progress["inter_rater_done"] is False


def test_confusable_surface_does_not_inflate_mix(tmp_path):
    (tmp_path / "labels").mkdir()
    (tmp_path / "clips").mkdir()
    (tmp_path / "clips" / "c1.mp4").write_bytes(b"\x00\x00\x00\x18ftypisom" + b"x")
    (tmp_path / "clips" / "c2.mp4").write_bytes(b"\x00\x00\x00\x18ftypisom" + b"y")
    complete = {
        "events": {name: {"t_ms": 100} for name in EVENTS["release"]},
        "cues": {name: {"value": 1.0, "disputed": False} for name in CUES["release"]},
    }
    clips = []
    for cid, surface in (("c1", "turf"), ("c2", "\u0442urf")):
        clips.append(
            {
                "clip_id": cid,
                "position_target": "WR",
                "movement": "release",
                "athlete_id": "ath_1",
                "surface": surface,
                "lighting": "day",
                "camera_side": {"path": f"clips/{cid}.mp4", "present": True},
            }
        )
        (tmp_path / "labels" / f"{cid}_coach_a.json").write_text(
            json.dumps({"clip_id": cid, "coach_id": "coach_a", **complete})
        )
    (tmp_path / "manifest.json").write_text(json.dumps({"clips": clips}))
    progress = gates.get_progress(tmp_path)
    assert progress["wr_labeled"] == 2
    assert progress["surfaces"] == 1
    assert progress["wr_athletes"] == 1
