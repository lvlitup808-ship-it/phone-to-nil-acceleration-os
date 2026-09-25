"""Clip naming contract.

<athlete_id>_<position>_<movement>_<angle>_<date>.mp4

Examples:
ath_0042_WR_release_side_20260925.mp4
ath_0042_WR_release_45_20260925.mp4
ath_0043_DB_break_side_20260925.mp4
ath_0043_DB_break_45_20260925.mp4
"""

from __future__ import annotations

import re

PATTERN = re.compile(
    r"^(ath_\d{4})_(WR|DB)_(release|break)_(side|45|fortyfive)_(\d{8})\.mp4$"
)
RENAME = "Rename to <athlete_id>_<position>_<movement>_<angle>_<date>.mp4 and re-upload."


def validate_name(filename: str) -> tuple[bool, str | None]:
    if PATTERN.match(filename):
        return True, None
    return False, RENAME
