"""Honesty pin: the live golden set on disk keeps the film-first gate closed.

No real labeled film exists. wr_labeled and db_labeled stay 0. Status is
blocked_on_golden_set. Fixture manifest entries never count. No NIL numbers.
"""

from __future__ import annotations

from services.api.gates import get_progress, gate_state


def test_live_golden_progress_is_zero():
    progress = get_progress()
    assert progress["wr_labeled"] == 0
    assert progress["db_labeled"] == 0
    assert progress["inter_rater_done"] is False
    assert progress["disputed"] == 0
    assert progress["surfaces"] == 0
    assert progress["lighting_conditions"] == 0
    assert progress["wr_athletes"] == 0
    assert progress["db_athletes"] == 0


def test_live_gate_status_blocked():
    state = gate_state()
    assert state["status"] == "blocked_on_golden_set"
    assert "p25" not in state
    assert "mae" not in state
