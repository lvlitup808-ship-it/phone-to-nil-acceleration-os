"""Honesty: drill seed, position templates, and judgment fallback publish no NIL.

These files feed prescription and template choice. A dollar, composite, MAE,
or p25/p50/p75 here would look like a valuation while the golden-set gate is
closed. This pin does not open the gate and does not invent numbers.
"""

from __future__ import annotations

import json
from pathlib import Path

from packages.judgment.client import JudgmentClient

ROOT = Path(__file__).resolve().parents[1]
DRILLS = ROOT / "data" / "samples" / "drills.json"
TEMPLATES = ROOT / "data" / "samples" / "position_templates.json"
FORBIDDEN = ("$", "mae", "composite", "p25", "p50", "p75")


def _assert_no_valuation_tokens(raw: str, label: str) -> None:
    low = raw.lower()
    for token in FORBIDDEN:
        assert token not in low, f"{label} contains {token}"


def test_drill_seed_publishes_no_nil_or_mae() -> None:
    raw = DRILLS.read_text()
    _assert_no_valuation_tokens(raw, "drills.json")
    rows = json.loads(raw)
    assert rows, "expected seed drills so a numeric leak is visible"
    for row in rows:
        assert "nil" not in json.dumps(row).lower()
        assert row.get("coach_reviewed") in (True, False)
        assert isinstance(row.get("evidence_chunk_ids"), list)


def test_position_templates_publish_no_nil_or_mae() -> None:
    raw = TEMPLATES.read_text()
    _assert_no_valuation_tokens(raw, "position_templates.json")
    data = json.loads(raw)
    assert "wr_release" in data
    assert "db_break" in data
    for name, template in data.items():
        assert template.get("cues"), name
        assert all(isinstance(cue, str) for cue in template["cues"])


def test_judgment_heuristic_has_no_nil_band() -> None:
    client = JudgmentClient()
    client.api_key = ""
    out = client.decide(
        {"quality_score": 0.9, "blur": 0.1, "citations": ["chk_shin_01"], "template": "wr_release"},
        {
            "clip_usable": {"type": "noul"},
            "synthetic_highlight_risk": {"type": "noul"},
            "grounded_claim": {"type": "noul"},
            "template": {"type": "choice", "criteria": {"wr_release": "WR", "db_break": "DB"}},
        },
    )
    blob = json.dumps({name: judgment.__dict__ for name, judgment in out.items()})
    _assert_no_valuation_tokens(blob, "judgment heuristic")
    assert all(judgment.source == "heuristic" for judgment in out.values())
