"""Honesty pin: golden-set manifest stays pending until real labeled film.

No clip may report camera film present. Gate stays closed. No NIL numbers.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data/golden_set/manifest.json"


def test_manifest_golden_set_is_pending() -> None:
    data = json.loads(MANIFEST.read_text())
    assert data.get("golden_set") == "pending", "golden_set must stay pending until real film"


def test_no_clip_has_camera_film_present() -> None:
    data = json.loads(MANIFEST.read_text())
    for clip in data.get("clips", []):
        side = clip.get("camera_side", {})
        forty = clip.get("camera_45", {})
        assert side.get("present") is False, f"{clip.get('clip_id')} side present"
        assert forty.get("present") is False, f"{clip.get('clip_id')} 45 present"
