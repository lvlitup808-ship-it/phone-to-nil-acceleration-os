"""Honesty pin: a byte copy of a camera file is the same film.

Hardlinks already share an inode and count once. A copy gets a new inode
and a new path, so get_progress used to treat it as a second clip and
inflate wr_labeled, surfaces, and athletes. Same bytes are not a second shoot.
"""

from __future__ import annotations

import json
import shutil

from services.api import gates
from services.golden_set.labels import CUES, EVENTS


def _label(clip_id: str, coach: str = "coach_a") -> dict:
    return {
        "clip_id": clip_id,
        "coach_id": coach,
        "labeling_protocol_version": "1.0.0",
        "events": {name: {"t_ms": 100} for name in EVENTS["release"]},
        "cues": {name: {"value": 1.0, "disputed": False} for name in CUES["release"]},
    }


def _clip(clip_id: str, athlete: str, surface: str) -> dict:
    return {
        "clip_id": clip_id,
        "position_target": "WR",
        "movement": "release",
        "athlete_id": athlete,
        "surface": surface,
        "lighting": "day",
        "camera_side": {"path": f"clips/{clip_id}.mp4", "present": True},
    }


def _seed(tmp_path, first: bytes, second: bytes):
    (tmp_path / "labels").mkdir()
    (tmp_path / "clips").mkdir()
    (tmp_path / "clips" / "c1.mp4").write_bytes(first)
    (tmp_path / "clips" / "c2.mp4").write_bytes(second)
    clips = [_clip("c1", "ath_1", "turf"), _clip("c2", "ath_2", "grass")]
    (tmp_path / "manifest.json").write_text(
        json.dumps({"clips": clips, "labeling_protocol_version": "1.0.0"})
    )
    (tmp_path / "labels" / "c1.json").write_text(json.dumps(_label("c1")))
    (tmp_path / "labels" / "c2.json").write_text(json.dumps(_label("c2", "coach_b")))


def test_byte_copy_does_not_count_twice(tmp_path):
    payload = b"same-phone-clip"
    _seed(tmp_path, payload, payload)
    assert (tmp_path / "clips" / "c1.mp4").stat().st_ino != (
        tmp_path / "clips" / "c2.mp4"
    ).stat().st_ino
    progress = gates.get_progress(tmp_path)
    assert progress["wr_labeled"] == 1
    assert progress["surfaces"] == 1
    assert progress["wr_athletes"] == 1


def test_distinct_bytes_still_count(tmp_path):
    _seed(tmp_path, b"film-one", b"film-two")
    progress = gates.get_progress(tmp_path)
    assert progress["wr_labeled"] == 2
    assert progress["surfaces"] == 2
    assert progress["wr_athletes"] == 2


def test_shutil_copy_is_not_a_second_shoot(tmp_path):
    _seed(tmp_path, b"original-shoot", b"placeholder")
    shutil.copy(tmp_path / "clips" / "c1.mp4", tmp_path / "clips" / "c2.mp4")
    progress = gates.get_progress(tmp_path)
    assert progress["wr_labeled"] == 1
