"""Add a filmed clip to data/golden_set/manifest.json.

    python -m services.golden_set.add_clip \\
        --side ath_0042_WR_release_side_20260925.mp4 \\
        --45   ath_0042_WR_release_45_20260925.mp4 \\
        --surface turf --lighting daylight [--fps 60] [--height-cm 185] [--dry-run]

Both files must already be in data/golden_set/clips/ (gitignored; never committed).
athlete_id, position and movement are read from the file names (naming contract,
services/cv_worker/ingest/naming.py); surface and lighting come from the intake
form. The clip is refused unless both angles are on disk, so every clip added
here is present: true and counts toward the gate. The new manifest is run
through the same check as make lint before it is written.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from packages.shared.golden import GoldenManifest
from services.cv_worker.ingest.naming import PATTERN, RENAME
from services.golden_set.manifest import MANIFEST, film_problems

GOLDEN_DIR = MANIFEST.parent


class AddClipError(Exception):
    pass


def _camera(golden_dir: Path, name: str, angle: tuple[str, ...], fps: float | None) -> tuple[dict, tuple]:
    clips = (golden_dir / "clips").resolve()
    path = (clips / name).resolve()
    if path.parent != clips:
        raise AddClipError(f"{name}: give a file name inside {clips}, not a path")
    m = PATTERN.match(path.name)
    if m is None:
        raise AddClipError(f"bad_filename: {path.name}. {RENAME}")
    if m.group(4) not in angle:
        raise AddClipError(f"{path.name}: expected a {'/'.join(angle)} angle file")
    if not path.is_file():
        raise AddClipError(f"missing_side_or_45: {path} is not on disk")
    return {"path": f"clips/{path.name}", "fps": fps, "present": True}, m.groups()


def build_clip(
    manifest: dict[str, Any],
    golden_dir: Path,
    side: str,
    forty_five: str,
    surface: str | None,
    lighting: str | None,
    fps: float | None = None,
    height_cm: float | None = None,
) -> dict[str, Any]:
    missing = [n for n, v in (("surface", surface), ("lighting", lighting)) if not v]
    if missing:
        raise AddClipError(f"record {', '.join(missing)} from the intake form")
    cam_side, (athlete, position, movement, _, date) = _camera(golden_dir, side, ("side",), fps)
    cam_45, other = _camera(golden_dir, forty_five, ("45", "fortyfive"), fps)
    if (other[0], other[1], other[2], other[4]) != (athlete, position, movement, date):
        raise AddClipError(f"{side} and {forty_five} are not the same athlete / position / movement / date")
    clips = manifest.get("clips", [])
    used = {c.get(k, {}).get("path") for c in clips for k in ("camera_side", "camera_45") if c.get(k)}
    if cam_side["path"] in used or cam_45["path"] in used:
        raise AddClipError("this film is already in the manifest")
    ids = [int(c["clip_id"][4:]) for c in clips if str(c.get("clip_id", "")).startswith("clp_")]
    return {
        "clip_id": f"clp_{max(ids, default=0) + 1:04d}",
        "athlete_id": athlete,
        "position_target": position,
        "movement": movement,
        "surface": surface,
        "lighting": lighting,
        "athlete_height_cm": height_cm,
        "camera_side": cam_side,
        "camera_45": cam_45,
        "disputed": False,
        "labels": {},
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="python -m services.golden_set.add_clip", description=__doc__.split("\n")[0])
    ap.add_argument("--side", required=True, help="side-angle file name in clips/")
    ap.add_argument("--45", dest="forty_five", required=True, help="45-degree file name in clips/")
    ap.add_argument("--surface", help="turf | grass | track")
    ap.add_argument("--lighting", help="daylight | night_lit | indoor")
    ap.add_argument("--fps", type=float)
    ap.add_argument("--height-cm", type=float)
    ap.add_argument("--golden-dir", type=Path, default=GOLDEN_DIR)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)

    path = args.golden_dir / "manifest.json"
    manifest = json.loads(path.read_text())
    try:
        clip = build_clip(
            manifest, args.golden_dir, args.side, args.forty_five,
            args.surface, args.lighting, args.fps, args.height_cm,
        )
        new = {**manifest, "clips": [*manifest.get("clips", []), clip]}
        model = GoldenManifest.model_validate(new)
        problems = [p for c in model.clips for p in film_problems(c)]
        if problems:
            raise AddClipError("; ".join(problems))
    except ValidationError as exc:
        print("\n".join(f"refused: {e['msg']} ({'.'.join(map(str, e['loc']))})" for e in exc.errors()), file=sys.stderr)
        return 1
    except AddClipError as exc:
        print(f"refused: {exc}", file=sys.stderr)
        return 1
    if args.dry_run:
        print(json.dumps(clip, indent=2))
        return 0
    path.write_text(json.dumps(new, indent=2) + "\n")
    print(f"added {clip['clip_id']} ({clip['athlete_id']} {clip['position_target']} {clip['movement']}) to {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
