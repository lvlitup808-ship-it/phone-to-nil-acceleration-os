"""Load real frames for a golden-set clip (only used when POSE_REAL_FRAMES is on)."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

GOLDEN_DIR = Path(__file__).resolve().parents[3] / "data/golden_set"


class FilmNotFound(Exception):
    pass


def load_clip_frames(clip_id: str, side_clip: bool = True) -> tuple[list[np.ndarray], float]:
    """RGB frames and fps for the clip's side (or 45) camera. Raises FilmNotFound if not on disk."""
    import cv2

    root = GOLDEN_DIR.resolve()
    manifest = json.loads((GOLDEN_DIR / "manifest.json").read_text())
    clip = next((c for c in manifest.get("clips", []) if c.get("clip_id") == clip_id), None)
    if clip is None:
        raise FilmNotFound(f"{clip_id} is not in the golden-set manifest")
    key = "camera_side" if side_clip else "camera_45"
    cam = clip.get(key) or {}
    if not (cam.get("present") and cam.get("path")):
        raise FilmNotFound(f"{clip_id} has no {key} film")
    path = (root / cam["path"]).resolve()
    if not path.is_relative_to(root) or not path.is_file():
        raise FilmNotFound(f"{clip_id} {key} file is not on disk")
    cap = cv2.VideoCapture(str(path))
    try:
        fps = float(cam.get("fps") or cap.get(cv2.CAP_PROP_FPS) or 0.0)
        frames = []
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            frames.append(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    finally:
        cap.release()
    if not frames or fps <= 0:
        raise FilmNotFound(f"{clip_id} {key} could not be decoded")
    return frames, fps
