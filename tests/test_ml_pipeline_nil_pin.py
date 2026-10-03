"""Honesty pin: ML pipeline notes are not a NIL band or a measured MAE.

docs/ml.md lists notebooks and acceptance targets (ICC, capture success).
Those figures are not results. The file must not print a dollar amount,
a numeric percentile, MAE, or a composite. The live contract stays null
until the golden-set gate opens on real labeled film.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "ml.md"

_DOLLAR = re.compile(r"\$\s*\d")
_PERCENTILE = re.compile(r"\b(p25|p50|p75)\b\s*[:=]\s*\d", re.IGNORECASE)
_MAE = re.compile(r"\bMAE\b\s*[:=]?\s*\d", re.IGNORECASE)
_COMPOSITE = re.compile(r"\bcomposite\s*[:=]\s*\d", re.IGNORECASE)
_LIVE_CONTRACT = "Live contract: NIL p25/p50/p75 are null."


def test_ml_pipeline_publishes_no_nil_numbers() -> None:
    assert DOC.is_file(), DOC
    text = DOC.read_text()
    assert _LIVE_CONTRACT in text
    assert "not measured results" in text
    assert "No MAE is published." in text
    assert "This file is not a band." in text
    assert _DOLLAR.search(text) is None
    assert _PERCENTILE.search(text) is None
    assert _MAE.search(text) is None
    assert _COMPOSITE.search(text) is None


def test_ml_pipeline_keeps_thresholds_as_targets_not_results() -> None:
    text = DOC.read_text()
    assert "acceptance targets" in text
    assert "ICC > 0.8" in text
    assert "85%" in text
    assert "Slice 3" in text
    assert "golden-set gate is closed" in text
