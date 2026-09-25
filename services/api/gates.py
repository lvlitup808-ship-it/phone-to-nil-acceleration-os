from __future__ import annotations

from typing import Any

GOLDEN_SET_GATE = {
    "wr_labeled_min": 10,
    "db_labeled_min": 10,
    "inter_rater_done": True,
    "disputed_max": 2,
}


def get_progress() -> dict[str, Any]:
    return {
        "wr_labeled": 0,
        "db_labeled": 0,
        "inter_rater_done": False,
        "disputed": 0,
    }


def prescription_enabled(progress: dict[str, Any] | None = None) -> bool:
    p = progress or get_progress()
    return (
        p["wr_labeled"] >= GOLDEN_SET_GATE["wr_labeled_min"]
        and p["db_labeled"] >= GOLDEN_SET_GATE["db_labeled_min"]
        and p["inter_rater_done"]
        and p["disputed"] <= GOLDEN_SET_GATE["disputed_max"]
    )


def blocked_reason(progress: dict[str, Any] | None = None) -> dict[str, Any]:
    p = progress or get_progress()
    missing = []
    if p["wr_labeled"] < GOLDEN_SET_GATE["wr_labeled_min"]:
        missing.append(f"wr_labeled {p['wr_labeled']}/10")
    if p["db_labeled"] < GOLDEN_SET_GATE["db_labeled_min"]:
        missing.append(f"db_labeled {p['db_labeled']}/10")
    if not p["inter_rater_done"]:
        missing.append("inter_rater")
    if p["disputed"] > GOLDEN_SET_GATE["disputed_max"]:
        missing.append(f"disputed {p['disputed']}")
    return {"status": "blocked_on_golden_set", "missing": missing, "progress": p}
