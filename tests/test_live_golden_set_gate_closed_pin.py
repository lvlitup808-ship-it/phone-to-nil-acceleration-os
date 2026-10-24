"""Honesty pin: the live golden set on disk keeps the film-first gate closed.

manifest.json marks golden_set pending, both fixture clips have present: false,
and no real film exists. gate_state must report blocked_on_golden_set and zero
labeled clips. No NIL numbers are computed.
"""

from __future__ import annotations

from pathlib import Path

from services.api.gates import gate_state, get_progress


ROOT = Path(__file__).resolve().parents[1]
GOLDEN = ROOT / "data" / "golden_set"


def test_live_manifest_has_no_film():
    import json
    manifest = json.loads((GOLDEN / "manifest.json").read_text())
    assert manifest.get("golden_set") == "pending"
    for clip in manifest.get("clips", []):
        for cam in ("camera_side", "camera_45"):
            if cam in clip:
                assert clip[cam].get("present") is False, clip["clip_id"]


def test_live_gate_stays_closed():
    progress = get_progress(GOLDEN)
    assert progress["wr_labeled"] == 0
    assert progress["db_labeled"] == 0
    state = gate_state()
    assert state["status"] == "blocked_on_golden_set"
    assert "wr_labeled 0/10" in state["missing"]
