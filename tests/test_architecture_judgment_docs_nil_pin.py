"""Honesty pin: architecture and judgment docs must not publish NIL dollars or MAE.

Architecture, Jev, RAG, attachments, athlete-facing copy, and PROMPT may name
the valuation slot. They must not print a dollar band, a numeric percentile, or
a measured MAE while the golden-set gate is closed.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PATHS = [
    ROOT / "docs" / "architecture.md",
    ROOT / "docs" / "jev-judgments.md",
    ROOT / "docs" / "rag-evidence.md",
    ROOT / "PROMPT.md",
    ROOT / "docs" / "copy" / "athlete_facing_review.md",
    ROOT / "docs" / "copy" / "review_log.md",
]

_DOLLAR = re.compile(r"\$\s*\d")
_PERCENTILE = re.compile(r"\b(p25|p50|p75)\b\s*[:=]\s*\d", re.IGNORECASE)
_MAE = re.compile(r"\bMAE\b\s*[:=]?\s*\d", re.IGNORECASE)


def _attachment_docs() -> list[Path]:
    return sorted((ROOT / "docs" / "attachments").glob("*.md"))


def test_architecture_and_judgment_docs_publish_no_nil_or_mae() -> None:
    offenders: list[str] = []
    for path in PATHS + _attachment_docs():
        assert path.is_file(), path
        text = path.read_text()
        if _DOLLAR.search(text):
            offenders.append(f"{path.relative_to(ROOT)}:dollar")
        if _PERCENTILE.search(text):
            offenders.append(f"{path.relative_to(ROOT)}:percentile")
        if _MAE.search(text):
            offenders.append(f"{path.relative_to(ROOT)}:mae")
    assert offenders == []


def test_rag_and_attachments_stay_ungrounded() -> None:
    rag = (ROOT / "docs" / "rag-evidence.md").read_text()
    assert "Do not emit a point estimate." in rag
    assert "Every numeric NIL claim must map to a retrieved comp row." in rag
    attachments = (ROOT / "docs" / "attachments" / "README.md").read_text()
    assert "[ ] NIL/recruiting data" in attachments
    copy = (ROOT / "docs" / "copy" / "athlete_facing_review.md").read_text()
    assert "This is not a ranking." in copy
