"""Honesty: the valuation engine must never emit numeric NIL bands.

No sourced comp dataset exists. estimate_band must return schema_only with
every band field null. This pin does not invent numbers and does not open
the golden-set gate.
"""

from __future__ import annotations

from services.valuation.engine import estimate_band


def test_estimate_band_stays_null_and_schema_only():
    band = estimate_band("ath_test", template="wr_release", school_level="hs")
    assert band.status == "schema_only"
    assert band.p25 is None
    assert band.p50 is None
    assert band.p75 is None
    assert band.confidence is None
    assert band.comp_cluster_ids == []
    assumptions = " ".join(band.assumptions).lower()
    assert "no comp dataset" in assumptions
    assert "null" in assumptions
    # Model dump must not contain numeric band values.
    dumped = band.model_dump()
    for key in ("p25", "p50", "p75", "confidence"):
        assert dumped[key] is None
    blob = str(dumped).lower()
    assert "mae" not in blob
    assert "composite" not in blob
