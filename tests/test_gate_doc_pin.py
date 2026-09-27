"""Pin Slice-3 gate thresholds in docs/film_first.md to GOLDEN_SET_GATE constants."""

import re
from pathlib import Path

from services.api.gates import GOLDEN_SET_GATE

ROOT = Path(__file__).resolve().parents[1]
DOC = (ROOT / "docs/film_first.md").read_text()


def test_film_first_gate_numbers_match_constants():
    # "Slice 3 gate: 10 WR + 10 DB, 3 surfaces, 2 lighting, 3 athletes/position, 2 coaches on 4 clips."
    # "... requires disputed clips <= 2."
    m = re.search(
        r"Slice 3 gate:\s*(\d+)\s*WR\s*\+\s*(\d+)\s*DB,\s*(\d+)\s*surfaces,\s*(\d+)\s*lighting,\s*"
        r"(\d+)\s*athletes/position,\s*2 coaches on\s*(\d+)\s*clips",
        DOC,
    )
    assert m, "film_first.md missing Slice 3 gate sentence"
    wr, db, surfaces, lighting, athletes, inter = map(int, m.groups())
    assert wr == GOLDEN_SET_GATE["wr_labeled_min"]
    assert db == GOLDEN_SET_GATE["db_labeled_min"]
    assert surfaces == GOLDEN_SET_GATE["surfaces_min"]
    assert lighting == GOLDEN_SET_GATE["lighting_min"]
    assert athletes == GOLDEN_SET_GATE["athletes_per_position_min"]
    assert inter == GOLDEN_SET_GATE["inter_rater_clips_min"]

    d = re.search(r"disputed clips\s*<=\s*(\d+)", DOC)
    assert d, "film_first.md missing disputed <= N"
    assert int(d.group(1)) == GOLDEN_SET_GATE["disputed_max"]
