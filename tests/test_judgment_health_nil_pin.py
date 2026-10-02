"""Honesty: judgment fallback, /health, and drill seeds carry no NIL numbers.

/health is liveness only. Judgment answers are bounded decisions, not a
valuation. Sample drills and position templates are prescription seeds.
None of them may publish p25/p50/p75, MAE, a composite, or a dollar amount
while the golden set is still pending.
"""

from __future__ import annotations

import os
import re
from pathlib import Path

from fastapi.testclient import TestClient

from packages.judgment.client import JudgmentClient
from services.api.app import app
from services.api.gates import get_progress, prescription_enabled

ROOT = Path(__file__).resolve().parents[1]
client = TestClient(app)
DOLLAR = re.compile(r"\$\s*\d")
_FORBIDDEN = ("p25", "p50", "p75", "mae", "composite", "nil_band", "nil_dollars")


def _assert_no_valuation(body: object) -> None:
    if isinstance(body, dict):
        for key, value in body.items():
            assert key.lower() not in _FORBIDDEN, key
            assert not (isinstance(value, str) and "$" in value and any(c.isdigit() for c in value))
            _assert_no_valuation(value)
    elif isinstance(body, list):
        for item in body:
            _assert_no_valuation(item)


def test_gate_still_closed_before_health_and_judgment() -> None:
    assert prescription_enabled(get_progress()) is False
    assert get_progress()["wr_labeled"] == 0
    assert get_progress()["db_labeled"] == 0


def test_health_is_liveness_only() -> None:
    res = client.get("/health")
    assert res.status_code == 200
    body = res.json()
    assert body == {"status": "ok"}
    assert body.get("status") != "open"
    _assert_no_valuation(body)


def test_heuristic_judgment_is_not_a_valuation() -> None:
    os.environ.pop("TYPESAFE_API_KEY", None)
    judge = JudgmentClient()
    judge.api_key = ""
    decisions = judge.decide(
        {"quality_score": 0.9, "blur": 0.05, "angle": "side", "citations": []},
        {
            "usable": {"type": "noul", "instructions": "Is this clip usable for pose estimation?"},
            "synthetic": {"type": "noul", "instructions": "Does this look like a synthetic highlight?"},
            "grounded": {"type": "noul", "instructions": "Is the claim grounded?"},
            "template": {"type": "choice", "criteria": {"wr_release": "WR", "db_break": "DB"}},
        },
    )
    assert set(decisions) == {"usable", "synthetic", "grounded", "template"}
    for name, judgment in decisions.items():
        assert judgment.source == "heuristic"
        assert judgment.name == name
        dumped = {
            "name": judgment.name,
            "kind": judgment.kind,
            "value": judgment.value,
            "confidence": judgment.confidence,
            "source": judgment.source,
        }
        _assert_no_valuation(dumped)
        assert not isinstance(judgment.value, str) or "$" not in judgment.value


def test_judgment_and_seed_copy_have_no_dollar_amounts() -> None:
    roots = [
        ROOT / "packages" / "judgment",
        ROOT / "data" / "samples" / "drills.json",
        ROOT / "data" / "samples" / "position_templates.json",
    ]
    hits: list[str] = []
    for root in roots:
        paths = [root] if root.is_file() else sorted(root.rglob("*"))
        for path in paths:
            if not path.is_file() or path.suffix not in {".py", ".json", ".md"}:
                continue
            for i, line in enumerate(path.read_text().splitlines(), 1):
                if DOLLAR.search(line):
                    hits.append(f"{path.relative_to(ROOT)}:{i}:{line.strip()}")
    assert hits == [], hits
