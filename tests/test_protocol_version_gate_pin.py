"""Honesty pin: a label without the manifest protocol does not open the gate.

POST /golden/labels stamps labeling_protocol_version from the manifest.
A hand-written labels/*.json can omit that stamp or name another protocol.
When the manifest declares a protocol, only a matching stamp counts.
"""

from __future__ import annotations

import json

from services.api import gates
from services.golden_set.labels import CUES, EVENTS


def _seed(tmp_path, protocol: str | None):
    (tmp_path / "labels").mkdir()
    (tmp_path / "clips").mkdir()
    (tmp_path / "clips" / "c1.mp4").write_bytes(b"x")
    clip = {
        "clip_id": "c1",
        "position_target": "WR",
        "movement": "release",
        "athlete_id": "ath_1",
        "surface": "turf",
        "lighting": "day",
        "camera_side": {"path": "clips/c1.mp4", "present": True},
    }
    manifest: dict = {"clips": [clip]}
    if protocol is not None:
        manifest["labeling_protocol_version"] = protocol
    (tmp_path / "manifest.json").write_text(json.dumps(manifest))
    return {
        "clip_id": "c1",
        "coach_id": "coach_a",
        "events": {name: {"t_ms": 100} for name in EVENTS["release"]},
        "cues": {name: {"value": 1.0, "disputed": False} for name in CUES["release"]},
    }


def test_missing_protocol_stamp_does_not_count(tmp_path):
    label = _seed(tmp_path, "1.0.0")
    (tmp_path / "labels" / "unstamped.json").write_text(json.dumps(label))
    progress = gates.get_progress(tmp_path)
    assert progress["wr_labeled"] == 0
    assert progress["inter_rater_clips"] == 0


def test_mismatched_protocol_stamp_does_not_count(tmp_path):
    label = _seed(tmp_path, "1.0.0")
    label["labeling_protocol_version"] = "0.9.0"
    (tmp_path / "labels" / "old.json").write_text(json.dumps(label))
    progress = gates.get_progress(tmp_path)
    assert progress["wr_labeled"] == 0


def test_matching_protocol_stamp_counts(tmp_path):
    label = _seed(tmp_path, "1.0.0")
    label["labeling_protocol_version"] = " 1.0.0 "
    (tmp_path / "labels" / "ok.json").write_text(json.dumps(label))
    progress = gates.get_progress(tmp_path)
    assert progress["wr_labeled"] == 1
