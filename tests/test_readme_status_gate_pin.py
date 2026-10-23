"""Pin README Status matches the closed golden gate.

Operator-facing Status must stay honest: golden set pending, gate closed,
no published MAE, NIL bands null. A drift that opens the gate in prose fails CI.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README = (ROOT / "README.md").read_text()


def test_readme_status_says_gate_closed_and_pending() -> None:
    status = README.split("## Status", 1)[1].split("## Solution", 1)[0]
    assert "**Golden set: pending.**" in status
    assert "No real, coach-labeled film exists." in status
    assert "No accuracy (MAE) against coach labels is published" in status
    assert "**Gate closed.**" in status
    assert "blocked_on_golden_set" in status
    assert "p25/p50/p75 are `null`" in status
    assert "$" not in status
