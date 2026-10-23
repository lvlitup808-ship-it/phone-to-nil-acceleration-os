"""Honesty pin: the checked-in golden-set manifest has no real film.

All camera present flags must stay false and athlete/surface/lighting null
until owner-supplied consented film is added. Fixture entries must not be
treated as labeled film.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data" / "golden_set" / "manifest.json"


def test_checked_in_manifest_has_no_film() -> None:
    data = json.loads(MANIFEST.read_text())
    assert data.get("golden_set") == "pending"
    clips = data.get("clips", [])
    assert clips, "manifest must list the fixture stubs"
    for clip in clips:
        for cam in ("camera_side", "camera_45"):
            assert clip.get(cam, {}).get("present") is False, clip["clip_id"]
        assert clip.get("athlete_id") is None
        assert clip.get("surface") is None
        assert clip.get("lighting") is None
