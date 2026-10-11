"""Honesty pin: manifest declares golden_set pending and no real film present.

Fails if the checked-in fixture manifest starts claiming present film or
opens the golden set without real labeled clips on disk.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data/golden_set/manifest.json"


def test_manifest_is_pending_fixture():
    data = json.loads(MANIFEST.read_text())
    assert data.get("golden_set") == "pending"
    assert "Fixture labels only" in data.get("note", "")
    assert "No real athlete film" in data.get("note", "")
    clips = data.get("clips", [])
    assert clips, "manifest has no clips"
    for clip in clips:
        for cam in ("camera_side", "camera_45"):
            camera = clip.get(cam) or {}
            assert camera.get("present") is not True, f"{clip.get('clip_id')} {cam} claims present"
