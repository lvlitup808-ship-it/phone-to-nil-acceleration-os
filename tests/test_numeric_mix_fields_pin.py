"""Honesty pin: numeric mix fields do not satisfy the film-first gate.

docs/film_first.md counts surfaces, lighting, and athletes from recorded
manifest strings. A hand-edited number (1, 2, 3) is not a surface, a
lighting condition, or an athlete id, even when the clip has real film
and a complete coach label. Those values must not inflate the mix.
"""

from __future__ import annotations

import json

from services.api import gates
from services.golden_set.labels import CUES, EVENTS


def test_numeric_mix_fields_do_not_count(tmp_path):
    (tmp_path / "labels").mkdir()
    (tmp_path / "clips").mkdir()
    for i in (1, 2, 3):
        (tmp_path / "clips" / f"c{i}.mp4").write_bytes(b"x")
    clips = []
    for i, position in ((1, "WR"), (2, "WR"), (3, "DB")):
        clips.append({
            "clip_id": f"c{i}",
            "position_target": position,
            "movement": "release",
            "athlete_id": i,
            "surface": i,
            "lighting": i,
            "camera_side": {"path": f"clips/c{i}.mp4", "present": True},
        })
        (tmp_path / "labels" / f"l{i}.json").write_text(
            json.dumps({
                "clip_id": f"c{i}",
                "coach_id": "coach_a",
                "events": {name: {"t_ms": 100} for name in EVENTS["release"]},
                "cues": {name: {"value": 1.0, "disputed": False} for name in CUES["release"]},
            })
        )
    (tmp_path / "manifest.json").write_text(json.dumps({"clips": clips}))
    progress = gates.get_progress(tmp_path)
    assert progress["wr_labeled"] == 2
    assert progress["db_labeled"] == 1
    assert progress["surfaces"] == 0
    assert progress["lighting_conditions"] == 0
    assert progress["wr_athletes"] == 0
    assert progress["db_athletes"] == 0
