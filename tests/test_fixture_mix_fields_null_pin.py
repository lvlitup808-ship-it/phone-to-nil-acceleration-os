"""Honesty pin: fixture manifest clips have null mix fields and no present film.

A clip with athlete_id, surface, or lighting set, or present:true, would start
counting toward the film_first diversity bars even without real film on disk.
This fails if the checked-in fixtures stop being pure placeholders.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data/golden_set/manifest.json"


def test_fixture_clips_have_null_mix_and_absent_film() -> None:
    data = json.loads(MANIFEST.read_text())
    assert data.get("golden_set") == "pending"
    clips = data["clips"]
    assert len(clips) == 2
    for clip in clips:
        assert clip.get("athlete_id") is None, clip["clip_id"]
        assert clip.get("surface") is None, clip["clip_id"]
        assert clip.get("lighting") is None, clip["clip_id"]
        for cam in ("camera_side", "camera_45"):
            camera = clip[cam]
            assert camera.get("present") is False, f"{clip['clip_id']} {cam}"
            assert camera.get("path", "").startswith("clips/")
