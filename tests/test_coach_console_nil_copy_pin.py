"""Honesty: coach-console home must not publish an NIL point estimate.

The golden-set gate is closed and band numerics are null. The roster
page is allowed to say not to publish estimates. It must not print a
dollar amount, a p25/p50/p75, MAE, or a composite.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "apps" / "coach-console" / "app" / "page.tsx"
APP = ROOT / "apps" / "coach-console" / "app"

_DOLLAR = re.compile(r"\$\s*\d")
_PERCENTILE = re.compile(r"\b(p25|p50|p75)\b\s*[:=]\s*\d", re.IGNORECASE)
_MAE = re.compile(r"\bMAE\b\s*[:=]\s*\d", re.IGNORECASE)


def test_coach_console_home_refuses_nil_point_estimates() -> None:
    text = PAGE.read_text()
    assert "Do not publish NIL point estimates." in text
    lowered = text.lower()
    assert "your nil" not in lowered
    assert "nil band is" not in lowered
    assert _DOLLAR.search(text) is None
    assert _PERCENTILE.search(text) is None
    assert _MAE.search(text) is None
    assert "composite" not in lowered


def test_coach_console_app_has_no_hardcoded_nil_numbers() -> None:
    offenders: list[str] = []
    for path in APP.rglob("*"):
        if path.suffix not in {".tsx", ".ts", ".jsx", ".js"}:
            continue
        text = path.read_text()
        if _DOLLAR.search(text) or _PERCENTILE.search(text) or _MAE.search(text):
            offenders.append(str(path.relative_to(ROOT)))
    assert offenders == []
