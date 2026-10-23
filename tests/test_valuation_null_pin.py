"""Honesty pin: valuation engine must never emit numeric NIL bands.

No comp dataset exists. Any p25/p50/p75 or confidence number is an invented claim.
"""

from services.valuation.engine import estimate_band


def test_estimate_band_fields_stay_null():
    band = estimate_band("ath_test")
    assert band.p25 is None
    assert band.p50 is None
    assert band.p75 is None
    assert band.confidence is None
    assert band.status in {"schema_only", "blocked_on_golden_set"}
    assert "no comp dataset" in " ".join(band.assumptions).lower()
    # No dollar or percentile numbers in the payload shape itself
    assert band.comp_cluster_ids == []
