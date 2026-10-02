"""Honesty: nil_quantile_v0 model card must not publish a point estimate.

models/model_cards/nil_quantile_v0.md is the valuation card. While no comp
dataset exists, it must stay schema_only with null quantiles. It must not
print a dollar amount, a numeric p25/p50/p75, MAE, or claim a fitted model.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CARD = ROOT / "models" / "model_cards" / "nil_quantile_v0.md"

_DOLLAR = re.compile(r"\$\s*\d")
_PERCENTILE = re.compile(r"\b(p25|p50|p75)\b\s*[:=]\s*\d", re.IGNORECASE)
_MAE = re.compile(r"\bMAE\b\s*[:=]\s*\d", re.IGNORECASE)


def test_nil_quantile_card_is_schema_only_and_null() -> None:
    text = CARD.read_text()
    lowered = text.lower()
    assert "schema_only" in text
    assert "null" in lowered
    assert "no model exists yet" in lowered
    assert "no comp" in lowered
    assert _DOLLAR.search(text) is None
    assert _PERCENTILE.search(text) is None
    assert _MAE.search(text) is None
    assert "composite" not in lowered


def test_model_cards_have_no_hardcoded_nil_numbers() -> None:
    offenders: list[str] = []
    cards = ROOT / "models" / "model_cards"
    for path in sorted(cards.glob("*.md")):
        text = path.read_text()
        if _DOLLAR.search(text) or _PERCENTILE.search(text) or _MAE.search(text):
            offenders.append(str(path.relative_to(ROOT)))
        if "your nil is" in text.lower():
            offenders.append(str(path.relative_to(ROOT)))
    assert offenders == []
