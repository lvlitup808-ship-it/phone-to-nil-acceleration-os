"""Golden-set gate.

Prescription, passport and NIL content stay blocked until the golden set is real:
10 WR + 10 DB coach-labeled clips of real film, inter-rater done, few disputes,
and the diversity mix in docs/film_first.md (3 surfaces, 2 lighting, 3 athletes
per position).

Progress is derived from data/golden_set/: a label counts only when its clip is
in the manifest, at least one camera file for that clip exists on disk, the
label is neither excluded nor disputed, and it has the five events and six
frozen cues for the clip's movement. A stub file is not a coach label. A labels file that is not a JSON object
is skipped, not counted, and must not crash the gate.
Fixture entries (no film) never count. camera present must be JSON true; 1 and "true" are not film. Coach, athlete, surface, and lighting
ids are compared case-insensitively so spelling variants cannot inflate progress.
When the manifest declares labeling_protocol_version, a label counts only if it
carries that same stamp. A missing or other protocol is not a coach label.
Only WR and DB clips count toward labeled totals, inter-rater, and the
surface / lighting mix. An RB, OL, or other position cannot fill those bars.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from services.golden_set.labels import CUES, EVENTS

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


def _norm_token(raw: Any) -> str:
    """Strip and casefold a string id. Non-strings are not identities."""
    if not isinstance(raw, str):
        return ""
    return raw.strip().casefold()


def _load_json(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text())
    except (OSError, ValueError):
        return None


def has_film(clip: dict[str, Any], root: Path) -> bool:
    for key in ("camera_side", "camera_45"):
        cam = clip.get(key) or {}
        # Only JSON true counts. 1 and "true" are hand-edited lies, not film.
        if cam.get("present") is not True or not cam.get("path"):
            continue
        path = (root / cam["path"]).resolve()
        if path.is_relative_to(root.resolve()) and path.is_file():
            return True
    return False


def _event_stamped(event: Any) -> bool:
    if not isinstance(event, dict):
        return False
    t_ms = event.get("t_ms")
    return isinstance(t_ms, int) and not isinstance(t_ms, bool) and t_ms >= 0


def _cue_answered(cue: Any) -> bool:
    """A counted cue has a number, or is explicitly disputed. Empty objects are stubs."""
    if not isinstance(cue, dict):
        return False
    if cue.get("disputed") is True:
        return True
    value = cue.get("value")
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _complete_label(label: dict[str, Any], clip: dict[str, Any]) -> bool:
    """A gate-counting label has the movement's events and frozen cues.

    POST /golden/labels already rejects incomplete saves. Hand-written files
    under labels/ must not open the gate by skipping that check. Event names
    without t_ms, and cue names without a value or disputed flag, do not count.
    """
    movement = clip.get("movement")
    if movement not in EVENTS:
        return False
    events = label.get("events")
    cues = label.get("cues")
    if not isinstance(events, dict) or set(events) != set(EVENTS[movement]):
        return False
    if not isinstance(cues, dict) or set(cues) != set(CUES[movement]):
        return False
    if not all(_event_stamped(events[name]) for name in EVENTS[movement]):
        return False
    return all(_cue_answered(cues[name]) for name in CUES[movement])



def _protocol_ok(label: dict[str, Any], manifest: dict[str, Any]) -> bool:
    """Count a label only under the protocol the manifest declares.

    POST /golden/labels stamps labeling_protocol_version. Hand-written files
    that omit the stamp, or name another protocol, must not open the gate.
    A manifest with no protocol declared does not add this check.
    """
    expected = manifest.get("labeling_protocol_version")
    if not isinstance(expected, str) or not expected.strip():
        return True
    got = label.get("labeling_protocol_version")
    if not isinstance(got, str):
        return False
    return got.strip() == expected.strip()


def get_progress(golden_dir: Path = GOLDEN_DIR) -> dict[str, Any]:
    manifest = _load_json(golden_dir / "manifest.json") or {}
    clips = {c["clip_id"]: c for c in manifest.get("clips", []) if "clip_id" in c}
    filmed = {cid: c for cid, c in clips.items() if has_film(c, golden_dir)}

    coaches: dict[str, set[str]] = {}
    disputed: set[str] = set()
    labels_dir = golden_dir / "labels"
    for path in sorted(labels_dir.glob("*.json")) if labels_dir.is_dir() else []:
        if path.name.startswith("_"):
            continue
        label = _load_json(path)
        if not isinstance(label, dict):
            continue
        cid = str(label.get("clip_id", ""))
        coach = _norm_token(label.get("coach_id"))
        if cid not in filmed or label.get("excluded") or not coach:
            continue
        if not _complete_label(label, filmed[cid]):
            continue
        if not _protocol_ok(label, manifest):
            continue
        if label.get("disputed") or filmed[cid].get("disputed"):
            disputed.add(cid)
            continue
        coaches.setdefault(cid, set()).add(coach)

    labeled = [filmed[cid] for cid in coaches if cid not in disputed]
    wr = [c for c in labeled if c.get("position_target") == "WR"]
    db = [c for c in labeled if c.get("position_target") == "DB"]
    counted = wr + db
    overlap = sum(
        1
        for cid, who in coaches.items()
        if cid not in disputed
        and len(who) >= 2
        and filmed[cid].get("position_target") in ("WR", "DB")
    )

    def distinct(rows: list[dict[str, Any]], key: str) -> int:
        values: set[Any] = set()
        for row in rows:
            raw = row.get(key)
            if isinstance(raw, str):
                raw = _norm_token(raw)
            if raw:
                values.add(raw)
        return len(values)

    return {
        "wr_labeled": len(wr),
        "db_labeled": len(db),
        "inter_rater_done": overlap >= GOLDEN_SET_GATE["inter_rater_clips_min"],
        "disputed": len(disputed),
        "inter_rater_clips": overlap,
        "surfaces": distinct(counted, "surface"),
        "lighting_conditions": distinct(counted, "lighting"),
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
