"""Honesty pin: film-first ops docs and drill seeds publish no NIL or MAE.

Capture/labeling copy may name protocol targets (inter-rater agreement).
It must not publish a dollar, a numeric percentile, a numeric MAE, or a
measured calibration error. Drill seeds stay cue language only.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILM_DOCS = (
    ROOT / "docs" / "film_first" / "assignments_sheet.md",
    ROOT / "docs" / "film_first" / "bag_checklist.md",
    ROOT / "docs" / "film_first" / "capture_guide.md",
    ROOT / "docs" / "film_first" / "labeling_protocol.md",
    ROOT / "docs" / "film_first" / "retake_templates.md",
    ROOT / "docs" / "film_first" / "schedule.md",
    ROOT / "docs" / "film_first" / "session_1.md",
)
SEEDS = (
    ROOT / "data" / "samples" / "drills.json",
    ROOT / "data" / "samples" / "position_templates.json",
)

_DOLLAR = re.compile(r"\$\s*\d")
_PERCENTILE = re.compile(r"\b(p25|p50|p75)\b\s*[:=]\s*\d", re.IGNORECASE)
_MAE = re.compile(r"\bMAE\b\s*[:=]?\s*\d", re.IGNORECASE)
_ERROR = re.compile(r"\berror_yd\b\s*[:=]\s*\d", re.IGNORECASE)


def test_film_ops_and_drill_seeds_publish_no_nil_or_mae() -> None:
    offenders: list[str] = []
    for path in FILM_DOCS + SEEDS:
        assert path.is_file(), path
        text = path.read_text()
        if _DOLLAR.search(text):
            offenders.append(f"{path.relative_to(ROOT)}:dollar")
        if _PERCENTILE.search(text):
            offenders.append(f"{path.relative_to(ROOT)}:percentile")
        if _MAE.search(text):
            offenders.append(f"{path.relative_to(ROOT)}:mae")
        if _ERROR.search(text):
            offenders.append(f"{path.relative_to(ROOT)}:error_yd")
    assert offenders == []


def test_session_one_forbids_nil_copy_and_slice_3() -> None:
    text = (ROOT / "docs" / "film_first" / "session_1.md").read_text()
    assert "No Slice 3" in text
    assert "Do not draft NIL band copy." in text
    assert "wr_labeled + db_labeled" in text


def test_drill_seeds_are_cues_not_valuation() -> None:
    drills = json.loads((ROOT / "data" / "samples" / "drills.json").read_text())
    assert drills, "drill seed must not be empty"
    for drill in drills:
        assert "nil" not in json.dumps(drill).lower()
        assert "value" not in drill
        assert drill.get("cue_language")
        assert "evidence_chunk_ids" in drill
    unreviewed = [d for d in drills if d.get("coach_reviewed") is False]
    assert unreviewed, "an unreviewed draft must stay in the seed"
    assert all(d["evidence_chunk_ids"] == [] for d in unreviewed)
