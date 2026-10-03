"""Honesty pin: audit notes may quote the old invented NIL band only as a closed defect.

docs/audit/baseline.md records the pre-repair hard-coded band. docs/audit/post_repair.md
must keep the repaired state (blocked_on_golden_set, numbers null). docs/audit/open_questions.md
must keep the null-band question. None of these files may add a new dollar amount,
numeric percentile, or MAE.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "docs" / "audit"
BASELINE = AUDIT / "baseline.md"
POST = AUDIT / "post_repair.md"
OPEN = AUDIT / "open_questions.md"

# Closed defect quoted in the 2026-09-25 audit. Not a live band.
_CLOSED_DEFECT = frozenset({"2500", "6000", "14000"})
_DOLLAR = re.compile(r"\$\s*(\d+)")
_ASSIGNED = re.compile(r"\b(p25|p50|p75)\b\s*[:=]\s*(\d+)", re.IGNORECASE)
_MAE = re.compile(r"\bMAE\b\s*[:=]?\s*\d", re.IGNORECASE)


def test_audit_files_exist() -> None:
    for path in (BASELINE, POST, OPEN):
        assert path.is_file(), path


def test_baseline_records_invented_band_as_a_defect() -> None:
    text = BASELINE.read_text()
    assert "p25=2500, p50=6000, p75=14000" in text
    assert "hard-coded numbers, no comp data behind them" in text
    assert "blocked_on_golden_set" in text


def test_post_repair_keeps_nil_band_null() -> None:
    text = POST.read_text()
    assert "p25/p50/p75 = 2500/6000/14000, confidence 0.41 (invented)" in text
    assert "`blocked_on_golden_set`, all numbers `null`" in text
    assert "No validation numbers were fabricated in this pass." in text
    assert "No composite metric added." in text


def test_open_questions_keeps_nil_bands_null() -> None:
    text = OPEN.read_text()
    assert "NIL bands: p25/p50/p75 are `null`" in text
    assert "No comp dataset exists." in text
    assert "blocked_on_golden_set" in text


def test_audit_docs_add_no_new_dollars_percentiles_or_mae() -> None:
    offenders: list[str] = []
    for path in (BASELINE, POST, OPEN):
        text = path.read_text()
        for match in _DOLLAR.finditer(text):
            if match.group(1) not in _CLOSED_DEFECT:
                offenders.append(f"{path.name}:dollar:{match.group(0)}")
        for match in _ASSIGNED.finditer(text):
            if match.group(2) not in _CLOSED_DEFECT:
                offenders.append(f"{path.name}:percentile:{match.group(0)}")
        if _MAE.search(text):
            offenders.append(f"{path.name}:mae")
    assert offenders == []
