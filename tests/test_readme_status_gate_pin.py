"""Honesty pin: README Status section must stay truthful about the closed gate.

The Status block in README.md is the public claim. It must say the golden set
is pending and the gate is closed, matching the live /gates/golden response.
No MAE, no composite, no invented numbers.
"""

from pathlib import Path

from fastapi.testclient import TestClient

from services.api.app import app

ROOT = Path(__file__).resolve().parents[1]
client = TestClient(app)


def test_readme_status_declares_gate_closed_and_golden_pending():
    text = (ROOT / "README.md").read_text()
    status_section = text.split("## Status (what is real today)")[1].split("## Solution")[0]
    assert "Golden set: pending" in status_section
    assert "Gate closed" in status_section
    assert "No accuracy (MAE)" in status_section or "MAE" in status_section
    assert "p25/p50/p75 are `null`" in status_section


def test_readme_status_matches_live_gate():
    body = client.get("/gates/golden").json()
    assert body["status"] == "blocked_on_golden_set"
    text = (ROOT / "README.md").read_text()
    assert "Gate closed" in text
    # Live progress must be zero while fixtures only.
    progress = body["progress"]
    assert progress["wr_labeled"] == 0
    assert progress["db_labeled"] == 0
