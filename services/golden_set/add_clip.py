"""Register a real (or staged) clip in data/golden_set/manifest.json.

    python -m services.golden_set.add_clip \\
      --clip-id clp_0003 \\
      --athlete-id ath_0001 \\
      --position WR \\
      --movement release \\
      --surface turf \\
      --lighting daylight \\
      --side /path/to/side.mp4 --side-fps 60 \\
      --fortyfive /path/to/45.mp4 --fortyfive-fps 60

Copies provided video files into data/golden_set/clips/ (gitignored) and
appends a validated ManifestClip. Does not invent labels, NIL numbers, or
coach annotations. Fixture entries are never treated as film.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

from packages.shared.golden import Camera, GoldenManifest, ManifestClip

ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = ROOT / "data/golden_set/manifest.json"
CLIPS_DIR = ROOT / "data/golden_set/clips"


def _next_default_clip_id(existing: list[str]) -> str:
    nums = []
    for cid in existing:
        if cid.startswith("clp_") and cid[4:].isdigit():
            nums.append(int(cid[4:]))
    n = max(nums, default=0) + 1
    return f"clp_{n:04d}"


def add_clip(
    *,
    clip_id: str | None,
    athlete_id: str,
    position_target: str,
    movement: str,
    surface: str,
    lighting: str,
    athlete_height_cm: float | None,
    side_src: Path | None,
    side_fps: float | None,
    fortyfive_src: Path | None,
    fortyfive_fps: float | None,
    dry_run: bool = False,
) -> tuple[ManifestClip, list[str]]:
    """Build, validate, and optionally write a new clip entry. Returns the clip and log lines."""
    raw = json.loads(MANIFEST_PATH.read_text())
    manifest = GoldenManifest.model_validate(raw)
    existing_ids = [c.clip_id for c in manifest.clips]
    cid = clip_id or _next_default_clip_id(existing_ids)
    if cid in existing_ids:
        raise SystemExit(f"clip_id {cid} already in manifest")

    side: Camera | None = None
    fortyfive: Camera | None = None
    messages: list[str] = []

    if side_src is not None:
        if not side_src.is_file():
            raise SystemExit(f"side video not found: {side_src}")
        dest_name = f"{cid}_side{side_src.suffix.lower() or '.mp4'}"
        dest = CLIPS_DIR / dest_name
        if not dry_run:
            CLIPS_DIR.mkdir(parents=True, exist_ok=True)
            shutil.copy2(side_src, dest)
            messages.append(f"copied side -> {dest.relative_to(ROOT)}")
        side = Camera(path=f"clips/{dest_name}", fps=side_fps, present=True)
    if fortyfive_src is not None:
        if not fortyfive_src.is_file():
            raise SystemExit(f"45 video not found: {fortyfive_src}")
        dest_name = f"{cid}_45{fortyfive_src.suffix.lower() or '.mp4'}"
        dest = CLIPS_DIR / dest_name
        if not dry_run:
            CLIPS_DIR.mkdir(parents=True, exist_ok=True)
            shutil.copy2(fortyfive_src, dest)
            messages.append(f"copied 45 -> {dest.relative_to(ROOT)}")
        fortyfive = Camera(path=f"clips/{dest_name}", fps=fortyfive_fps, present=True)

    if side is None and fortyfive is None:
        raise SystemExit("at least one of --side or --fortyfive is required for a real clip")

    clip = ManifestClip(
        clip_id=cid,
        athlete_id=athlete_id,
        position_target=position_target,  # type: ignore[arg-type]
        movement=movement,  # type: ignore[arg-type]
        surface=surface,  # type: ignore[arg-type]
        lighting=lighting,  # type: ignore[arg-type]
        athlete_height_cm=athlete_height_cm,
        camera_side=side,
        camera_45=fortyfive,
        disputed=False,
        labels={},
    )
    # Re-validate whole manifest so uniqueness + filmed rules fire.
    new_clips = list(manifest.clips) + [clip]
    GoldenManifest.model_validate({**raw, "clips": [c.model_dump() for c in new_clips]})

    if not dry_run:
        raw["clips"] = [c.model_dump() for c in new_clips]
        MANIFEST_PATH.write_text(json.dumps(raw, indent=2) + "\n")
        messages.append(f"wrote {MANIFEST_PATH.relative_to(ROOT)} ({cid})")
    else:
        messages.append(f"dry-run: would write {cid}")

    return clip, messages


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Add a real clip to the golden-set manifest")
    p.add_argument("--clip-id", default=None, help="clp_NNNN (default: next free)")
    p.add_argument("--athlete-id", required=True, help="ath_NNNN")
    p.add_argument("--position", required=True, choices=["WR", "DB"])
    p.add_argument("--movement", required=True, choices=["release", "break"])
    p.add_argument("--surface", required=True, choices=["turf", "grass", "track"])
    p.add_argument("--lighting", required=True, choices=["daylight", "night_lit", "indoor"])
    p.add_argument("--height-cm", type=float, default=None)
    p.add_argument("--side", type=Path, default=None, help="path to side-view video")
    p.add_argument("--side-fps", type=float, default=None)
    p.add_argument("--fortyfive", type=Path, default=None, help="path to 45-view video")
    p.add_argument("--fortyfive-fps", type=float, default=None)
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args(argv)

    try:
        clip, lines = add_clip(
            clip_id=args.clip_id,
            athlete_id=args.athlete_id,
            position_target=args.position,
            movement=args.movement,
            surface=args.surface,
            lighting=args.lighting,
            athlete_height_cm=args.height_cm,
            side_src=args.side,
            side_fps=args.side_fps,
            fortyfive_src=args.fortyfive,
            fortyfive_fps=args.fortyfive_fps,
            dry_run=args.dry_run,
        )
    except SystemExit as e:
        print(e, file=sys.stderr)
        return 1
    for line in lines:
        print(line)
    print(f"ok {clip.clip_id} athlete={clip.athlete_id} surface={clip.surface} lighting={clip.lighting}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
