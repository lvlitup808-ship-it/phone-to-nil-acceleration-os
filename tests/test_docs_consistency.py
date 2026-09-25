"""Docs that encode contracts must match the code they describe."""

import re
from pathlib import Path

from packages.capture.contract import validate_ingest

ROOT = Path(__file__).resolve().parents[1]


def _validator_codes() -> set[str]:
    bad = validate_ingest(fps=10, duration_s=1, angles=["side"], stable_first_500ms=False, pair_complete=False)
    return set(bad.reasons) | {"bad_filename"}


def test_retake_packet_codes_match_validator():
    text = (ROOT / "docs/film_first/retake_templates.md").read_text()
    documented = set(re.findall(r"^## Reason: (\S+)$", text, flags=re.M))
    assert documented == _validator_codes()


def test_cue_freeze_matches_extractors():
    from services.cv_worker.pipeline_v2 import run_pose_assessment

    text = (ROOT / "docs/product/cue_freeze_v1.md").read_text()
    wr_doc = re.findall(r"^\d\. (\w+)$", text.split("## DB break")[0], flags=re.M)
    db_doc = re.findall(r"^\d\. (\w+)$", text.split("## DB break")[1], flags=re.M)
    wr = [c["name"] for c in run_pose_assessment(movement="release", clip_id="c")["cues"]]
    db = [c["name"] for c in run_pose_assessment(movement="break", clip_id="c")["cues"]]
    assert wr_doc == wr and len(wr) == 6
    assert db_doc == db and len(db) == 6


def test_readme_endpoints_exist():
    from services.api.app import app

    routes = {(m.upper(), path) for path, ops in app.openapi()["paths"].items() for m in ops}
    text = (ROOT / "README.md").read_text()
    listed = set(re.findall(r"^\| `(GET|POST) (/[^`]*)` \|", text, flags=re.M))
    assert listed, "README endpoint table missing"
    assert listed <= routes, listed - routes
    assert routes <= listed, routes - listed
