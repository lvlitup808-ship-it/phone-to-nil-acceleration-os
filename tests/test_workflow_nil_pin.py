"""Honesty pin: GitHub workflows are not a NIL band or a deploy.

CI, docs, attachments, feature-drift, and golden-nightly must not print a
dollar amount, a numeric percentile, MAE, or a composite. Golden nightly runs
the fixture harness only. Checkout stays at v7 (Dependabot #8 content is
already on main). No workflow deploys the app.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GITHUB = ROOT / ".github"

_DOLLAR = re.compile(r"\$\s*\d")
_PERCENTILE = re.compile(r"\b(p25|p50|p75)\b\s*[:=]\s*\d", re.IGNORECASE)
_MAE = re.compile(r"\bMAE\b\s*[:=]?\s*\d", re.IGNORECASE)
_COMPOSITE = re.compile(r"\bcomposite\s*[:=]\s*\d", re.IGNORECASE)
_DEPLOY = re.compile(r"\b(vercel|flyctl|kubectl\s+apply|npm\s+run\s+deploy)\b", re.IGNORECASE)


def _github_texts() -> list[tuple[str, str]]:
    paths = sorted(GITHUB.rglob("*"))
    rows: list[tuple[str, str]] = []
    for path in paths:
        if not path.is_file():
            continue
        if path.suffix not in {".yml", ".yaml", ".md"}:
            continue
        rows.append((str(path.relative_to(ROOT)), path.read_text()))
    assert rows, "expected .github workflow and template files"
    return rows


def test_github_config_publishes_no_nil_numbers() -> None:
    offenders: list[str] = []
    for rel, text in _github_texts():
        if _DOLLAR.search(text):
            offenders.append(f"{rel}:dollar")
        if _PERCENTILE.search(text):
            offenders.append(f"{rel}:percentile")
        if _MAE.search(text):
            offenders.append(f"{rel}:mae")
        if _COMPOSITE.search(text):
            offenders.append(f"{rel}:composite")
        if _DEPLOY.search(text):
            offenders.append(f"{rel}:deploy")
    assert offenders == [], offenders


def test_ci_and_nightly_stay_honest() -> None:
    ci = (GITHUB / "workflows" / "ci.yml").read_text()
    nightly = (GITHUB / "workflows" / "golden-nightly.yml").read_text()
    assert "actions/checkout@v7" in ci
    assert "actions/checkout@v4" not in ci
    assert "python -m pytest tests -q" in ci
    assert "python -m services.golden_set.manifest" in ci
    assert "python -m services.golden_set.harness" in nightly
    assert "tests/golden/test_pose_pipeline.py" in nightly
    assert "valuation" not in nightly
    assert "nil-band" not in nightly
    pr = (GITHUB / "PULL_REQUEST_TEMPLATE.md").read_text()
    assert "No guaranteed dollar figures" in pr
    assert "No athlete PII or raw video in this PR" in pr
