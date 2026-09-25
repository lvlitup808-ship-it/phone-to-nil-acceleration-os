"""Golden-set gate.

Prescription, passport and NIL content stay blocked until the golden set is real:
10 WR + 10 DB coach-labeled clips of real film, inter-rater done, few disputes,
and the diversity mix in docs/film_first.md (3 surfaces, 2 lighting, 3 athletes
per position).

Progress is derived from data/golden_set/: a label counts only when its clip is
in the manifest, at least one camera file for that clip exists on disk, and the
label is neither excluded nor disputed. Fixture entries (no film) never count.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
GOLDEN_DIR = ROOT / "data/golden_set"

GOLDEN_SET_GATE = {
    "wr_labeled_min": 10,
    "db_labeled_min": 10,
    "inter_rater_done": True,
    "inter_rater_clips_min": 4,
    "disputed_max": 2,
    "surfaces_min": 3,
    "lighting_min": 2,
    "athletes_per_position_min": 3,
}


def _load_json(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text())
    except (OSError, ValueError):
        return None


def _has_film(clip: dict[str, Any], root: Path) -> bool:
    for key in ("camera_side", "camera_45"):
        cam = clip.get(key) or {}
        if cam.get("present") and cam.get("path") and (root / cam["path"]).is_file():
            return True
    return False


def get_progress(golden_dir: Path = GOLDEN_DIR) -> dict[str, Any]:
    manifest = _load_json(golden_dir / "manifest.json") or {}
    clips = {c["clip_id"]: c for c in manifest.get("clips", []) if "clip_id" in c}
    filmed = {cid: c for cid, c in clips.items() if _has_film(c, golden_dir)}

    coaches: dict[str, set[str]] = {}
    disputed: set[str] = set()
    labels_dir = golden_dir / "labels"
    for path in sorted(labels_dir.glob("*.json")) if labels_dir.is_dir() else []:
        if path.name.startswith("_"):
            continue
        label = _load_json(path) or {}
        cid = str(label.get("clip_id", ""))
        if cid not in filmed or label.get("excluded"):
            continue
        if label.get("disputed") or filmed[cid].get("disputed"):
            disputed.add(cid)
            continue
        coaches.setdefault(cid, set()).add(str(label.get("coach_id", "")))

    labeled = [filmed[cid] for cid in coaches if cid not in disputed]
    wr = [c for c in labeled if c.get("position_target") == "WR"]
    db = [c for c in labeled if c.get("position_target") == "DB"]
    overlap = sum(1 for cid, who in coaches.items() if cid not in disputed and len(who) >= 2)

    def distinct(rows: list[dict[str, Any]], key: str) -> int:
        return len({r[key] for r in rows if r.get(key)})

    return {
        "wr_labeled": len(wr),
        "db_labeled": len(db),
        "inter_rater_done": overlap >= GOLDEN_SET_GATE["inter_rater_clips_min"],
        "disputed": len(disputed),
        "inter_rater_clips": overlap,
        "surfaces": distinct(labeled, "surface"),
        "lighting_conditions": distinct(labeled, "lighting"),
        "wr_athletes": distinct(wr, "athlete_id"),
        "db_athletes": distinct(db, "athlete_id"),
    }


def _missing(p: dict[str, Any]) -> list[str]:
    g = GOLDEN_SET_GATE
    missing = []
    if p.get("wr_labeled", 0) < g["wr_labeled_min"]:
        missing.append(f"wr_labeled {p.get('wr_labeled', 0)}/{g['wr_labeled_min']}")
    if p.get("db_labeled", 0) < g["db_labeled_min"]:
        missing.append(f"db_labeled {p.get('db_labeled', 0)}/{g['db_labeled_min']}")
    if not p.get("inter_rater_done"):
        missing.append("inter_rater")
    if p.get("disputed", 0) > g["disputed_max"]:
        missing.append(f"disputed {p.get('disputed', 0)}")
    if p.get("surfaces", 0) < g["surfaces_min"]:
        missing.append(f"surfaces {p.get('surfaces', 0)}/{g['surfaces_min']}")
    if p.get("lighting_conditions", 0) < g["lighting_min"]:
        missing.append(f"lighting {p.get('lighting_conditions', 0)}/{g['lighting_min']}")
    for pos in ("wr", "db"):
        n = p.get(f"{pos}_athletes", 0)
        if n < g["athletes_per_position_min"]:
            missing.append(f"{pos}_athletes {n}/{g['athletes_per_position_min']}")
    return missing


def prescription_enabled(progress: dict[str, Any] | None = None) -> bool:
    p = progress if progress is not None else get_progress()
    return not _missing(p)


def blocked_reason(progress: dict[str, Any] | None = None) -> dict[str, Any]:
    p = progress if progress is not None else get_progress()
    return {"status": "blocked_on_golden_set", "missing": _missing(p), "progress": p}


def gate_state() -> dict[str, Any]:
    """Current gate as served on /gates/golden: open, or blocked with what is missing."""
    p = get_progress()
    if prescription_enabled(p):
        return {"status": "open", "missing": [], "progress": p}
    return blocked_reason(p)
