"""Honesty: product and evidence docs must not publish an NIL point estimate.

The golden-set gate is closed. Product thesis, architecture, RAG notes, and
athlete-facing copy may describe a future range. They must not print a dollar
amount, a numeric p25/p50/p75, MAE, or a composite score. Share links stay
access tokens only.
"""

from __future__ import annotations

import re
from pathlib import Path

from fastapi.testclient import TestClient

from services.api.app import app

ROOT = Path(__file__).resolve().parents[1]
DOCS = (
    ROOT / "docs" / "product.md",
    ROOT / "docs" / "architecture.md",
    ROOT / "docs" / "rag-evidence.md",
    ROOT / "docs" / "copy" / "athlete_facing_review.md",
)

_DOLLAR = re.compile(r"\$\s*\d")
_PERCENTILE = re.compile(r"\b(p25|p50|p75)\b\s*[:=]\s*\d", re.IGNORECASE)
_MAE = re.compile(r"\bMAE\b\s*[:=]\s*\d", re.IGNORECASE)

client = TestClient(app)


def test_product_docs_do_not_publish_nil_numbers() -> None:
    offenders: list[str] = []
    for path in DOCS:
        text = path.read_text()
        lowered = text.lower()
        if _DOLLAR.search(text) or _PERCENTILE.search(text) or _MAE.search(text):
            offenders.append(str(path.relative_to(ROOT)))
        if "your nil is" in lowered or "composite score" in lowered:
            offenders.append(str(path.relative_to(ROOT)))
    assert offenders == []


def test_rag_evidence_refuses_point_estimate() -> None:
    text = (ROOT / "docs" / "rag-evidence.md").read_text().lower()
    assert "do not emit a point estimate" in text
    assert "numeric nil claim" in text


def test_athlete_facing_copy_forbids_nil_deal() -> None:
    text = (ROOT / "docs" / "copy" / "athlete_facing_review.md").read_text().lower()
    assert "nil deal" in text
    assert "not a ranking" in text


def test_share_link_payload_has_no_nil_fields() -> None:
    body = client.post(
        "/share-link",
        json={"athlete_id": "ath_share_pin", "recipient": "coach@x.test", "ttl_days": 7},
    ).json()
    assert body["athlete_id"] == "ath_share_pin"
    assert "token" in body
    banned = {"p25", "p50", "p75", "nil_band", "mae", "composite", "valuation"}
    assert banned.isdisjoint(body.keys())
    blob = str(body).lower()
    assert "$" not in blob
    assert "mae" not in blob
