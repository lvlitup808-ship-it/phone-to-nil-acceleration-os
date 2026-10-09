"""Non-finite capture numbers are not a valid phone clip.

float("nan") < 30 is False in IEEE comparisons, so a NaN fps or duration
used to pass validate_ingest. That is not 30fps+ film.
"""

from __future__ import annotations

from packages.capture.contract import validate_ingest


def test_nan_fps_is_rejected() -> None:
    decision = validate_ingest(
        fps=float("nan"),
        duration_s=6.0,
        angles=["side", "fortyfive"],
        stable_first_500ms=True,
    )
    assert decision.accepted is False
    assert "fps_below_30" in decision.reasons


def test_nan_duration_is_rejected() -> None:
    decision = validate_ingest(
        fps=60.0,
        duration_s=float("nan"),
        angles=["side", "fortyfive"],
        stable_first_500ms=True,
    )
    assert decision.accepted is False
    assert "duration_not_4_to_12s" in decision.reasons
