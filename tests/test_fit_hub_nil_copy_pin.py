"""Honesty: FIT HUB copy must not publish an NIL point estimate.

The marketing surface can say bands stay null. It must not print a dollar
amount, a p25/p50/p75 assignment, an MAE, or claim the golden-set gate is open.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HUB = ROOT / "apps" / "fit-hub" / "src"
FILM = HUB / "film.ts"

_DOLLAR = re.compile(r"\$\s*\d")
_PERCENTILE = re.compile(r"\b(p25|p50|p75)\b\s*[:=]\s*\d", re.IGNORECASE)
_MAE = re.compile(r"\bMAE\b\s*[:=]\s*\d", re.IGNORECASE)
_GATE_OPEN = re.compile(r"\bgate\s+is\s+open\b", re.IGNORECASE)
_GOLDEN_MET = re.compile(
    r"\bgolden set\s+is\s+(met|complete|open)\b",
    re.IGNORECASE,
)


def _sources() -> list[Path]:
    return [
        path
        for path in HUB.rglob("*")
        if path.suffix in {".ts", ".tsx", ".js", ".jsx"}
    ]


def test_fit_hub_says_nil_bands_stay_null() -> None:
    text = FILM.read_text()
    assert "NIL bands stay null" in text
    assert "No composite" in text
    assert _GATE_OPEN.search(text) is None
    assert _GOLDEN_MET.search(text) is None


def test_fit_hub_src_has_no_nil_point_estimates() -> None:
    offenders: list[str] = []
    for path in _sources():
        text = path.read_text()
        if (
            _DOLLAR.search(text)
            or _PERCENTILE.search(text)
            or _MAE.search(text)
            or _GATE_OPEN.search(text)
            or _GOLDEN_MET.search(text)
        ):
            offenders.append(str(path.relative_to(ROOT)))
    assert offenders == []
