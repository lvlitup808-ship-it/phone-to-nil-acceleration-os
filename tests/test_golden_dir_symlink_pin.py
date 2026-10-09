"""Honesty pin: a symlinked golden-set directory is not the store on disk.

labels/ and manifest.json already refuse to be symlinks. Replacing
data/golden_set itself with a link to an outside packet still followed
the link: manifest, labels, and clips resolved inside the target and
counted as labeled film. A link is not the golden set.
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


def _write_packet(root) -> None:
    (root / "labels").mkdir()
    (root / "clips").mkdir()
    (root / "clips" / "c1.mp4").write_bytes(b"\x00\x00\x00\x10ftypisom\x00\x00\x00\x00\x00\x00\x00\x0cmdatfilm")
    clip = {
        "clip_id": "c1",
        "position_target": "WR",
        "movement": "release",
        "athlete_id": "ath_1",
        "surface": "turf",
        "lighting": "day",
        "camera_side": {"path": "clips/c1.mp4", "present": True},
    }
    (root / "manifest.json").write_text(
        json.dumps({"clips": [clip], "labeling_protocol_version": "1.0.0"})
    )
    (root / "labels" / "c1.json").write_text(json.dumps(_label("c1")))


def test_real_golden_dir_still_counts(tmp_path):
    _write_packet(tmp_path)
    progress = gates.get_progress(tmp_path)
    assert progress["wr_labeled"] == 1


def test_symlinked_golden_dir_does_not_count(tmp_path):
    packet = tmp_path / "packet"
    packet.mkdir()
    _write_packet(packet)
    linked = tmp_path / "golden"
    linked.symlink_to(packet, target_is_directory=True)
    progress = gates.get_progress(linked)
    assert progress["wr_labeled"] == 0
    assert progress["wr_athletes"] == 0
    assert progress["surfaces"] == 0
    assert progress["inter_rater_clips"] == 0
