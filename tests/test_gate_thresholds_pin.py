"""Honesty pin: golden-set gate thresholds match film_first.md and stay closed at zero.

The live /gates/golden missing list must name the exact counts from
docs/film_first.md (10 WR, 10 DB, 3 surfaces, 2 lighting, 3 athletes per
position) while no real labeled film exists. Changing a threshold in code
without updating the film-first doc or this pin fails the test.
"""

from __future__ import annotations

import re
from pathlib import Path

from services.api import gates

ROOT = Path(__file__).resolve().parents[1]
FILM_FIRST = (ROOT / "docs/film_first.md").read_text()


def test_film_first_md_states_the_thresholds():
    assert re.search(r"10 WR \+ 10 DB", FILM_FIRST)
    assert re.search(r"3 surfaces", FILM_FIRST)
    assert re.search(r"2 lighting", FILM_FIRST)
    assert re.search(r"3 athletes/position", FILM_FIRST)


def test_live_gate_missing_names_exact_zero_thresholds():
    state = gates.gate_state()
    assert state["status"] == "blocked_on_golden_set"
    missing = set(state["missing"])
    expected = {
        "wr_labeled 0/10",
        "db_labeled 0/10",
        "inter_rater",
        "surfaces 0/3",
        "lighting 0/2",
        "wr_athletes 0/3",
        "db_athletes 0/3",
    }
    assert missing == expected, f"missing set drifted: {sorted(missing)}"
    assert state["progress"]["wr_labeled"] == 0
    assert state["progress"]["db_labeled"] == 0
