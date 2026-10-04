"""Honesty: shared NILBand defaults and golden-set notes stay number-free.

services/valuation is pinned separately. NILBand in packages/shared is the
shape every caller inherits. A numeric default on p25/p50/p75/confidence
would leak into routes without a valuation edit. The golden-set README sits
next to the fixture manifest; it may describe made-up scale stand-ins and
must not publish a dollar, a numeric percentile, or a measured MAE.
"""

from __future__ import annotations

import re
from pathlib import Path

from packages.shared.models import NILBand
from services.valuation.engine import estimate_band

ROOT = Path(__file__).resolve().parents[1]
GOLDEN_README = ROOT / "data" / "golden_set" / "README.md"
MANIFEST = ROOT / "data" / "golden_set" / "manifest.json"

_DOLLAR = re.compile(r"\$\s*\d")
_PERCENTILE = re.compile(r"\b(p25|p50|p75)\b\s*[:=]\s*\d", re.IGNORECASE)
_MAE = re.compile(r"\bMAE\b\s*[:=]\s*\d", re.IGNORECASE)


def test_nil_band_model_defaults_stay_null() -> None:
    fields = NILBand.model_fields
    for key in ("p25", "p50", "p75", "confidence"):
        assert fields[key].default is None, f"{key} default is {fields[key].default!r}"
    assert fields["status"].default == "schema_only"
    assert fields["currency"].default == "USD"
    factory = fields["counterfactuals"].default_factory
    assert factory is not None
    assert factory() == {}


def test_estimate_band_counterfactuals_empty_and_no_dollars() -> None:
    band = estimate_band("ath_model_pin")
    assert band.counterfactuals == {}
    assert band.p25 is None and band.p50 is None and band.p75 is None
    assert band.confidence is None
    dumped = band.model_dump_json()
    assert _DOLLAR.search(dumped) is None
    assert _PERCENTILE.search(dumped) is None
    assert "no comp dataset" in " ".join(band.assumptions).lower()


def test_golden_set_notes_are_not_a_valuation() -> None:
    readme = GOLDEN_README.read_text()
    manifest = MANIFEST.read_text()
    assert "Fixture labels only" in readme
    assert "made-up" in readme
    assert "film that does not exist" in readme
    assert "No real athlete film" in manifest
    assert "Do not treat as athlete validation" in manifest
    for label, text in (("readme", readme), ("manifest", manifest)):
        assert _DOLLAR.search(text) is None, label
        assert _PERCENTILE.search(text) is None, label
        assert _MAE.search(text) is None, label
