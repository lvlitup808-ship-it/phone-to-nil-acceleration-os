"""Honesty pin: architecture map and build prompt are not a NIL band.

docs/architecture.md names the valuation layer. PROMPT.md is the repo contract.
Neither may print a dollar amount, a numeric percentile, MAE, or a composite.
The live contract stays null until the golden-set gate opens on real labeled film.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = (
    ROOT / "docs" / "architecture.md",
    ROOT / "PROMPT.md",
)

_DOLLAR = re.compile(r"\$\s*\d")
_PERCENTILE = re.compile(r"\b(p25|p50|p75)\b\s*[:=]\s*\d", re.IGNORECASE)
_MAE = re.compile(r"\bMAE\b\s*[:=]?\s*\d", re.IGNORECASE)
_COMPOSITE = re.compile(r"\bcomposite\s*[:=]\s*\d", re.IGNORECASE)
_LIVE_CONTRACT = "Live contract: NIL p25/p50/p75 are null."


def test_architecture_and_prompt_publish_no_nil_numbers() -> None:
    offenders: list[str] = []
    missing: list[str] = []
    for path in DOCS:
        assert path.is_file(), path
        text = path.read_text()
        rel = str(path.relative_to(ROOT))
        if _LIVE_CONTRACT not in text:
            missing.append(rel)
        if _DOLLAR.search(text):
            offenders.append(f"{rel}:dollar")
        if _PERCENTILE.search(text):
            offenders.append(f"{rel}:percentile")
        if _MAE.search(text):
            offenders.append(f"{rel}:mae")
        if _COMPOSITE.search(text):
            offenders.append(f"{rel}:composite")
    assert missing == [], missing
    assert offenders == [], offenders


def test_architecture_keeps_valuation_as_ranges_only() -> None:
    text = (ROOT / "docs" / "architecture.md").read_text()
    assert "Valuation — ranges only" in text
    assert "This file is not a band." in text
    assert "Slice 3" not in text
    prompt = (ROOT / "PROMPT.md").read_text()
    assert "Do not invent dollars, percentiles, MAE, or a composite." in prompt
