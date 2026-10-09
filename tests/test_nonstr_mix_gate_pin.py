"""Honesty pin: non-string mix fields and camera paths do not open the gate.

docs/film_first.md reads surface, lighting, and athlete_id from the manifest.
A number or boolean is not an athlete or a surface. A camera path that is not
a string is not film, and must not crash GET /gates/golden.
"""

from __future__ import annotations

import json

from services.api import gates
from services.golden_set.labels import CUES, EVENTS


def _label(clip_id: str) -> dict:
    return {
        "clip_id": clip_id,
        "coach_id": "coach_a",
        "labeling_protocol_version": "1.0.0",
        "events": {name: {"t_ms": 100} for name in EVENTS["release"]},
        "cues": {name: {"value": 1.0, "disputed": False} for name in CUES["release"]},
    }


def _write(tmp_path, clips):
    (tmp_path / "labels").mkdir()
    (tmp_path / "clips").mkdir()
    for clip in clips:
        (tmp_path / "clips" / f"{clip['clip_id']}.mp4").write_bytes(b"\x00\x00\x00\x10ftypisom\x00\x00\x00\x00" + clip["clip_id"].encode())
        (tmp_path / "labels" / f"{clip['clip_id']}.json").write_text(
            json.dumps(_label(clip["clip_id"]))
        )
    (tmp_path / "manifest.json").write_text(
        json.dumps({"clips": clips, "labeling_protocol_version": "1.0.0"})
    )


def test_non_string_mix_fields_do_not_count(tmp_path):
    clips = []
    for i, athlete, surface, lighting in (
        (1, 1, 1, True),
        (2, 1.0, False, 2),
        (3, True, "turf", "day"),
    ):
        clips.append(
            {
                "clip_id": f"c{i}",
                "position_target": "WR",
                "movement": "release",
                "athlete_id": athlete,
                "surface": surface,
                "lighting": lighting,
                "camera_side": {"path": f"clips/c{i}.mp4", "present": True},
            }
        )
    _write(tmp_path, clips)
    progress = gates.get_progress(tmp_path)
    assert progress["wr_labeled"] == 3
    assert progress["wr_athletes"] == 0
    assert progress["surfaces"] == 1
    assert progress["lighting_conditions"] == 1


def test_non_string_camera_path_does_not_crash_or_count(tmp_path):
    (tmp_path / "labels").mkdir()
    (tmp_path / "clips").mkdir()
    clip = {
        "clip_id": "c1",
        "position_target": "WR",
        "movement": "release",
        "athlete_id": "ath_1",
        "surface": "turf",
        "lighting": "day",
        "camera_side": {"path": 1, "present": True},
        "camera_45": {"path": ["clips/nope.mp4"], "present": True},
    }
    (tmp_path / "manifest.json").write_text(
        json.dumps({"clips": [clip], "labeling_protocol_version": "1.0.0"})
    )
    (tmp_path / "labels" / "c1.json").write_text(json.dumps(_label("c1")))
    progress = gates.get_progress(tmp_path)
    assert progress["wr_labeled"] == 0
    assert progress["wr_athletes"] == 0
