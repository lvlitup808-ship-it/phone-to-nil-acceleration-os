"""Honesty pin: case variants do not inflate the golden-set mix.

Surface, lighting, and athlete_id are free text. 'Turf' and 'turf' are one
surface; 'Ath_1' and 'ath_1' are one athlete. Coach ids are casefolded the
same way so 'Coach_A' and 'coach_a' are not two raters.
"""

from __future__ import annotations

import json

from services.api import gates


def test_case_variants_do_not_inflate_mix(tmp_path):
    (tmp_path / "labels").mkdir()
    (tmp_path / "clips").mkdir()
    clips = []
    for i, (athlete, surface, lighting, coach) in enumerate(
        (
            ("Ath_1", "Turf", "Day", "Coach_A"),
            ("ath_1", "turf", "day", "coach_a"),
        )
    ):
        cid = f"c{i}"
        (tmp_path / "clips" / f"{cid}.mp4").write_bytes(b"x")
        clips.append(
            {
                "clip_id": cid,
                "position_target": "WR",
                "athlete_id": athlete,
                "surface": surface,
                "lighting": lighting,
                "camera_side": {"path": f"clips/{cid}.mp4", "present": True},
            }
        )
        (tmp_path / "labels" / f"{cid}.json").write_text(
            json.dumps({"clip_id": cid, "coach_id": coach})
        )
    (tmp_path / "manifest.json").write_text(json.dumps({"clips": clips}))
    progress = gates.get_progress(tmp_path)
    assert progress["wr_labeled"] == 2
    assert progress["wr_athletes"] == 1
    assert progress["surfaces"] == 1
    assert progress["lighting_conditions"] == 1
    assert progress["inter_rater_clips"] == 0
    assert progress["inter_rater_done"] is False
