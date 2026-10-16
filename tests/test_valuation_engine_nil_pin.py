"""Honesty pin: the valuation engine must never hardcode a NIL number.

`services/valuation/engine.py` is the only place that builds a NILBand.
Until a sourced comp dataset exists and the golden-set gate opens, every
call must return null p25/p50/p75/confidence and status schema_only.
This test fails if a future change hardcodes a dollar, a numeric percentile,
or a composite into the engine.
"""

from __future__ import annotations

import re
from pathlib import Path

from services.valuation.engine import estimate_band

ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / "services" / "valuation" / "engine.py"

_DOLLAR = re.compile(r"\$\s*\d")
_PERCENTILE = re.compile(r"\b(p25|p50|p75)\b\s*[:=]\s*\d", re.IGNORECASE)
_MAE = re.compile(r"\bMAE\b\s*[:=]\s*\d", re.IGNORECASE)
_COMPOSITE = re.compile(r"\bcomposite\s*[:=]\s*\d", re.IGNORECASE)


def test_estimate_band_returns_nulls() -> None:
    band = estimate_band("ath_test", template="wr_release", school_level="hs")
    assert band.p25 is None
    assert band.p50 is None
    assert band.p75 is None
    assert band.confidence is None
    assert band.status == "schema_only"
    assert band.comp_cluster_ids == []
    blob = band.model_dump_json()
    assert "$" not in blob
    assert "mae" not in blob.lower()
    assert "composite" not in blob.lower()


def test_valuation_engine_source_has_no_hardcoded_numbers() -> None:
    text = ENGINE.read_text()
    assert _DOLLAR.search(text) is None
    assert _PERCENTILE.search(text) is None
    assert _MAE.search(text) is None
    assert _COMPOSITE.search(text) is None
    assert "p25=None" in text or "p25 = None" in text or "p25: int | None = None" not in text  # allow the model default, but engine must not assign numbers
    # engine itself must not assign a number
    assert not re.search(r"p2[57]\s*=\s*\d", text)
    assert not re.search(r"p50\s*=\s*\d", text)
