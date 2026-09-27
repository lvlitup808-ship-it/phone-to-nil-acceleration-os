"""Validate data/golden_set/manifest.json.

    python -m services.golden_set.manifest            # exit 1 on any problem
    python -m services.golden_set.manifest path.json
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from pydantic import ValidationError

from packages.shared.golden import GoldenManifest, ManifestClip
from services.cv_worker.ingest.naming import PATTERN

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "data/golden_set/manifest.json"


def film_problems(clip: ManifestClip) -> list[str]:
    """A camera marked present must be a contract-named file in clips/ that matches the clip."""
    problems = []
    for key in ("camera_side", "camera_45"):
        cam = getattr(clip, key)
        if cam is None or not cam.present:
            continue
        where = f"{clip.clip_id}.{key}"
        parent, _, name = cam.path.rpartition("/")
        if parent != "clips":
            problems.append(f"{where}: path must be clips/<file>, got {cam.path!r}")
            continue
        m = PATTERN.match(name)
        if m is None:
            problems.append(f"{where}: {name!r} does not follow the naming contract "
                            "<athlete_id>_<position>_<movement>_<angle>_<date>.mp4")
            continue
        athlete, position, movement, angle, _ = m.groups()
        want_angle = "side" if key == "camera_side" else ("45", "fortyfive")
        if (athlete, position, movement) != (clip.athlete_id, clip.position_target, clip.movement) or (
            angle not in want_angle
        ):
            problems.append(f"{where}: {name!r} does not match athlete_id / position / movement / angle")
    return problems


def check(path: Path = MANIFEST) -> tuple[bool, list[str]]:
    try:
        data = json.loads(path.read_text())
    except (OSError, ValueError) as exc:
        return False, [f"{path}: cannot read: {exc}"]
    try:
        manifest = GoldenManifest.model_validate(data)
    except ValidationError as exc:
        lines = []
        for err in exc.errors():
            loc = ".".join(str(p) for p in err["loc"])
            lines.append(f"{path}: {loc}: {err['msg']}" if loc else f"{path}: {err['msg']}")
        return False, lines
    problems = [f"{path}: {p}" for clip in manifest.clips for p in film_problems(clip)]
    if problems:
        return False, problems
    filmed = sum(
        1 for c in manifest.clips if any(cam and cam.present for cam in (c.camera_side, c.camera_45))
    )
    return True, [f"{path}: ok ({len(manifest.clips)} clips, {filmed} with film present)"]


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    ok, lines = check(Path(args[0]) if args else MANIFEST)
    print("\n".join(lines))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
