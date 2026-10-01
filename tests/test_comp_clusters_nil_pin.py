"""Honesty: sample comps and the evidence pipeline must not mint NIL bands.

`data/samples/comp_clusters.json` is loaded into every report evidence pack.
A numeric p25/p50/p75/n here would look like a valuation even while the gate
is closed. This pin does not open the gate and does not invent numbers.
"""

from __future__ import annotations

import json
from pathlib import Path

from packages.evidence.pipeline import EvidencePipeline

ROOT = Path(__file__).resolve().parents[1]
COMPS = ROOT / "data" / "samples" / "comp_clusters.json"
BAND_KEYS = ("p25", "p50", "p75", "n")


def test_sample_comp_clusters_stay_placeholder_null():
    rows = json.loads(COMPS.read_text())
    assert rows, "expected placeholder clusters so a numeric leak is visible"
    for row in rows:
        assert row.get("status") == "placeholder"
        for key in BAND_KEYS:
            assert row.get(key) is None, f"{row.get('id')}.{key}"
        assumptions = " ".join(row.get("assumptions") or []).lower()
        assert "no comp data" in assumptions
        blob = json.dumps(row)
        assert "$" not in blob
        assert "mae" not in blob.lower()
        assert "composite" not in blob.lower()


def test_evidence_pipeline_comps_stay_null():
    out = EvidencePipeline().run("wr release recruiting band", "shin_angle_at_contact")
    comps = out.get("comps") or []
    assert comps, "pipeline should surface the placeholder clusters"
    for comp in comps:
        assert comp.get("status") == "placeholder"
        for key in BAND_KEYS:
            assert comp.get(key) is None
        assert "$" not in json.dumps(comp)
