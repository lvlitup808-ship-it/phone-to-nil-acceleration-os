"""JSON Schemas in data/schemas/ generated from the pydantic models the API emits.

    python -m packages.shared.schemas          # check for drift (exit 1 on drift)
    python -m packages.shared.schemas --write  # regenerate
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from pydantic import BaseModel

from packages.shared.models import ClipQuality, Cue, NILBand
from packages.shared.slice2 import Slice2Assessment, Slice2Cue

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_DIR = ROOT / "data/schemas"
MODELS: dict[str, type[BaseModel]] = {
    "slice1_cue.schema.json": Cue,
    "clip_quality.schema.json": ClipQuality,
    "nil_band.schema.json": NILBand,
    "slice2_cue.schema.json": Slice2Cue,
    "slice2_assessment.schema.json": Slice2Assessment,
}


def render(model: type[BaseModel]) -> str:
    return json.dumps(model.model_json_schema(), indent=2, sort_keys=True) + "\n"


def drift() -> list[str]:
    return [name for name, model in MODELS.items()
            if not (SCHEMA_DIR / name).is_file() or (SCHEMA_DIR / name).read_text() != render(model)]


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if "--write" in args:
        for name, model in MODELS.items():
            (SCHEMA_DIR / name).write_text(render(model))
        return 0
    stale = drift()
    for name in stale:
        print(f"schema drift: data/schemas/{name}")
    return 1 if stale else 0


if __name__ == "__main__":
    raise SystemExit(main())
