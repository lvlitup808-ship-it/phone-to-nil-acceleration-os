"""Honesty pin: README endpoint table still documents closed-gate behavior.

Prevents the public endpoint table from drifting to claim open prescription,
invented NIL numbers, or non-empty position-fit clusters while the golden set
is pending. Complements the OpenAPI/route existence pin in test_docs_consistency.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README = (ROOT / "README.md").read_text()


def _row(route: str) -> str:
    # Match the table row for an exact route template.
    pattern = rf"^\| `[^`]* {re.escape(route)}` \|.*\|$"
    matches = re.findall(pattern, README, flags=re.M)
    assert matches, f"README missing endpoint row for {route}"
    return matches[0]


def test_nil_band_row_documents_null_and_blocked() -> None:
    row = _row("/nil-band/{athlete_id}")
    assert "blocked_on_golden_set" in row
    assert "p25/p50/p75 `null`" in row


def test_nil_scenarios_row_documents_schema_only() -> None:
    row = _row("/nil-band/{athlete_id}/scenarios")
    assert "schema_only" in row
    assert "scenarios: []" in row


def test_position_fit_row_documents_blocked_empty() -> None:
    row = _row("/position-fit/{athlete_id}")
    assert "blocked_on_golden_set" in row
    assert "clusters: []" in row


def test_passport_row_documents_blocked_empty() -> None:
    row = _row("/passport/{athlete_id}")
    assert "blocked_on_golden_set" in row
    assert "assessments: []" in row


def test_prescribe_row_documents_blocked_empty() -> None:
    row = _row("/prescribe/{assessment_id}")
    assert "blocked_on_golden_set" in row
    assert "drills: []" in row
