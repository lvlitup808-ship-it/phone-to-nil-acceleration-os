"""Honesty: coach label save and spec carry no NIL numbers or MAE.

A label is a coach timestamp and cue judgment. It is not a valuation and
not an accuracy claim against the model. The response, the spec, and the
on-disk record must not publish p25/p50/p75, MAE, a composite, or a dollar band.
Saving a label also must not open the live golden-set gate.
"""

from __future__ import annotations

import json

import pytest
from fastapi.testclient import TestClient

from services.api import gates
from services.api.app import app
from services.golden_set import labels

client = TestClient(app)

_FORBIDDEN = ("p25", "p50", "p75", "mae", "composite", "nil_band", "nil_dollars")

WR_EVENTS = ["motion_start", "first_step", "second_step", "release", "peak_velocity"]
WR_CUES = [
    "first_step_separation",
    "shin_angle_at_contact",
    "hip_height_at_contact",
    "ground_contact_time_first_step",
    "lean_at_release",
    "arm_drive_symmetry",
]


def _assert_no_valuation(body: object) -> None:
    if isinstance(body, dict):
        for key, value in body.items():
            assert key.lower() not in _FORBIDDEN, key
            assert not (isinstance(value, str) and "$" in value and any(c.isdigit() for c in value))
            _assert_no_valuation(value)
    elif isinstance(body, list):
        for item in body:
            _assert_no_valuation(item)


@pytest.fixture
def golden(tmp_path, monkeypatch):
    (tmp_path / "labels").mkdir()
    (tmp_path / "clips").mkdir()
    (tmp_path / "clips" / "clp_0100_side.mp4").write_bytes(b"x")
    manifest = {
        "labeling_protocol_version": "1.0.0",
        "golden_set": "pending",
        "clips": [
            {
                "clip_id": "clp_0100",
                "athlete_id": "ath_0100",
                "position_target": "WR",
                "movement": "release",
                "surface": "turf",
                "lighting": "daylight",
                "camera_side": {"path": "clips/clp_0100_side.mp4", "fps": 60, "present": True},
            }
        ],
    }
    (tmp_path / "manifest.json").write_text(json.dumps(manifest))
    monkeypatch.setattr(labels, "GOLDEN_DIR", tmp_path)
    return tmp_path


def _body() -> dict:
    return {
        "clip_id": "clp_0100",
        "coach_id": "coach_ab",
        "events": {name: {"t_ms": 100 * (i + 1)} for i, name in enumerate(WR_EVENTS)},
        "cues": {name: {"value": 1.0} for name in WR_CUES},
        "notes": "coach timestamps only",
    }


def test_label_spec_has_no_valuation_fields(golden) -> None:
    response = client.get("/golden/labels/clp_0100/spec")
    assert response.status_code == 200
    spec = response.json()
    assert spec["movement"] == "release"
    assert spec["events"] == WR_EVENTS
    assert "mae" not in spec
    assert spec.get("nil_band") is None
    _assert_no_valuation(spec)


def test_saved_label_is_not_a_valuation_and_does_not_open_the_gate(golden) -> None:
    response = client.post("/golden/labels", json=_body())
    assert response.status_code == 201, response.text
    body = response.json()
    assert body["path"] == "labels/clp_0100_coach_ab.json"
    assert body["label"]["coach_id"] == "coach_ab"
    assert "mae" not in body["label"]
    assert body["label"].get("accuracy") is None
    _assert_no_valuation(body)

    saved = json.loads((golden / "labels" / "clp_0100_coach_ab.json").read_text())
    assert saved["labeling_protocol_version"] == "1.0.0"
    assert "mae" not in saved
    _assert_no_valuation(saved)

    progress = gates.get_progress(golden)
    assert progress["wr_labeled"] == 1

    live = client.get("/gates/golden")
    assert live.status_code == 200
    state = live.json()
    assert state["status"] == "blocked_on_golden_set"
    assert state.get("status") != "open"
    _assert_no_valuation(state)


def test_valuation_guard_rejects_a_dollar_band() -> None:
    with pytest.raises(AssertionError):
        _assert_no_valuation({"p25": 1000})
