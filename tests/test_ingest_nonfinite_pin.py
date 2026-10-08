"""Honesty pin: non-finite capture numbers are not a valid clip.

float('nan') < 30 is False in Python, so a NaN fps used to pass
validate_ingest. Infinity duration did too. Those are not 30fps+ / 4-12s
film. Map them onto the existing retake codes; do not invent a new reason.
"""

from __future__ import annotations

import math

from packages.capture.contract import validate_ingest

GOOD = {
    "angles": ["side", "fortyfive"],
    "stable_first_500ms": True,
}


def test_nan_fps_is_below_30() -> None:
    decision = validate_ingest(fps=math.nan, duration_s=8, **GOOD)
    assert decision.accepted is False
    assert "fps_below_30" in decision.reasons


def test_infinite_duration_is_out_of_range() -> None:
    decision = validate_ingest(fps=60, duration_s=math.inf, **GOOD)
    assert decision.accepted is False
    assert "duration_not_4_to_12s" in decision.reasons


def test_nan_duration_is_out_of_range() -> None:
    decision = validate_ingest(fps=60, duration_s=math.nan, **GOOD)
    assert decision.accepted is False
    assert "duration_not_4_to_12s" in decision.reasons
    assert "fps_below_30" not in decision.reasons
