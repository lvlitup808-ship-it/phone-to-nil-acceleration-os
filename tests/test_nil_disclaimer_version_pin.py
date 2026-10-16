"""Honesty pin: NIL band carries the frozen disclaimer_version and no-comp assumptions.

The engine and both band routes must stamp disclaimer_version='2026-09-24'
and must keep the 'no comp dataset' assumption. Changing the stamp or dropping
the assumption would let a future payload look like a live valuation while the
golden-set gate is closed. No numbers are invented.
"""

from __future__ import annotations

from fastapi.testclient import TestClient

from services.api.app import app
from services.valuation.app import app as valuation_app
from services.valuation.engine import DISCLAIMER, estimate_band

client = TestClient(app)
val_client = TestClient(valuation_app)

EXPECTED = "2026-09-24"


def test_engine_disclaimer_version_is_frozen() -> None:
    assert DISCLAIMER == EXPECTED
    band = estimate_band("ath_pin")
    assert band.disclaimer_version == EXPECTED
    assumptions = " ".join(band.assumptions).lower()
    assert "no comp dataset" in assumptions


def test_api_nil_band_carries_disclaimer_version() -> None:
    body = client.get("/nil-band/ath_pin").json()
    assert body["disclaimer_version"] == EXPECTED
    assumptions = " ".join(body.get("assumptions") or []).lower()
    assert "no comp dataset" in assumptions
    assert body["p25"] is None
    assert body["p50"] is None
    assert body["p75"] is None


def test_valuation_service_carries_disclaimer_version() -> None:
    body = val_client.get("/nil-band/ath_pin").json()
    assert body["disclaimer_version"] == EXPECTED
    assumptions = " ".join(body.get("assumptions") or []).lower()
    assert "no comp dataset" in assumptions
    assert body["p25"] is None
