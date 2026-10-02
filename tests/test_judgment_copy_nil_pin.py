"""Honesty: judgment and athlete-facing copy must not mint NIL numbers.

Bounded decisions and the D23 copy review are not valuations. While the
golden-set gate is closed they must not print a dollar, a numeric
percentile, MAE, or a composite.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from packages.judgment.client import JudgmentClient

ROOT = Path(__file__).resolve().parents[1]
COPY = ROOT / "docs" / "copy"
_DOLLAR = re.compile(r"\$\s*\d")
_PERCENTILE = re.compile(r"\b(p25|p50|p75)\b\s*[:=]\s*\d", re.IGNORECASE)
_MAE = re.compile(r"\bMAE\b\s*[:=]\s*\d", re.IGNORECASE)


def test_heuristic_judgments_carry_no_nil_band() -> None:
    client = JudgmentClient()
    client.api_key = ""
    decisions = client.decide(
        {"quality_score": 0.9, "blur": 0.05, "template": "wr_release", "citations": ["drill_1"]},
        {
            "clip_usable": {"type": "noul", "instructions": "Is the clip usable?"},
            "cue_priority": {"type": "choice", "criteria": {"shin_angle": "shin", "hip_height": "hip"}},
            "synthetic_highlight_risk": {"type": "noul", "instructions": "Synthetic highlight risk?"},
            "grounded": {"type": "noul", "instructions": "Are claims grounded?"},
        },
    )
    blob = json.dumps({name: decision.__dict__ for name, decision in decisions.items()})
    lowered = blob.lower()
    for key in ("p25", "p50", "p75", "mae", "composite"):
        assert key not in lowered
    assert _DOLLAR.search(blob) is None
    for decision in decisions.values():
        assert decision.source == "heuristic"
        assert "nil" not in decision.name


def test_athlete_facing_copy_forbids_deals_and_prints_no_numbers() -> None:
    review = (COPY / "athlete_facing_review.md").read_text()
    lowered = review.lower()
    assert "forbidden" in lowered
    assert "nil deal" in lowered
    assert "guaranteed" in lowered
    assert "not a ranking" in lowered
    offenders: list[str] = []
    for path in sorted(COPY.glob("*.md")):
        text = path.read_text()
        if _DOLLAR.search(text) or _PERCENTILE.search(text) or _MAE.search(text):
            offenders.append(str(path.relative_to(ROOT)))
        if "your nil is" in text.lower():
            offenders.append(str(path.relative_to(ROOT)))
    assert offenders == []
