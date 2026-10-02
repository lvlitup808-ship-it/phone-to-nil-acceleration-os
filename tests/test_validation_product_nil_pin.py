"""Honesty: validation and product docs must not publish a point estimate.

docs/validation is the harness output. docs/product.md and docs/ml.md describe
the band. While the golden-set gate is closed they may name the loop and the
acceptance thresholds. They must not print a dollar amount, a numeric
p25/p50/p75, a published MAE, or a composite score.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATION = ROOT / "docs" / "validation"
PRODUCT = ROOT / "docs" / "product.md"
ML = ROOT / "docs" / "ml.md"
SLICE2 = VALIDATION / "slice2_report.md"

_DOLLAR = re.compile(r"\$\s*\d")
_PERCENTILE = re.compile(r"\b(p25|p50|p75)\b\s*[:=]\s*\d", re.IGNORECASE)
_MAE = re.compile(r"\bMAE\b\s*[:=]\s*\d", re.IGNORECASE)


def _offenders(paths: list[Path]) -> list[str]:
    found: list[str] = []
    for path in paths:
        text = path.read_text()
        lowered = text.lower()
        if _DOLLAR.search(text) or _PERCENTILE.search(text) or _MAE.search(text):
            found.append(str(path.relative_to(ROOT)))
        if "your nil is" in lowered or "composite score" in lowered:
            found.append(str(path.relative_to(ROOT)))
    return found


def test_slice2_report_is_fixture_and_unpublished() -> None:
    text = SLICE2.read_text()
    lowered = text.lower()
    assert "golden_set: pending" in text
    assert "real_mp4_present: false" in text
    assert "not athlete film" in lowered
    assert "no athlete-film mae is published" in lowered
    assert _DOLLAR.search(text) is None
    assert _MAE.search(text) is None


def test_validation_product_ml_have_no_hardcoded_nil_numbers() -> None:
    paths = sorted(VALIDATION.glob("*.md")) + [PRODUCT, ML]
    assert _offenders(paths) == []
