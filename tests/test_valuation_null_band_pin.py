"""Honesty pin: valuation engine never invents a NIL band.

estimate_band is the only place a band could be computed. Until a sourced
comp dataset exists and the golden-set gate opens, every call must return
null percentiles, schema_only status, and an empty comp cluster list.
This test fails if anyone hardcodes a dollar amount or numeric percentile
into services/valuation/engine.py.
"""

from __future__ import annotations

import re
from pathlib import Path

from services.valuation.engine import estimate_band

ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / "services" / "valuation" / "engine.py"

_NUMERIC_BAND = re.compile(r"\b(p25|p50|p75)\s*=\s*\d", re.IGNORECASE)
_DOLLAR = re.compile(r"\$\s*\d")


def test_estimate_band_returns_null_schema_only() -> None:
    band = estimate_band("ath_test", template="wr_release", school_level="hs")
    assert band.p25 is None
    assert band.p50 is None
    assert band.p75 is None
    assert band.confidence is None
    assert band.status == "schema_only"
    assert band.comp_cluster_ids == []
    assert "no comp dataset" in " ".join(band.assumptions).lower()


def test_engine_source_has_no_hardcoded_numbers() -> None:
    text = ENGINE.read_text()
    assert not _NUMERIC_BAND.search(text), "hardcoded numeric band in engine.py"
    assert not _DOLLAR.search(text), "dollar amount in engine.py"
    assert "p25=None" in text
    assert "status=\"schema_only\"" in text
