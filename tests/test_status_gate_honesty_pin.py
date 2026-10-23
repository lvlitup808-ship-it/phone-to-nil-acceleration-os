"""Honesty pin: README Status must match the live golden-set gate.

The Status section must say the golden set is pending and the gate is closed
while GET /gates/golden reports blocked_on_golden_set. No invented progress.
"""

from pathlib import Path

from fastapi.testclient import TestClient

from services.api.app import app

ROOT = Path(__file__).resolve().parents[1]
client = TestClient(app)


def test_readme_status_matches_closed_gate():
    readme = (ROOT / "README.md").read_text()
    status = readme.split("## Status (what is real today)")[1].split("## Solution")[0]
    assert "Golden set: pending" in status
    assert "Gate closed" in status
    assert "blocked_on_golden_set" in status

    body = client.get("/gates/golden").json()
    assert body["status"] == "blocked_on_golden_set"
    assert body["progress"]["wr_labeled"] == 0
    assert body["progress"]["db_labeled"] == 0
