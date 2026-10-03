"""Honesty pin: blank or padded coach ids do not inflate the gate.

Inter-rater is two distinct coaches on the same filmed clip. Whitespace-only
ids are not coaches, and padding must not split one coach into two.
"""

from __future__ import annotations

import json

from services.api import gates


def test_whitespace_coach_id_does_not_inflate_inter_rater(tmp_path):
    (tmp_path / "labels").mkdir()
    (tmp_path / "clips").mkdir()
    (tmp_path / "clips" / "c1.mp4").write_bytes(b"x")
    clip = {
        "clip_id": "c1",
        "position_target": "WR",
        "athlete_id": "ath_1",
        "surface": "turf",
        "lighting": "day",
        "camera_side": {"path": "clips/c1.mp4", "present": True},
    }
    (tmp_path / "manifest.json").write_text(json.dumps({"clips": [clip]}))
    (tmp_path / "labels" / "blank.json").write_text(
        json.dumps({"clip_id": "c1", "coach_id": "   "})
    )
    (tmp_path / "labels" / "padded.json").write_text(
        json.dumps({"clip_id": "c1", "coach_id": " coach_a "})
    )
    (tmp_path / "labels" / "same.json").write_text(
        json.dumps({"clip_id": "c1", "coach_id": "coach_a"})
    )
    progress = gates.get_progress(tmp_path)
    assert progress["wr_labeled"] == 1
    assert progress["inter_rater_clips"] == 0
    assert progress["inter_rater_done"] is False
