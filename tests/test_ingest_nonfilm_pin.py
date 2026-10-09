"""Pin ingest so a claimed pair or a non-finite number is not a filmed clip.

validate_ingest treated pair_complete=True as proof of side+45, so an empty
angle list was accepted. NaN fails every comparison, so NaN fps and duration
were accepted too. Neither is a phone capture. A single angle with the pair
claim still accepts: POST /upload sends one file. Gate stays closed.
"""

from __future__ import annotations

from packages.capture.contract import validate_ingest


def test_pair_complete_does_not_waive_an_empty_angle_list() -> None:
    decision = validate_ingest(
        fps=60,
        duration_s=8,
        angles=[],
        stable_first_500ms=True,
        pair_complete=True,
    )
    assert decision.accepted is False
    assert "missing_side_or_45" in decision.reasons


def test_pair_complete_still_accepts_one_upload_angle() -> None:
    decision = validate_ingest(
        fps=60,
        duration_s=8,
        angles=["side"],
        stable_first_500ms=True,
        pair_complete=True,
    )
    assert decision.accepted is True
    assert decision.reasons == []


def test_non_finite_fps_and_duration_are_not_a_capture() -> None:
    decision = validate_ingest(
        fps=float("nan"),
        duration_s=float("nan"),
        angles=["side", "fortyfive"],
        stable_first_500ms=True,
        pair_complete=True,
    )
    assert decision.accepted is False
    assert "fps_below_30" in decision.reasons
    assert "duration_not_4_to_12s" in decision.reasons


def test_real_pair_still_accepts() -> None:
    decision = validate_ingest(
        fps=60,
        duration_s=8,
        angles=["side", "45"],
        stable_first_500ms=True,
        pair_complete=True,
    )
    assert decision.accepted is True
    assert decision.reasons == []
