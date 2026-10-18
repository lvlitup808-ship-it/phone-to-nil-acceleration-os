"""Pin README Status section matches live honesty.

Status must claim golden set pending, gate closed, NIL bands null.
No invented MAE or dollars.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README = (ROOT / "README.md").read_text()
STATUS = README.split("## Status (what is real today)")[1].split("## Solution")[0]


def test_status_says_golden_pending_and_gate_closed():
    assert "Golden set: pending." in STATUS
    assert "No real, coach-labeled film exists." in STATUS
    assert "Gate closed." in STATUS
    assert "blocked_on_golden_set" in STATUS
    assert "Live state: `GET /gates/golden`." in STATUS


def test_status_says_nil_null_no_mae():
    assert "NIL bands are schema placeholders." in STATUS
    assert "p25/p50/p75 are `null`" in STATUS
    assert "there is no comp dataset." in STATUS
    assert "No accuracy (MAE)" in STATUS
    assert "calibration error is unmeasured." in STATUS
