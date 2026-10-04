"""Honesty pin: one film file cannot count as two golden-set clips.

Two manifest rows that resolve to the same bytes (shared path or symlink)
must not inflate wr_labeled, db_labeled, athletes, surfaces, or lighting.
The first manifest clip that owns the file is the only one that can count.
"""

from __future__ import annotations

import json

from services.api import gates
from services.golden_set.labels import CUES, EVENTS


def _label(clip_id: str, coach_id: str = "coach_a") -> dict:
    return {
        "clip_id": clip_id,
        "coach_id": coach_id,
        "events": {name: {"t_ms": 100} for name in EVENTS["release"]},
        "cues": {name: {"value": 1.0, "disputed": False} for name in CUES["release"]},
    }


def _clip(clip_id: str, path: str, athlete_id: str, surface: str) -> dict:
    return {
        "clip_id": clip_id,
        "position_target": "WR",
        "movement": "release",
        "athlete_id": athlete_id,
        "surface": surface,
        "lighting": "daylight",
        "camera_side": {"path": path, "present": True},
    }


def _write(tmp_path, clips, labels):
    (tmp_path / "labels").mkdir(exist_ok=True)
    (tmp_path / "clips").mkdir(exist_ok=True)
    (tmp_path / "manifest.json").write_text(json.dumps({"clips": clips}))
    for i, lab in enumerate(labels):
        (tmp_path / "labels" / f"l{i}.json").write_text(json.dumps(lab))


def test_shared_film_path_counts_once(tmp_path):
    film = tmp_path / "clips" / "shared.mp4"
    film.parent.mkdir()
    film.write_bytes(b"same-bytes")
    clips = [
        _clip("c1", "clips/shared.mp4", "ath_a", "turf"),
        _clip("c2", "clips/shared.mp4", "ath_b", "grass"),
    ]
    _write(
        tmp_path,
        clips,
        [_label("c1"), _label("c2", "coach_b")],
    )
    p = gates.get_progress(tmp_path)
    assert p["wr_labeled"] == 1
    assert p["wr_athletes"] == 1
    assert p["surfaces"] == 1
    assert p["inter_rater_clips"] == 0


def test_path_alias_does_not_double_count(tmp_path):
    film = tmp_path / "clips" / "shared.mp4"
    film.parent.mkdir()
    film.write_bytes(b"same-bytes")
    clips = [
        _clip("c1", "clips/shared.mp4", "ath_a", "turf"),
        _clip("c2", "clips/nested/../shared.mp4", "ath_b", "grass"),
    ]
    _write(tmp_path, clips, [_label("c1"), _label("c2")])
    p = gates.get_progress(tmp_path)
    assert p["wr_labeled"] == 1
    assert p["wr_athletes"] == 1


def test_symlink_to_same_film_counts_once(tmp_path):
    film = tmp_path / "clips" / "real.mp4"
    film.parent.mkdir()
    film.write_bytes(b"same-bytes")
    alias = tmp_path / "clips" / "alias.mp4"
    alias.symlink_to(film)
    clips = [
        _clip("c1", "clips/real.mp4", "ath_a", "turf"),
        _clip("c2", "clips/alias.mp4", "ath_b", "grass"),
    ]
    _write(tmp_path, clips, [_label("c1"), _label("c2")])
    p = gates.get_progress(tmp_path)
    assert p["wr_labeled"] == 1
    assert p["wr_athletes"] == 1


def test_distinct_film_files_still_count(tmp_path):
    (tmp_path / "clips").mkdir()
    (tmp_path / "clips" / "a.mp4").write_bytes(b"a")
    (tmp_path / "clips" / "b.mp4").write_bytes(b"b")
    clips = [
        _clip("c1", "clips/a.mp4", "ath_a", "turf"),
        _clip("c2", "clips/b.mp4", "ath_b", "grass"),
    ]
    _write(tmp_path, clips, [_label("c1"), _label("c2")])
    p = gates.get_progress(tmp_path)
    assert p["wr_labeled"] == 2
    assert p["wr_athletes"] == 2
    assert p["surfaces"] == 2
