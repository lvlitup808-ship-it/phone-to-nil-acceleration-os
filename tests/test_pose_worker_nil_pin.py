"""Honesty: Slice 2 worker output is cues, not a valuation.

`run_pose_assessment` is the path under POST /pose/assess. Fixture mode (no
frames) and the real-frame error path must not publish p25/p50/p75, MAE, a
composite, or a dollar band. Fixture cue numbers are not coach-labeled accuracy.
"""

from __future__ import annotations

import json

import numpy as np

from services.cv_worker.pipeline_v2 import run_pose_assessment

_FORBIDDEN = ("p25", "p50", "p75", "mae", "composite", "nil_band", "nil_dollars")


def _assert_no_valuation(body: object) -> None:
    if isinstance(body, dict):
        for key, value in body.items():
            assert key.lower() not in _FORBIDDEN, key
            assert not (isinstance(value, str) and "$" in value and any(c.isdigit() for c in value))
            _assert_no_valuation(value)
    elif isinstance(body, list):
        for item in body:
            _assert_no_valuation(item)


def test_fixture_pose_worker_is_not_a_valuation() -> None:
    for movement in ("release", "break"):
        out = run_pose_assessment(movement=movement, clip_id=f"clp_worker_{movement}", frames=None)
        assert out["pose_source"] == "fixture"
        assert out["golden_set"] == "pending"
        assert out["movement"] == movement
        assert "mae" not in out
        assert out.get("nil_band") is None
        for cue in out["cues"]:
            assert "mae" not in cue
            assert cue.get("coach_labeled") is not True
        blob = json.dumps(out)
        assert "$" not in blob
        _assert_no_valuation(out)


def test_real_frame_error_path_does_not_invent_a_band() -> None:
    frames = [np.zeros((8, 8, 3), dtype=np.uint8) for _ in range(6)]
    out = run_pose_assessment(movement="release", clip_id="clp_worker_error", frames=frames)
    assert out["pose_source"] == "error"
    assert out["assessment_status"] == "error"
    assert out["cues"] == []
    assert out["golden_set"] == "pending"
    assert out.get("nil_band") is None
    assert "mae" not in out
    _assert_no_valuation(out)
    assert "$" not in out.get("pose_error", "")
