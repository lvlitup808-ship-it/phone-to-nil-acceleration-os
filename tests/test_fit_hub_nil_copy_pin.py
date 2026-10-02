"""Honesty: FIT HUB marketing copy must not publish an NIL point estimate.

The golden-set gate is closed and band numerics are null. FIT HUB is a
demo film site. It may refuse a made-up band. It must not print a dollar
amount, a p25/p50/p75 numeric, MAE, or a composite score.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "apps" / "fit-hub" / "src"

_DOLLAR = re.compile(r"\$\s*\d")
_PERCENTILE = re.compile(r"\b(p25|p50|p75)\b\s*[:=]\s*\d", re.IGNORECASE)
_MAE = re.compile(r"\bMAE\b\s*[:=]\s*\d", re.IGNORECASE)


def test_fit_hub_refuses_made_up_nil_band() -> None:
    text = (SRC / "App.tsx").read_text()
    assert "NO MADE-UP NIL BAND" in text
    assert "NO COMPOSITE" in text
    assert _DOLLAR.search(text) is None
    assert _PERCENTILE.search(text) is None
    assert _MAE.search(text) is None


def test_fit_hub_src_has_no_hardcoded_nil_numbers() -> None:
    offenders: list[str] = []
    for path in SRC.rglob("*"):
        if path.suffix not in {".tsx", ".ts", ".jsx", ".js"}:
            continue
        text = path.read_text()
        if _DOLLAR.search(text) or _PERCENTILE.search(text) or _MAE.search(text):
            offenders.append(str(path.relative_to(ROOT)))
        if "your nil is" in text.lower():
            offenders.append(str(path.relative_to(ROOT)))
    assert offenders == []
