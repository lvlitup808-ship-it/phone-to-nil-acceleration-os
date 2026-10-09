"""Honesty pin: a non-mp4 file inside the golden root is not camera film.

has_film used to accept any non-empty regular file under the golden root.
Pointing camera_side at manifest.json, a coach label, or a .txt still
inside the root would otherwise count as filmed. The intake contract is
clips/<name>.mp4. A document is not a clip.
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


def _seed(tmp_path, path: str, payload: bytes = b"not-film"):
    (tmp_path / "labels").mkdir()
    (tmp_path / "clips").mkdir()
    target = tmp_path / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(payload)
    clip = {
        "clip_id": "c1",
        "position_target": "WR",
        "movement": "release",
        "athlete_id": "ath_1",
        "surface": "turf",
        "lighting": "day",
        "camera_side": {"path": path, "present": True},
    }
    (tmp_path / "manifest.json").write_text(
        json.dumps({"clips": [clip], "labeling_protocol_version": "1.0.0"})
    )
    (tmp_path / "labels" / "c1.json").write_text(json.dumps(_label("c1")))
    return clip


def test_manifest_json_is_not_film(tmp_path):
    clip = _seed(tmp_path, "manifest.json", b'{"clips":[]}')
    assert gates.has_film(clip, tmp_path) is False
    progress = gates.get_progress(tmp_path)
    assert progress["wr_labeled"] == 0
    assert progress["surfaces"] == 0
    assert progress["wr_athletes"] == 0


def test_label_json_is_not_film(tmp_path):
    clip = _seed(tmp_path, "labels/c1.json")
    assert gates.has_film(clip, tmp_path) is False
    progress = gates.get_progress(tmp_path)
    assert progress["wr_labeled"] == 0


def test_txt_under_clips_is_not_film(tmp_path):
    clip = _seed(tmp_path, "clips/c1.txt", b"notes")
    assert gates.has_film(clip, tmp_path) is False
    progress = gates.get_progress(tmp_path)
    assert progress["wr_labeled"] == 0


def test_mp4_under_clips_still_counts(tmp_path):
    _seed(tmp_path, "clips/c1.mp4", b"\x00\x00\x00\x18ftypisom\x00\x00\x00\x00film")
    progress = gates.get_progress(tmp_path)
    assert progress["wr_labeled"] == 1
