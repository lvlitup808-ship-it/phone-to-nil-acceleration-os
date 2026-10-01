"""Honesty: Fit Hub marketing copy must not publish an NIL point estimate.

The golden-set gate is closed. Fit Hub may say the band is not made up.
It must not print a dollar amount, a p25/p50/p75 assignment, MAE, or a composite.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "apps" / "fit-hub" / "src"
APP = SRC / "App.tsx"
FILM = SRC / "film.ts"

_DOLLAR = re.compile(r"\$\s*\d")
_PERCENTILE = re.compile(r"\b(p25|p50|p75)\b\s*[:=]\s*\d", re.IGNORECASE)
_MAE = re.compile(r"\bMAE\b\s*[:=]\s*\d", re.IGNORECASE)


def test_fit_hub_refuses_made_up_nil_band() -> None:
    text = APP.read_text()
    assert "NO MADE-UP NIL BAND" in text
    lowered = text.lower()
    assert "your nil" not in lowered
    assert "nil band is" not in lowered
    assert _DOLLAR.search(text) is None
    assert _PERCENTILE.search(text) is None
    assert _MAE.search(text) is None
    assert "composite score" not in lowered or "no composite" in lowered
    film = FILM.read_text()
    assert "NIL bands stay null" in film
    assert "no p50" in film.lower()


def test_fit_hub_src_has_no_hardcoded_nil_numbers() -> None:
    offenders: list[str] = []
    for path in SRC.rglob("*"):
        if path.suffix not in {".tsx", ".ts", ".jsx", ".js"}:
            continue
        text = path.read_text()
        if _DOLLAR.search(text) or _PERCENTILE.search(text) or _MAE.search(text):
            offenders.append(str(path.relative_to(ROOT)))
    assert offenders == []
