"""Dependabot Next 16 / React 19 stay unmerged.

Coach console stays on Next 14 and React 18 until an owner-approved
migration. This test fails if package.json majors land via #9 #10 #11.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "apps" / "coach-console" / "package.json"


def _major(spec: str) -> int:
    digits = spec.lstrip("^~>=<")
    return int(digits.split(".")[0])


def test_coach_console_stays_off_next_16_and_react_19():
    data = json.loads(PKG.read_text())
    deps = data["dependencies"]
    assert _major(deps["next"]) == 14, deps["next"]
    assert _major(deps["react"]) == 18, deps["react"]
    assert _major(deps["react-dom"]) == 18, deps["react-dom"]
