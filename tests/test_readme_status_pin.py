"""Pin README Status claims to live gate + golden-set reality.

If Status says gate closed / golden pending / no MAE, those must match
GET /gates/golden and the manifest. Prevents the Status paragraph from
lying after someone opens the gate or invents accuracy numbers.
"""

from __future__ import annotations

import re
from pathlib import Path

from fastapi.testclient import TestClient

from services.api.app import app
from services.api.gates import get_progress, prescription_enabled

ROOT = Path(__file__).resolve().parents[1]
README = (ROOT / "README.md").read_text()
MANIFEST = (ROOT / "data/golden_set/manifest.json").read_text()

client = TestClient(app)


def test_readme_status_declares_gate_closed_matching_live():
    assert re.search(r"\*\*Gate closed\.\*\*", README), "README Status missing **Gate closed.**"
    live = client.get("/gates/golden").json()
    assert live["status"] == "blocked_on_golden_set"
    assert prescription_enabled(get_progress()) is False


def test_readme_status_declares_golden_pending_matching_manifest():
    assert re.search(r"\*\*Golden set:\s*pending\.\*\*", README), "README Status missing **Golden set: pending.**"
    assert '"golden_set": "pending"' in MANIFEST or '"golden_set":"pending"' in MANIFEST


def test_readme_status_never_claims_measured_mae():
    # Honesty: calibration error is unmeasured; no published MAE number.
    assert "No accuracy (MAE)" in README or "no accuracy (MAE)" in README.lower()
    # Fail if someone pastes a numeric MAE into Status (e.g. "MAE 12.3").
    status_block = README.split("## Status")[1].split("## Solution")[0]
    assert not re.search(r"\bMAE\s*[:=]?\s*\d", status_block, flags=re.I), (
        "README Status must not publish a numeric MAE while golden set is pending"
    )


def test_readme_status_says_no_real_coach_labeled_film():
    assert "No real, coach-labeled film exists" in README
    p = get_progress()
    assert p["wr_labeled"] == 0 and p["db_labeled"] == 0
