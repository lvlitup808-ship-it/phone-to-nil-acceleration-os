"""Honesty pin: one film file cannot count as two golden-set clips.

Hand-written manifests can point two clip ids at the same camera path.
That must not inflate wr_labeled / db_labeled. The first clip keeps the
file; later clips that reuse it do not count.
"""

from __future__ import annotations

import json

from services.api import gates
from services.golden_set.labels import CUES, EVENTS


def _complete(movement: str = "release") -> dict:
    return {
        "events": {name: {"t_ms": 100} for name in EVENTS[movement]},
        "cues": {name: {"value": 1.0, "disputed": False} for name in CUES[movement]},
    }


def _clip(clip_id: str, path: str, position: str = "WR", movement: str = "release") -> dict:
    return {
        "clip_id": clip_id,
        "position_target": position,
        "movement": movement,
        "athlete_id": f"ath_{clip_id}",
        "surface": "turf",
        "lighting": "day",
        "camera_side": {"path": path, "present": True},
    }


def test_shared_film_path_does_not_inflate_labeled_count(tmp_path):
    (tmp_path / "labels").mkdir()
    (tmp_path / "clips").mkdir()
    (tmp_path / "clips" / "only.mp4").write_bytes(b"film")
    clips = [
        _clip("c1", "clips/only.mp4"),
        _clip("c2", "clips/only.mp4"),
    ]
    (tmp_path / "manifest.json").write_text(json.dumps({"clips": clips}))
    complete = _complete()
    for clip in clips:
        (tmp_path / "labels" / f"{clip['clip_id']}.json").write_text(
            json.dumps({"clip_id": clip["clip_id"], "coach_id": "coach_a", **complete})
        )
    progress = gates.get_progress(tmp_path)
    assert progress["wr_labeled"] == 1
    assert progress["db_labeled"] == 0


def test_distinct_film_files_still_count(tmp_path):
    (tmp_path / "labels").mkdir()
    (tmp_path / "clips").mkdir()
    (tmp_path / "clips" / "a.mp4").write_bytes(b"a")
    (tmp_path / "clips" / "b.mp4").write_bytes(b"b")
    clips = [_clip("c1", "clips/a.mp4"), _clip("c2", "clips/b.mp4")]
    (tmp_path / "manifest.json").write_text(json.dumps({"clips": clips}))
    complete = _complete()
    for clip in clips:
        (tmp_path / "labels" / f"{clip['clip_id']}.json").write_text(
            json.dumps({"clip_id": clip["clip_id"], "coach_id": "coach_a", **complete})
        )
    progress = gates.get_progress(tmp_path)
    assert progress["wr_labeled"] == 2
