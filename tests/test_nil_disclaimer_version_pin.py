"""Honesty pin: NIL disclaimer version stays the known placeholder date.

No sourced comp dataset exists. The engine must keep disclaimer_version
at the schema-only stamp and must not embed dollar amounts or percentiles
in assumptions. This does not invent NIL numbers or open the gate.
"""

from __future__ import annotations

from services.valuation.engine import DISCLAIMER, estimate_band


def test_disclaimer_version_is_schema_stamp():
    assert DISCLAIMER == "2026-09-24"
    band = estimate_band("ath_test")
    assert band.disclaimer_version == DISCLAIMER
    assert band.status == "schema_only"
    for assumption in band.assumptions:
        lowered = assumption.lower()
        assert "$" not in assumption
        assert "percent" not in lowered
        assert "p25" not in lowered
        assert "p50" not in lowered
        assert "p75" not in lowered
        # No invented dollar or MAE language.
        assert "mae" not in lowered
        assert "composite" not in lowered
