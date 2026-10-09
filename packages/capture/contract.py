from __future__ import annotations

import math
from dataclasses import dataclass, field


@dataclass
class IngestDecision:
    accepted: bool
    reasons: list[str] = field(default_factory=list)
    retake_instruction: str | None = None


def _finite_number(value: object) -> float | None:
    """A capture measurement is a finite number. bool is not a frame rate."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    number = float(value)
    if not math.isfinite(number):
        return None
    return number


def validate_ingest(
    *,
    fps: float,
    duration_s: float,
    angles: list[str],
    stable_first_500ms: bool,
    pair_complete: bool | None = None,
) -> IngestDecision:
    """Reject a capture that is not 4-12s, 30fps+, still at the start.

    pair_complete=True is how POST /upload accepts one angle file. It is not
    proof that an empty angle list is side+45. NaN fails every comparison, so
    a non-finite fps or duration is not a filmed clip.
    """
    reasons: list[str] = []
    fps_n = _finite_number(fps)
    duration_n = _finite_number(duration_s)
    if fps_n is None or fps_n < 30:
        reasons.append("fps_below_30")
    if duration_n is None or duration_n < 4 or duration_n > 12:
        reasons.append("duration_not_4_to_12s")
    needed = {"side", "fortyfive"}
    have: set[str] = set()
    if isinstance(angles, list):
        for angle in angles:
            if isinstance(angle, str):
                have.add(angle.replace("45", "fortyfive"))
    known = have & needed
    # A claimed pair still needs at least one real angle on this request.
    # Without that claim, both side and 45 are required.
    pair_missing = pair_complete is not True or not known
    if pair_missing and not needed.issubset(have):
        reasons.append("missing_side_or_45")
    if stable_first_500ms is not True:
        reasons.append("phone_unstable_first_500ms")
    if not reasons:
        return IngestDecision(True, [])
    return IngestDecision(
        False,
        reasons,
        "Reshoot both angles, 5-10 seconds, 30fps+, hold still for the first half-second, then the athlete goes.",
    )
