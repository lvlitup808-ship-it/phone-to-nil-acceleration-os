"""Honesty pin: a coach label cannot be saved on a clip with no film on disk.

docs/film_first.md counts only real film. Fixture manifest rows (present false,
or present true with no file) must not get a label file that looks like a
golden-set save.
"""

from __future__ import annotations

import json

import pytest
from fastapi.testclient import TestClient

from services.api.app import app
from services.golden_set import labels

client = TestClient(app)

WR_EVENTS = ["motion_start", "first_step", "second_step", "release", "peak_velocity"]
WR_CUES = [
    "first_step_separation",
    "shin_angle_at_contact",
    "hip_height_at_contact",
    "ground_contact_time_first_step",
    "lean_at_release",
    "arm_drive_symmetry",
]


@pytest.fixture
def golden(tmp_path, monkeypatch):
    (tmp_path / "labels").mkdir()
    (tmp_path / "clips").mkdir()
    manifest = {
        "labeling_protocol_version": "1.0.0",
        "clips": [
            {
                "clip_id": "clp_0301",
                "position_target": "WR",
                "movement": "release",
                "camera_side": {"path": "clips/clp_0301_side.mp4", "present": False},
            },
            {
                "clip_id": "clp_0302",
                "position_target": "WR",
                "movement": "release",
                "camera_side": {"path": "clips/clp_0302_side.mp4", "present": True},
            },
        ],
    }
    (tmp_path / "manifest.json").write_text(json.dumps(manifest))
    monkeypatch.setattr(labels, "GOLDEN_DIR", tmp_path)
    return tmp_path


def _body(clip_id: str, **over: object) -> dict:
    body = {
        "clip_id": clip_id,
        "coach_id": "coach_ab",
        "events": {name: {"t_ms": 100 * (i + 1)} for i, name in enumerate(WR_EVENTS)},
        "cues": {name: {"value": 1.0} for name in WR_CUES},
    }
    body.update(over)
    return body


def test_fixture_clip_cannot_be_labeled(golden):
    response = client.post("/golden/labels", json=_body("clp_0301"))
    assert response.status_code == 409, response.text
    assert "no film" in response.json()["detail"]
    assert list((golden / "labels").glob("*.json")) == []


def test_present_flag_without_file_cannot_be_labeled(golden):
    response = client.post("/golden/labels", json=_body("clp_0302"))
    assert response.status_code == 409, response.text
    assert list((golden / "labels").glob("*.json")) == []


def test_excluded_flag_does_not_bypass_missing_film(golden):
    response = client.post(
        "/golden/labels",
        json=_body("clp_0301", events={}, cues={}, excluded=True),
    )
    assert response.status_code == 409, response.text
    assert list((golden / "labels").glob("*.json")) == []
