"""Honesty pin: architecture, RAG, and Jev docs publish no NIL dollars or MAE.

These docs describe layers and decisions. They must say band quantiles stay
null while the golden-set gate is closed, and must not print a dollar amount,
a numeric percentile, or a measured MAE.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = [
    ROOT / "docs" / "architecture.md",
    ROOT / "docs" / "rag-evidence.md",
    ROOT / "docs" / "jev-judgments.md",
]

_DOLLAR = re.compile(r"\$\s*\d")
_PERCENTILE = re.compile(r"\b(p25|p50|p75)\b\s*[:=]\s*\d", re.IGNORECASE)
_MAE = re.compile(r"\bMAE\b\s*[:=]?\s*\d", re.IGNORECASE)


def test_layer_docs_publish_no_nil_or_mae() -> None:
    offenders: list[str] = []
    for path in DOCS:
        assert path.is_file(), path
        text = path.read_text()
        rel = str(path.relative_to(ROOT))
        if _DOLLAR.search(text):
            offenders.append(f"{rel}:dollar")
        if _PERCENTILE.search(text):
            offenders.append(f"{rel}:percentile")
        if _MAE.search(text):
            offenders.append(f"{rel}:mae")
    assert offenders == []


def test_layer_docs_state_null_bands_and_closed_gate() -> None:
    for path in DOCS:
        text = path.read_text()
        assert "p25/p50/p75 stay null" in text, path.name
        assert "No MAE is published" in text, path.name
        assert "blocked_on_golden_set" in text, path.name
