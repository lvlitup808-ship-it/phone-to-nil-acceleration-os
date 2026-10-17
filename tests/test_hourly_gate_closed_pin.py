"""Hourly pin: current golden set keeps the film-first gate closed.

No real labeled film exists. Fixture clips must never open the gate.
"""

from services.api.gates import gate_state


def test_current_manifest_keeps_gate_closed():
    state = gate_state()
    assert state["status"] == "blocked_on_golden_set"
    progress = state["progress"]
    assert progress["wr_labeled"] == 0
    assert progress["db_labeled"] == 0
    assert not state.get("open", True) or state["status"] != "open"
