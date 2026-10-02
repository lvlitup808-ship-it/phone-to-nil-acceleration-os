"""Honesty: the retired hard-coded NIL band must not return.

docs/audit/baseline.md records the old bug: GET /nil-band emitted
p25=2500, p50=6000, p75=14000, confidence=0.41 with no comp data.
Those literals must stay out of services/ and packages/. Audit docs may
keep the history. This pin does not open the gate and does not invent
a new band.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BANNED = ("2500", "6000", "14000", "0.41")
SCAN = ("services", "packages")


def test_retired_band_literals_stay_out_of_product_code():
    hits: list[str] = []
    for folder in SCAN:
        for path in (ROOT / folder).rglob("*.py"):
            text = path.read_text()
            for token in BANNED:
                if token in text:
                    hits.append(f"{path.relative_to(ROOT)} contains {token}")
    assert hits == [], hits
