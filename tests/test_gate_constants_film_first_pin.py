"""Pin golden-set gate constants to docs/film_first.md.

The numbers that open the gate are not a product decision. film_first.md
states 10 WR + 10 DB, 3 surfaces, 2 lighting, 3 athletes per position, and
2 coaches on 4 clips. GOLDEN_SET_GATE must match those numbers exactly.
No invented MAE, no Slice 3, no opened gate.
"""

from __future__ import annotations

import re
from pathlib import Path

from services.api.gates import GOLDEN_SET_GATE, get_progress

ROOT = Path(__file__).resolve().parents[1]
FILM_FIRST = (ROOT / "docs/film_first.md").read_text()


def test_gate_constants_match_film_first() -> None:
    # Slice 3 gate line in film_first.md
    assert "10 WR + 10 DB" in FILM_FIRST
    assert "3 surfaces" in FILM_FIRST
    assert "2 lighting" in FILM_FIRST
    assert "3 athletes/position" in FILM_FIRST
    assert "2 coaches on 4 clips" in FILM_FIRST

    assert GOLDEN_SET_GATE["wr_labeled_min"] == 10
    assert GOLDEN_SET_GATE["db_labeled_min"] == 10
    assert GOLDEN_SET_GATE["surfaces_min"] == 3
    assert GOLDEN_SET_GATE["lighting_min"] == 2
    assert GOLDEN_SET_GATE["athletes_per_position_min"] == 3
    assert GOLDEN_SET_GATE["inter_rater_clips_min"] == 4
    assert GOLDEN_SET_GATE["inter_rater_done"] is True
    assert GOLDEN_SET_GATE["disputed_max"] == 2


def test_live_progress_is_zero_while_no_real_film() -> None:
    progress = get_progress()
    assert progress["wr_labeled"] == 0
    assert progress["db_labeled"] == 0
    assert progress["inter_rater_done"] is False
    assert progress["surfaces"] == 0
    assert progress["lighting_conditions"] == 0
    assert progress["wr_athletes"] == 0
    assert progress["db_athletes"] == 0
