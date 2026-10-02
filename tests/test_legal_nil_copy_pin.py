"""Honesty: legal copy must not publish an NIL dollar, percentile, or MAE.

docs/legal is what a parent or coach can be handed. The golden-set gate is
closed and band numerics are null. The disclaimer may describe the schema
(p25–p75) but must say those fields are null until a sourced comp set exists.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEGAL = ROOT / "docs" / "legal"
DISCLAIMER = LEGAL / "nil-disclaimer.md"

_DOLLAR = re.compile(r"\$\s*\d")
_PERCENTILE_VALUE = re.compile(r"\b(p25|p50|p75)\b\s*[:=]\s*\d", re.IGNORECASE)
_MAE = re.compile(r"\bMAE\b\s*[:=]\s*\d", re.IGNORECASE)
_COMPOSITE = re.compile(r"\bcomposite\s+(score|metric)\s*[:=]\s*\d", re.IGNORECASE)


def test_legal_docs_have_no_hardcoded_nil_numbers() -> None:
    offenders: list[str] = []
    for path in sorted(LEGAL.glob("*.md")):
        text = path.read_text()
        if (
            _DOLLAR.search(text)
            or _PERCENTILE_VALUE.search(text)
            or _MAE.search(text)
            or _COMPOSITE.search(text)
        ):
            offenders.append(path.name)
    assert offenders == []


def test_nil_disclaimer_says_bands_are_null_until_sourced() -> None:
    text = DISCLAIMER.read_text().lower()
    assert "not a contract offer" in text or "not a contract" in text
    assert "null" in text
    assert "golden" in text
    assert "no comp" in text or "not computed" in text or "not yet" in text
    assert _DOLLAR.search(DISCLAIMER.read_text()) is None
