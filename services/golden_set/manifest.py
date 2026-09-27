"""Validate data/golden_set/manifest.json.

    python -m services.golden_set.manifest            # exit 1 on any problem
    python -m services.golden_set.manifest path.json
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from pydantic import ValidationError

from packages.shared.golden import GoldenManifest

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "data/golden_set/manifest.json"


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
