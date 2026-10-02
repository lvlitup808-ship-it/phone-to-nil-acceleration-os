"""Honesty pin: product and validation docs must not publish NIL dollars or MAE.

docs/ml.md may name unmet acceptance targets (ICC, capture rate). It must not
report those as measured. Validation notes stay pending: no error_yd number,
no numeric MAE, no dollar band.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = (
    ROOT / "docs" / "ml.md",
    ROOT / "docs" / "product.md",
    ROOT / "docs" / "architecture.md",
    ROOT / "docs" / "validation" / "calibration_v1.md",
    ROOT / "docs" / "validation" / "session_1_report.md",
    ROOT / "docs" / "validation" / "slice2_report.md",
    ROOT / "docs" / "product" / "d21_d35.md",
    ROOT / "docs" / "product" / "cue_freeze_v1.md",
    ROOT / "docs" / "copy" / "athlete_facing_review.md",
)

_DOLLAR = re.compile(r"\$\s*\d")
_PERCENTILE = re.compile(r"\b(p25|p50|p75)\b\s*[:=]\s*\d", re.IGNORECASE)
_MAE = re.compile(r"\bMAE\b\s*[:=]?\s*\d", re.IGNORECASE)
_ERROR = re.compile(r"\berror_yd\b\s*[:=]\s*\d", re.IGNORECASE)
_MEASURED_ICC = re.compile(r"\bmeasured ICC\b|\bICC\s*[:=]\s*0\.\d+", re.IGNORECASE)


def test_product_and_validation_docs_publish_no_nil_or_mae() -> None:
    offenders: list[str] = []
    for path in DOCS:
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
        if _MEASURED_ICC.search(text):
            offenders.append(f"{path.relative_to(ROOT)}:measured-icc")
    assert offenders == []


def test_ml_targets_are_unmet_gates_not_results() -> None:
    text = (ROOT / "docs" / "ml.md").read_text()
    assert "ICC > 0.8 before a KPI ships" in text
    assert "Capture success rate > 85% after quality gate" in text
    assert "measured" not in text.lower()


def test_calibration_benchmark_stays_pending() -> None:
    text = (ROOT / "docs" / "validation" / "calibration_v1.md").read_text()
    lowered = text.lower()
    assert "pending" in lowered
    assert "No error_yd published" in text
    assert _ERROR.search(text) is None
    assert _DOLLAR.search(text) is None
