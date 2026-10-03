"""Honesty pin: audit notes may record the old invented band, never as live.

docs/audit/baseline.md captured p25=2500 / p50=6000 / p75=14000 before the
repair. Those figures are a defect snapshot. They are not a NIL band, a
composite, or an MAE. The live contract stays null until the golden-set gate
opens on real labeled film.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "docs" / "audit"
DOCS = (
    AUDIT / "baseline.md",
    AUDIT / "post_repair.md",
    AUDIT / "open_questions.md",
)

_DOLLAR = re.compile(r"\$\s*\d")
_INVENTED_BAND = re.compile(r"p25\s*=\s*2500|2500/6000/14000")
_LIVE_CONTRACT = "Live contract: NIL p25/p50/p75 are null. This file is not a band."


def test_audit_docs_are_not_a_live_nil_band() -> None:
    missing: list[str] = []
    dollars: list[str] = []
    for path in DOCS:
        assert path.is_file(), path
        text = path.read_text()
        if _LIVE_CONTRACT not in text:
            missing.append(str(path.relative_to(ROOT)))
        if _DOLLAR.search(text):
            dollars.append(str(path.relative_to(ROOT)))
    assert missing == [], missing
    assert dollars == [], dollars


def test_invented_band_only_appears_as_a_recorded_defect() -> None:
    hits: list[str] = []
    for path in DOCS:
        for i, line in enumerate(path.read_text().splitlines(), 1):
            if not _INVENTED_BAND.search(line):
                continue
            lowered = line.lower()
            if "hard-coded" not in lowered and "invented" not in lowered:
                hits.append(f"{path.relative_to(ROOT)}:{i}:{line.strip()}")
    assert hits == [], hits


def test_post_repair_records_null_band_and_questions_stay_blocked() -> None:
    repair = (AUDIT / "post_repair.md").read_text()
    assert "`blocked_on_golden_set`, all numbers `null`" in repair
    assert "No validation numbers were fabricated in this pass." in repair
    questions = (AUDIT / "open_questions.md").read_text()
    assert "no accuracy claim allowed" in questions
    assert "Any NIL number" in questions
    assert "p25/p50/p75 are `null`" in questions
