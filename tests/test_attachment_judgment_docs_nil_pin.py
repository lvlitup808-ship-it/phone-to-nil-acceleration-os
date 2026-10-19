"""Honesty pin: attachment, judgment, and evidence docs publish no NIL dollars.

These notes describe the Jev layer and the RAG loop. They may say a numeric
NIL claim must be grounded, and they may leave the comps CSV unchecked. They
must not print a dollar band, a numeric percentile, or a measured MAE.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = (
    ROOT / "PROMPT.md",
    ROOT / "docs" / "jev-judgments.md",
    ROOT / "docs" / "rag-evidence.md",
    ROOT / "docs" / "attachments" / "README.md",
    ROOT / "docs" / "attachments" / "links.md",
    ROOT / "docs" / "attachments" / "notes.md",
    ROOT / "docs" / "attachments" / "slice2.md",
    ROOT / "docs" / "attachments" / "d21-d35.md",
    ROOT / "docs" / "attachments" / "x-posts.md",
)

_DOLLAR = re.compile(r"\$\s*\d")
_PERCENTILE = re.compile(r"\b(p25|p50|p75)\b\s*[:=]\s*\d", re.IGNORECASE)
_MAE = re.compile(r"\bMAE\b\s*[:=]?\s*\d", re.IGNORECASE)


def test_attachment_and_judgment_docs_publish_no_nil_or_mae() -> None:
    offenders: list[str] = []
    for path in DOCS:
        assert path.is_file(), path
        text = path.read_text()
        if _DOLLAR.search(text):
            offenders.append(f"{path.relative_to(ROOT)}:dollar")
        if _PERCENTILE.search(text):
            offenders.append(f"{path.relative_to(ROOT)}:percentile")
        if _MAE.search(text):
            offenders.append(f"{path.relative_to(ROOT)}:mae")
    assert offenders == []


def test_rag_refuses_ungrounded_point_estimate() -> None:
    text = (ROOT / "docs" / "rag-evidence.md").read_text()
    assert "Do not emit a point estimate." in text
    assert "Every numeric NIL claim must map to a retrieved comp row." in text


def test_jev_does_not_write_valuation() -> None:
    text = (ROOT / "docs" / "jev-judgments.md").read_text()
    assert "Jev does **not** write." in text
    assert "NIL verifier" in text
    lowered = text.lower()
    assert "p25" not in lowered
    assert "p50" not in lowered
    assert "p75" not in lowered


def test_comps_csv_is_still_unchecked() -> None:
    text = (ROOT / "docs" / "attachments" / "README.md").read_text()
    assert "[ ] NIL/recruiting data" in text
    assert "do not commit raw athlete media" in text
