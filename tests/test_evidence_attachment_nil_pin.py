"""Honesty: evidence comps and attachment docs must not publish NIL numbers.

The evidence loop may cite placeholder clusters. It must not return a dollar,
a numeric p25/p50/p75, MAE, or a composite while the golden-set gate is closed.
Attachment notes, Jev, and RAG docs may name the closed gate. They are not a band.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from packages.evidence.pipeline import EvidencePipeline

ROOT = Path(__file__).resolve().parents[1]
DOCS = (
    ROOT / "docs" / "attachments",
    ROOT / "docs" / "jev-judgments.md",
    ROOT / "docs" / "rag-evidence.md",
)
_DOLLAR = re.compile(r"\$\s*\d")
_PERCENTILE = re.compile(r"\b(p25|p50|p75)\b\s*[:=]\s*\d", re.IGNORECASE)
_MAE = re.compile(r"\bMAE\b\s*[:=]?\s*\d", re.IGNORECASE)
_BAND_KEYS = ("p25", "p50", "p75")


def test_evidence_run_returns_no_nil_numbers() -> None:
    pipe = EvidencePipeline()
    out = pipe.run("nil recruiting band comparable wr release", "shin_angle")
    blob = json.dumps(out)
    lowered = blob.lower()
    assert _DOLLAR.search(blob) is None
    assert _PERCENTILE.search(blob) is None
    assert _MAE.search(blob) is None
    assert "composite" not in lowered
    for comp in out["comps"]:
        for key in _BAND_KEYS:
            assert comp.get(key) is None
        assert comp.get("n") is None
        assert comp.get("status") == "placeholder"
    assert out["comps"] == [] or all(c.get("status") == "placeholder" for c in out["comps"])


def test_attachment_jev_rag_docs_publish_no_nil_or_mae() -> None:
    offenders: list[str] = []
    paths: list[Path] = []
    for doc in DOCS:
        if doc.is_dir():
            paths.extend(sorted(doc.glob("*.md")))
        else:
            paths.append(doc)
    assert paths
    for path in paths:
        text = path.read_text()
        if _DOLLAR.search(text) or _PERCENTILE.search(text) or _MAE.search(text):
            offenders.append(str(path.relative_to(ROOT)))
        if "your nil is" in text.lower():
            offenders.append(str(path.relative_to(ROOT)))
    assert offenders == []


def test_rag_doc_refuses_point_estimate() -> None:
    text = (ROOT / "docs" / "rag-evidence.md").read_text()
    assert "Do not emit a point estimate." in text
    assert "Every numeric NIL claim must map to a retrieved comp row." in text
