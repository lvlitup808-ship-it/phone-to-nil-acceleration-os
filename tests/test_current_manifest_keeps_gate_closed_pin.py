"""Honesty pin: current fixture manifest keeps the film-first gate closed.

No clip has camera film present. Surface/lighting/athlete mix is unmet.
Only real labeled film on disk can open the gate. This pin fails if the
manifest is later treated as validation or if progress counters move off zero
without film.
"""

from fastapi.testclient import TestClient

from services.api.app import app
from services.api.gates import get_progress, prescription_enabled

client = TestClient(app)


def test_current_manifest_keeps_gate_closed():
    progress = get_progress()
    assert prescription_enabled(progress) is False
    assert progress["wr_labeled"] == 0
    assert progress["db_labeled"] == 0
    assert progress.get("disputed", 0) <= 2

    gate = client.get("/gates/golden").json()
    assert gate["status"] == "blocked_on_golden_set"
    assert gate["wr_labeled"] == 0
    assert gate["db_labeled"] == 0

    # Fixture clips must not be counted
    for clip in progress.get("clips", []) or []:
        assert not clip.get("camera_side", {}).get("present", False)
        assert not clip.get("camera_45", {}).get("present", False)
