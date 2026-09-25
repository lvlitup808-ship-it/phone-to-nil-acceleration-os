"""NIL / recruiting band.

No real comp data exists yet, so no band can be computed. Every numeric field is
null until a sourced comp dataset lands and the golden-set gate is open. The
response shape (Slice 1) is kept so clients do not break.
"""

from __future__ import annotations

from packages.shared.models import NILBand

DISCLAIMER = "2026-09-24"


def estimate_band(athlete_id: str, template: str = "wr_release", school_level: str = "hs") -> NILBand:
    return NILBand(
        athlete_id=athlete_id,
        p25=None,
        p50=None,
        p75=None,
        confidence=None,
        assumptions=[
            f"template={template}",
            f"school_level={school_level}",
            "no comp dataset exists; band fields are null placeholders",
            "does not include agency fees, taxes, or school-specific policy",
        ],
        comp_cluster_ids=[],
        disclaimer_version=DISCLAIMER,
        counterfactuals={},
        status="schema_only",
    )
