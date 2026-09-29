"""Honesty pin: live golden-set progress is zero while no real film exists.

Fails if fixture labels or present:false clips start counting toward the gate,
or if gate_state invents open status before film_first thresholds are met.
"""

from services.api import gates


def test_live_progress_all_zeros():
    p = gates.get_progress()
    assert p["wr_labeled"] == 0
    assert p["db_labeled"] == 0
    assert p["inter_rater_done"] is False
    assert p["inter_rater_clips"] == 0
    assert p["disputed"] == 0
    assert p["surfaces"] == 0
    assert p["lighting_conditions"] == 0
    assert p["wr_athletes"] == 0
    assert p["db_athletes"] == 0


def test_live_gate_blocked_with_expected_missing():
    state = gates.gate_state()
    assert state["status"] == "blocked_on_golden_set"
    missing = state["missing"]
    assert any(m.startswith("wr_labeled") for m in missing)
    assert any(m.startswith("db_labeled") for m in missing)
    assert "inter_rater" in missing
    assert any(m.startswith("surfaces") for m in missing)
    assert any(m.startswith("lighting") for m in missing)
    assert any(m.startswith("wr_athletes") for m in missing)
    assert any(m.startswith("db_athletes") for m in missing)
    assert state["progress"] == gates.get_progress()
