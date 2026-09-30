"""Source-level NIL honesty pin.

Runtime tests already assert p25/p50/p75 stay None. This file fails if anyone
hardcodes a dollar amount or a numeric percentile into services/valuation.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VAL = ROOT / "services" / "valuation"
BAND_KEYS = {"p25", "p50", "p75", "confidence"}
DOLLAR = re.compile(r"\$\s*\d")


def test_valuation_source_band_kwargs_are_none():
    hits: list[str] = []
    for path in sorted(VAL.rglob("*.py")):
        tree = ast.parse(path.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.keyword) and node.arg in BAND_KEYS:
                val = node.value
                if isinstance(val, ast.Constant) and isinstance(val.value, (int, float)):
                    hits.append(f"{path.relative_to(ROOT)}:{node.lineno}:{node.arg}={val.value}")
    assert hits == [], hits


def test_valuation_source_has_no_dollar_amounts():
    hits: list[str] = []
    for path in sorted(VAL.rglob("*.py")):
        for i, line in enumerate(path.read_text().splitlines(), 1):
            if DOLLAR.search(line):
                hits.append(f"{path.relative_to(ROOT)}:{i}:{line.strip()}")
    assert hits == [], hits
