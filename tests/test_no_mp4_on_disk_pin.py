"""Honesty pin: data/golden_set/clips contains no camera film.

The directory exists only to hold the intake path. A real .mp4 would be
counted by the gate once the manifest marks present:true. Fixtures stay
absent so the gate remains closed.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLIPS = ROOT / "data" / "golden_set" / "clips"


def test_clips_dir_has_no_mp4_film() -> None:
    assert CLIPS.is_dir(), "clips directory missing"
    mp4s = list(CLIPS.glob("*.mp4"))
    assert mp4s == [], f"unexpected film files: {[p.name for p in mp4s]}"
    # .gitkeep is the only expected placeholder
    others = [p for p in CLIPS.iterdir() if p.name != ".gitkeep"]
    assert others == [], f"unexpected files: {[p.name for p in others]}"
