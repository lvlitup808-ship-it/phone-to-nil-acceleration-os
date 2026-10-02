"""Honesty: evidence and judgment must not publish NIL numbers.

The evidence loop retrieves drill copy and placeholder comps. Judgment only
returns bounded decisions. Neither package may hardcode a dollar amount, a
numeric percentile, or a measured MAE, and a live retrieve must keep comp
bands null.
"""

from __future__ import annotations

import ast
import json
import re
from pathlib import Path

from packages.evidence.pipeline import EvidencePipeline

ROOT = Path(__file__).resolve().parents[1]
SURFACES = (ROOT / "packages" / "evidence", ROOT / "packages" / "judgment")
BAND_KEYS = {"p25", "p50", "p75"}
DOLLAR = re.compile(r"\$\s*\d")
MAE = re.compile(r"\bMAE\b\s*[:=]\s*\d", re.IGNORECASE)


def test_evidence_and_judgment_source_have_no_nil_numbers() -> None:
    dollar_hits: list[str] = []
    mae_hits: list[str] = []
    band_hits: list[str] = []
    for surface in SURFACES:
        for path in sorted(surface.rglob("*.py")):
            text = path.read_text()
            rel = path.relative_to(ROOT)
            for i, line in enumerate(text.splitlines(), 1):
                if DOLLAR.search(line):
                    dollar_hits.append(f"{rel}:{i}:{line.strip()}")
                if MAE.search(line):
                    mae_hits.append(f"{rel}:{i}:{line.strip()}")
            tree = ast.parse(text)
            for node in ast.walk(tree):
                if isinstance(node, ast.keyword) and node.arg in BAND_KEYS:
                    val = node.value
                    if isinstance(val, ast.Constant) and isinstance(val.value, (int, float)):
                        band_hits.append(f"{rel}:{node.lineno}:{node.arg}={val.value}")
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name) and target.id in BAND_KEYS:
                            val = node.value
                            if isinstance(val, ast.Constant) and isinstance(val.value, (int, float)):
                                band_hits.append(f"{rel}:{node.lineno}:{target.id}={val.value}")
    assert dollar_hits == [], dollar_hits
    assert mae_hits == [], mae_hits
    assert band_hits == [], band_hits


def test_evidence_retrieve_keeps_comp_bands_null() -> None:
    pipe = EvidencePipeline()
    out = pipe.run("wr release comparable", "shin_angle")
    blob = json.dumps(out)
    assert DOLLAR.search(blob) is None
    assert MAE.search(blob) is None
    comps = [row for row in out.get("comps", []) if isinstance(row, dict)]
    assert comps, "expected placeholder comps so a band cannot hide by omission"
    for row in comps:
        assert row.get("status") == "placeholder"
        for key in ("p25", "p50", "p75", "n"):
            assert row.get(key) is None, f"{row.get('id')} {key}={row.get(key)}"
        assert "no comp data collected yet" in " ".join(row.get("assumptions") or [])
