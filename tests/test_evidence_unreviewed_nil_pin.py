"""Honesty: evidence assembly must not prescribe unreviewed drills or NIL numbers.

The sample library includes an unreviewed draft. Retrieval score is not a
valuation. Comps stay schema placeholders (null quantiles). Gate stays closed.
"""

from __future__ import annotations

import json

from packages.evidence.pipeline import EvidencePipeline


def test_unreviewed_drill_is_not_assembled() -> None:
    pipe = EvidencePipeline()
    out = pipe.run("lean release draft placeholder", "lean_at_release")
    drills = out.get("drills") or []
    ids = {d.get("drill_id") or d.get("id") for d in drills}
    assert "drl_draft_unreviewed" not in ids
    assert "drill_draft_unreviewed" not in ids
    for drill in drills:
        assert drill.get("coach_reviewed") is True


def test_evidence_comps_stay_null_and_carry_no_dollars() -> None:
    pipe = EvidencePipeline()
    out = pipe.run("wr release cluster", "shin_angle")
    comps = out.get("comps") or []
    assert comps, "expected placeholder comps so a numeric leak would be visible"
    blob = json.dumps(out)
    assert "$" not in blob
    for comp in comps:
        assert comp.get("status") == "placeholder"
        assert comp.get("p25") is None
        assert comp.get("p50") is None
        assert comp.get("p75") is None
        assert comp.get("n") is None
