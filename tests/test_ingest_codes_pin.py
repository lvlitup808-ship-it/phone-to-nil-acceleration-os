"""Pin POST /ingest/check reason codes to docs/film_first/retake_templates.md.

Validator wins if they drift. Every ## Reason: heading in the retake packet
must be a code the contract or naming check can emit; every emitted code must
appear as a heading.
"""

import re
from pathlib import Path

from packages.capture.contract import validate_ingest
from services.cv_worker.ingest.naming import validate_name

ROOT = Path(__file__).resolve().parents[1]
DOC = (ROOT / "docs/film_first/retake_templates.md").read_text()

DOC_CODES = set(re.findall(r"^## Reason:\s*(\S+)", DOC, flags=re.M))

CONTRACT_CODES = {
    "fps_below_30",
    "duration_not_4_to_12s",
    "missing_side_or_45",
    "phone_unstable_first_500ms",
}
NAMING_CODE = "bad_filename"
VALIDATOR_CODES = CONTRACT_CODES | {NAMING_CODE}


def test_retake_templates_list_every_validator_code():
    missing = VALIDATOR_CODES - DOC_CODES
    assert not missing, f"missing reason headings: {sorted(missing)}"


def test_retake_templates_has_no_orphan_codes():
    orphans = DOC_CODES - VALIDATOR_CODES
    assert not orphans, f"unknown reason codes: {sorted(orphans)}"


def test_contract_emits_each_contract_code():
    cases = [
        dict(fps=24, duration_s=8, angles=["side", "fortyfive"], stable_first_500ms=True),
        dict(fps=60, duration_s=2, angles=["side", "fortyfive"], stable_first_500ms=True),
        dict(fps=60, duration_s=8, angles=["side"], stable_first_500ms=True),
        dict(fps=60, duration_s=8, angles=["side", "fortyfive"], stable_first_500ms=False),
    ]
    emitted: set[str] = set()
    for kwargs in cases:
        d = validate_ingest(**kwargs)
        emitted.update(d.reasons)
    missing = CONTRACT_CODES - emitted
    assert not missing, f"contract did not emit: {sorted(missing)}"


def test_naming_emits_bad_filename():
    ok, _ = validate_name("ath_0042_WR_release_side_20260925.mp4")
    assert ok is True
    bad, msg = validate_name("clip.mp4")
    assert bad is False
    assert msg is not None
    assert NAMING_CODE in DOC_CODES
