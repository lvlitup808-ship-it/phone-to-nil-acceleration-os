"""Honesty pin: contributor instructions must not publish a NIL band.

CONTRIBUTING.md is the first doc a new change sees. It may require a
disclaimer. It must state the live contract: p25/p50/p75 stay null until
the golden-set gate opens. It must not print a dollar, numeric percentile,
MAE, or composite.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRIBUTING = ROOT / "CONTRIBUTING.md"

_DOLLAR = re.compile(r"\$\s*\d")
_PERCENTILE = re.compile(r"\b(p25|p50|p75)\b\s*[:=]\s*\d", re.IGNORECASE)
_MAE = re.compile(r"\bMAE\b\s*[:=]?\s*\d", re.IGNORECASE)


def test_contributing_states_null_band_contract() -> None:
    text = CONTRIBUTING.read_text()
    lowered = text.lower()
    assert "p25/p50/p75 stay null" in text
    assert "golden-set gate" in lowered
    assert "do not invent" in lowered
    assert "mae" in lowered
    assert "composite" in lowered
    assert "athlete video" in lowered


def test_contributing_publishes_no_nil_numbers() -> None:
    text = CONTRIBUTING.read_text()
    assert _DOLLAR.search(text) is None
    assert _PERCENTILE.search(text) is None
    assert _MAE.search(text) is None
    assert "your nil is" not in text.lower()
