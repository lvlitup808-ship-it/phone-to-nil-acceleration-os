"""Honesty: drill seed and position templates are not a valuation.

`data/samples/drills.json` is loaded into every evidence retrieve. A dollar,
percentile, MAE, or composite on a drill or template would look like a NIL
band even while the golden-set gate is closed. This pin does not open the
gate and does not invent numbers.
"""

from __future__ import annotations

import json
from pathlib import Path

from packages.evidence.pipeline import EvidencePipeline

ROOT = Path(__file__).resolve().parents[1]
DRILLS = ROOT / "data" / "samples" / "drills.json"
TEMPLATES = ROOT / "data" / "samples" / "position_templates.json"
BANNED = ("p25", "p50", "p75", "confidence", "mae", "composite", "percentile")


def _blob(row: object) -> str:
    return json.dumps(row).lower()


def test_drill_seed_has_no_nil_numbers() -> None:
    rows = json.loads(DRILLS.read_text())
    assert rows, "expected a drill seed so a numeric leak is visible"
    reviewed = 0
    for row in rows:
        blob = _blob(row)
        assert "$" not in blob
        for key in BANNED:
            assert key not in blob, f"{row.get('drill_id')} leaks {key}"
        assert "nil" not in blob
        if row.get("coach_reviewed") is True:
            reviewed += 1
            assert row.get("evidence_chunk_ids"), row.get("drill_id")
    assert reviewed >= 1
    drafts = [r for r in rows if r.get("coach_reviewed") is False]
    assert drafts, "unreviewed draft must stay visible so a silent promote fails the pin"
    assert drafts[0].get("evidence_chunk_ids") == []


def test_position_templates_have_no_nil_numbers() -> None:
    templates = json.loads(TEMPLATES.read_text())
    assert set(templates) >= {"wr_release", "db_break"}
    blob = _blob(templates)
    assert "$" not in blob
    for key in BANNED:
        assert key not in blob
    assert "nil" not in blob
    for name, spec in templates.items():
        assert spec.get("cues"), name
        assert spec.get("film"), name
        assert "p25" not in spec


def test_evidence_retrieve_drills_carry_no_band() -> None:
    hits = EvidencePipeline().retrieve("shin wall", cue="shin_angle_at_contact")
    drills = [h for h in hits if h.get("kind") == "drill"]
    assert drills, "expected the wall-shin drill to retrieve"
    for hit in drills:
        blob = _blob(hit)
        assert "$" not in blob
        for key in ("p25", "p50", "p75", "confidence", "mae", "composite"):
            assert key not in hit
            assert key not in blob
