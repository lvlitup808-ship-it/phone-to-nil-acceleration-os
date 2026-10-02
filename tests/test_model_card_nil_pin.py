"""Honesty: model cards must not publish NIL dollars, MAE, or met validation.

`models/model_cards/` and `docs/models/` describe adapters that are not
validated on coach-labeled film. They may name intended fields (p25/p50/p75)
and an unmet target. They must not print a dollar amount, a numeric percentile,
a numeric MAE, or claim the golden-set gate is open.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CARD_DIRS = (ROOT / "models" / "model_cards", ROOT / "docs" / "models")

_DOLLAR = re.compile(r"\$\s*\d")
_PERCENTILE = re.compile(r"\b(p25|p50|p75)\b\s*[:=]\s*\d", re.IGNORECASE)
_MAE = re.compile(r"\bMAE\b\s*[:=]\s*\d", re.IGNORECASE)
_GATE_OPEN = re.compile(r"golden[- ]set gate is open", re.IGNORECASE)


def _cards() -> list[Path]:
    found: list[Path] = []
    for directory in CARD_DIRS:
        found.extend(sorted(directory.glob("*.md")))
    assert found, "model cards missing"
    return found


def test_nil_quantile_card_stays_schema_only() -> None:
    text = (ROOT / "models" / "model_cards" / "nil_quantile_v0.md").read_text()
    lowered = text.lower()
    assert "schema_only" in text
    assert "null" in lowered
    assert "no comp" in lowered
    assert "blocked_on_golden_set" in text
    assert _DOLLAR.search(text) is None
    assert _PERCENTILE.search(text) is None
    assert _MAE.search(text) is None


def test_model_cards_do_not_publish_nil_or_mae() -> None:
    offenders: list[str] = []
    for path in _cards():
        text = path.read_text()
        if _DOLLAR.search(text) or _PERCENTILE.search(text) or _MAE.search(text):
            offenders.append(str(path.relative_to(ROOT)))
        if _GATE_OPEN.search(text):
            offenders.append(f"{path.relative_to(ROOT)}:gate-open")
        if re.search(r"\bICC\b\s*[:=]\s*0\.\d+", text):
            offenders.append(f"{path.relative_to(ROOT)}:measured-icc")
    assert offenders == []
