"""Honesty pin: the golden-set labeling protocol is not an MAE report.

docs/golden_set/labeling_protocol.md is the coach labeling contract.
data/golden_set/README.md documents fixture scale stand-ins.
Neither may publish a dollar band, a numeric MAE, or treat the 185 / 183
fixture heights as athlete measurements. The live gate payload must not
echo those stand-ins.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from services.api import gates

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "docs" / "golden_set" / "labeling_protocol.md"
README = ROOT / "data" / "golden_set" / "README.md"

_DOLLAR = re.compile(r"\$\s*\d")
_PERCENTILE = re.compile(r"\b(p25|p50|p75)\b\s*[:=]\s*\d", re.IGNORECASE)
_MAE = re.compile(r"\bMAE\b\s*[:=]?\s*\d", re.IGNORECASE)
_CONTRACT = "No athlete-film MAE is published. Fixture heights are not measurements."


def test_labeling_protocol_states_no_mae_and_no_fixture_heights() -> None:
    text = PROTOCOL.read_text()
    assert _CONTRACT in text
    assert "Disputed clips excluded from MAE" in text
    assert _DOLLAR.search(text) is None
    assert _PERCENTILE.search(text) is None
    assert _MAE.search(text) is None
    assert "composite" not in text.lower()


def test_golden_readme_keeps_fixture_heights_as_stand_ins() -> None:
    text = README.read_text()
    assert "made-up scale stand-ins" in text
    assert "never copy them onto a real clip" in text
    assert "Do not" in text and "fill them with guesses" in text
    assert _DOLLAR.search(text) is None
    assert _PERCENTILE.search(text) is None
    assert _MAE.search(text) is None


def test_live_gate_does_not_echo_fixture_heights() -> None:
    blob = json.dumps(gates.gate_state())
    assert "185" not in blob
    assert "183" not in blob
    assert gates.gate_state()["status"] == "blocked_on_golden_set"
