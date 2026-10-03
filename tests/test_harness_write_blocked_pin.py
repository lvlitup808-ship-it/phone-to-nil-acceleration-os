"""Honesty pin: harness --write cannot stamp a validation report while the gate is closed.

`python -m services.golden_set.harness` may print the fixture honesty line.
`--write` must refuse while golden_set is pending or no real film is on disk,
so a nightly job cannot rewrite docs/validation/slice2_report.md as if it measured athletes.
"""

from __future__ import annotations

from pathlib import Path

from services.golden_set.harness import main

ROOT = Path(__file__).resolve().parents[1]
NIGHTLY = ROOT / ".github" / "workflows" / "golden-nightly.yml"


def test_harness_write_refuses_while_golden_set_pending(tmp_path: Path) -> None:
    out = tmp_path / "slice2_report.md"
    code = main(["--write", "--out", str(out)])
    assert code != 0
    assert not out.exists()


def test_golden_nightly_does_not_write_validation_report() -> None:
    text = NIGHTLY.read_text()
    assert "services.golden_set.harness" in text
    assert "--write" not in text
