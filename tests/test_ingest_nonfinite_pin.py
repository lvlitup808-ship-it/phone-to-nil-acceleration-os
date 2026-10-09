"""Honesty pin: a non-finite capture claim is not a usable ingest.

NaN is not < 30 and not outside 4-12, so a bare comparison accepted it.
Infinity fps is not below 30 either. Neither is a phone clip.
"""

from __future__ import annotations

import math

from fastapi.testclient import TestClient

from packages.capture.contract import validate_ingest
from services.api.app import app

client = TestClient(app)


def test_nan_fps_and_duration_are_not_accepted() -> None:
    decision = validate_ingest(
        fps=math.nan,
        duration_s=math.nan,
        angles=["side", "fortyfive"],
        stable_first_500ms=True,
    )
    assert decision.accepted is False
    assert "fps_below_30" in decision.reasons
    assert "duration_not_4_to_12s" in decision.reasons


def test_infinite_fps_is_not_30fps_plus() -> None:
    decision = validate_ingest(
        fps=math.inf,
        duration_s=8,
        angles=["side", "fortyfive"],
        stable_first_500ms=True,
    )
    assert decision.accepted is False
    assert decision.reasons == ["fps_below_30"]


def test_ingest_check_rejects_nonfinite_json() -> None:
    response = client.post(
        "/ingest/check",
        content=(
            b'{"fps": NaN, "duration_s": Infinity, "angles": ["side", "fortyfive"],'
            b' "stable_first_500ms": true}'
        ),
        headers={"content-type": "application/json"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["accepted"] is False
    assert "fps_below_30" in body["reasons"]
    assert "duration_not_4_to_12s" in body["reasons"]
    assert body["retake_instruction"]
