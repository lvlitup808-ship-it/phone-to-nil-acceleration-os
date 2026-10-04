"""Honesty: contributor surfaces must not publish an NIL band.

CONTRIBUTING, the PR template, and the copy-review log are how a change
ships. While the golden-set gate is closed they may name a range-plus-
disclaimer rule. They must not print a dollar, a numeric percentile, MAE,
or claim the gate is open. Copy review has not run.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRIBUTING = ROOT / "CONTRIBUTING.md"
TEMPLATE = ROOT / ".github" / "PULL_REQUEST_TEMPLATE.md"
REVIEW = ROOT / "docs" / "copy" / "review_log.md"

_DOLLAR = re.compile(r"\$\s*\d")
_PERCENTILE = re.compile(r"\b(p25|p50|p75)\b\s*[:=]\s*\d", re.IGNORECASE)
_MAE = re.compile(r"\bMAE\b\s*[:=]\s*\d", re.IGNORECASE)
_GATE_OPEN = re.compile(r"golden[- ]set gate is open", re.IGNORECASE)


def test_contributing_keeps_nil_null_until_gate_opens() -> None:
    text = CONTRIBUTING.read_text()
    lowered = text.lower()
    assert "null" in lowered
    assert "blocked_on_golden_set" in text
    assert "do not invent" in lowered
    assert "athlete video" in lowered
    assert _DOLLAR.search(text) is None
    assert _PERCENTILE.search(text) is None
    assert _MAE.search(text) is None
    assert _GATE_OPEN.search(text) is None


def test_pr_template_forbids_guaranteed_dollars() -> None:
    text = TEMPLATE.read_text()
    lowered = text.lower()
    assert "no guaranteed dollar figures" in lowered
    assert "no athlete pii or raw video" in lowered
    assert _DOLLAR.search(text) is None
    assert _PERCENTILE.search(text) is None
    assert _MAE.search(text) is None
    assert _GATE_OPEN.search(text) is None


def test_copy_review_log_has_not_run() -> None:
    text = REVIEW.read_text()
    lowered = text.lower()
    assert "sessions not run yet" in lowered
    assert "approved nil" not in lowered
    assert _DOLLAR.search(text) is None
    assert _PERCENTILE.search(text) is None
    assert _MAE.search(text) is None
