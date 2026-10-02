"""Honesty pin: film-first operator docs must not publish NIL dollars or MAE.

Capture, labeling, and golden-set notes may describe the closed gate and the
protocol. They must not print a dollar band, a numeric percentile, or a
measured MAE. Fixture heights in the golden-set README stay labeled made-up.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILM = ROOT / "docs" / "film_first"
GOLDEN_DOC = ROOT / "docs" / "golden_set" / "labeling_protocol.md"
GOLDEN_README = ROOT / "data" / "golden_set" / "README.md"

_DOLLAR = re.compile(r"\$\s*\d")
_PERCENTILE = re.compile(r"\b(p25|p50|p75)\b\s*[:=]\s*\d", re.IGNORECASE)
_MAE = re.compile(r"\bMAE\b\s*[:=]?\s*\d", re.IGNORECASE)
_ERROR = re.compile(r"\berror_yd\b\s*[:=]\s*\d", re.IGNORECASE)


def _docs() -> list[Path]:
    paths = sorted(FILM.glob("*.md"))
    paths.append(FILM.parent / "film_first.md")
    paths.append(GOLDEN_DOC)
    paths.append(GOLDEN_README)
    return paths


def test_film_first_docs_publish_no_nil_or_mae() -> None:
    offenders: list[str] = []
    for path in _docs():
        assert path.is_file(), path
        text = path.read_text()
        if _DOLLAR.search(text):
            offenders.append(f"{path.relative_to(ROOT)}:dollar")
        if _PERCENTILE.search(text):
            offenders.append(f"{path.relative_to(ROOT)}:percentile")
        if _MAE.search(text):
            offenders.append(f"{path.relative_to(ROOT)}:mae")
        if _ERROR.search(text):
            offenders.append(f"{path.relative_to(ROOT)}:error_yd")
    assert offenders == []


def test_film_first_stays_closed_and_forbids_nil_copy() -> None:
    gate = (FILM.parent / "film_first.md").read_text()
    assert "Do not start Slice 3" in gate
    assert "golden set is pending" in gate
    session = (FILM / "session_1.md").read_text()
    assert "Do not draft NIL band copy." in session
    readme = GOLDEN_README.read_text()
    assert "made-up" in readme
    assert "Fixture labels only" in readme
    assert "film that does not exist" in readme
