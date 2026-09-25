from __future__ import annotations

from packages.shared.models import NILBand

DISCLAIMER = "2026-09-24"


def estimate_band(athlete_id: str, template: str = "wr_release", school_level: str = "hs") -> NILBand:
    tables = {
        ("wr_release", "hs"): (2500, 6000, 14000),
        ("db_break", "hs"): (2000, 5000, 12000),
        ("wr_release", "g5"): (8000, 22000, 55000),
        ("db_break", "g5"): (7000, 18000, 48000),
    }
    p25, p50, p75 = tables.get((template, school_level), (1500, 4000, 9000))
    return NILBand(
        athlete_id=athlete_id,
        p25=p25,
        p50=p50,
        p75=p75,
        confidence=0.41,
        assumptions=[
            f"template={template}",
            f"school_level={school_level}",
            "sample is synthetic seed comps, not a live market feed",
            "does not include agency fees, taxes, or school-specific policy",
        ],
        comp_cluster_ids=["cluster_wr_acc_hs_a", "cluster_skill_g5_b"],
        disclaimer_version=DISCLAIMER,
        counterfactuals={
            "if_nickel_db": {"p25": int(p25 * 0.85), "p75": int(p75 * 0.9)},
            "if_slot_wr": {"p25": p25, "p75": p75},
        },
    )
