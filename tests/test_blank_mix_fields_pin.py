"""Honesty pin: blank mix fields do not satisfy the film-first gate.

docs/film_first.md counts surfaces, lighting, and athletes from recorded
manifest fields. Whitespace or empty strings are not a surface, a lighting
condition, or an athlete, even when the clip has real film and a coach label.
"""

from __future__ import annotations

import json

from services.api import gates


def test_blank_diversity_fields_do_not_count(tmp_path):
    (tmp_path / "labels").mkdir()
    (tmp_path / "clips").mkdir()
    (tmp_path / "clips" / "c1.mp4").write_bytes(b"x")
    clip = {
        "clip_id": "c1",
        "position_target": "WR",
        "athlete_id": "   ",
        "surface": " ",
        "lighting": "",
        "camera_side": {"path": "clips/c1.mp4", "present": True},
    }
    (tmp_path / "manifest.json").write_text(json.dumps({"clips": [clip]}))
    (tmp_path / "labels" / "l0.json").write_text(
        json.dumps({"clip_id": "c1", "coach_id": "coach_a"})
    )
    progress = gates.get_progress(tmp_path)
    assert progress["wr_labeled"] == 1
    assert progress["surfaces"] == 0
    assert progress["lighting_conditions"] == 0
    assert progress["wr_athletes"] == 0
