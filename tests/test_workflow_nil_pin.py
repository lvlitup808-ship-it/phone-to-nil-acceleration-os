"""Honesty pin: GitHub Actions workflows are not a NIL band.

Nightly golden and drift jobs print status. They must not echo a dollar,
a numeric percentile, MAE, or a composite. The live contract stays null
until the golden-set gate opens on real labeled film.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"

_DOLLAR = re.compile(r"\$\s*\d")
_PERCENTILE = re.compile(r"\b(p25|p50|p75)\b\s*[:=]\s*\d", re.IGNORECASE)
_MAE = re.compile(r"\bMAE\b\s*[:=]?\s*\d", re.IGNORECASE)
_COMPOSITE = re.compile(r"\bcomposite\s*[:=]\s*\d", re.IGNORECASE)
_LIVE_CONTRACT = "Live contract: NIL p25/p50/p75 are null."


def test_workflows_publish_no_nil_numbers() -> None:
    paths = sorted(WORKFLOWS.glob("*.yml"))
    assert paths, "no workflow files"
    offenders: list[str] = []
    missing: list[str] = []
    for path in paths:
        text = path.read_text()
        rel = str(path.relative_to(ROOT))
        if _LIVE_CONTRACT not in text:
            missing.append(rel)
        if _DOLLAR.search(text):
            offenders.append(f"{rel}:dollar")
        if _PERCENTILE.search(text):
            offenders.append(f"{rel}:percentile")
        if _MAE.search(text):
            offenders.append(f"{rel}:mae")
        if _COMPOSITE.search(text):
            offenders.append(f"{rel}:composite")
    assert missing == [], missing
    assert offenders == [], offenders


def test_golden_nightly_runs_harness_not_a_band() -> None:
    text = (WORKFLOWS / "golden-nightly.yml").read_text()
    assert "python -m services.golden_set.harness" in text
    assert "echo" not in text.lower() or "nil" not in text.lower().split("echo", 1)[-1]
    assert "Do not echo a dollar, MAE, or composite." in text
    assert "blocked_on_golden_set" not in text  # workflow must not pretend the gate opened
