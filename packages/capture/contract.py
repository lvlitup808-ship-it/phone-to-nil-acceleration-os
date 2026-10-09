from __future__ import annotations

import math
from dataclasses import dataclass, field


@dataclass
class IngestDecision:
    accepted: bool
    reasons: list[str] = field(default_factory=list)
    retake_instruction: str | None = None


def _finite_number(value: float) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def validate_ingest(*, fps: float, duration_s: float, angles: list[str], stable_first_500ms: bool, pair_complete: bool | None = None) -> IngestDecision:
    reasons: list[str] = []
    # NaN is not < 30 and not outside 4-12. Infinity fps is not below 30.
    # Neither is a phone clip.
    if not _finite_number(fps) or fps < 30:
        reasons.append("fps_below_30")
    if not _finite_number(duration_s) or duration_s < 4 or duration_s > 12:
        reasons.append("duration_not_4_to_12s")
    needed = {"side", "fortyfive"}
    have = {a.replace("45", "fortyfive") for a in angles}
    pair_missing = pair_complete is False or (pair_complete is None and len(have) < 2)
    if pair_missing and not needed.issubset(have):
        reasons.append("missing_side_or_45")
    if not stable_first_500ms:
        reasons.append("phone_unstable_first_500ms")
    if not reasons:
        return IngestDecision(True, [])
    return IngestDecision(False, reasons, "Reshoot both angles, 5-10 seconds, 30fps+, hold still for the first half-second, then the athlete goes.")
