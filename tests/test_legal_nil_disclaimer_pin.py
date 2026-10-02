"""Honesty: legal NIL copy must not publish a point estimate.

docs/legal is the athlete-facing disclaimer. While the golden-set gate is
closed, these files may say bands are informational and not an offer. They
must not print a dollar amount, a numeric p25/p50/p75, MAE, or a composite.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEGAL = ROOT / "docs" / "legal"
DISCLAIMER = LEGAL / "nil-disclaimer.md"

_DOLLAR = re.compile(r"\$\s*\d")
_PERCENTILE = re.compile(r"\b(p25|p50|p75)\b\s*[:=]\s*\d", re.IGNORECASE)
_MAE = re.compile(r"\bMAE\b\s*[:=]\s*\d", re.IGNORECASE)


def test_nil_disclaimer_is_not_an_offer_and_has_no_numbers() -> None:
    text = DISCLAIMER.read_text()
    lowered = text.lower()
    assert "not a contract offer" in lowered
    assert "disclaimer_version" in text
    assert "informational" in lowered
    assert _DOLLAR.search(text) is None
    assert _PERCENTILE.search(text) is None
    assert _MAE.search(text) is None
    assert "composite" not in lowered


def test_legal_docs_have_no_hardcoded_nil_numbers() -> None:
    offenders: list[str] = []
    for path in sorted(LEGAL.glob("*.md")):
        text = path.read_text()
        if _DOLLAR.search(text) or _PERCENTILE.search(text) or _MAE.search(text):
            offenders.append(str(path.relative_to(ROOT)))
        if "your nil is" in text.lower():
            offenders.append(str(path.relative_to(ROOT)))
    assert offenders == []
