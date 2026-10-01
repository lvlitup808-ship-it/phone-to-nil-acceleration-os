"""Honesty: Slice 1 /assess does not invent cue measurements.

README: template cues have no measurement behind them unless `metrics`
are passed. A future change that hardcodes shin angle / GCT / hip height
would look like real film. Values stay null without metrics.
"""

from fastapi.testclient import TestClient

from packages.biomech.features import extract_cues
from packages.shared.models import PositionTemplate
from services.api.app import app

client = TestClient(app)


def test_extract_cues_without_metrics_values_are_null():
    for template in PositionTemplate:
        cues = extract_cues(template, metrics={})
        assert cues, template
        for cue in cues:
            assert cue.value is None, f"{template} {cue.id} invented {cue.value}"
            assert cue.confidence == 0.45


def test_assess_route_without_metrics_leaves_values_null():
    up = client.post(
        "/upload",
        json={"athlete_id": "ath_no_metrics", "angle": "side", "uri": "demo://nm"},
    )
    assert up.status_code == 200
    clip_id = up.json()["clip_id"]
    assessed = client.post(
        "/assess",
        json={"clip_ids": [clip_id], "athlete_id": "ath_no_metrics", "template": "wr_release"},
    )
    assert assessed.status_code == 200
    body = assessed.json()
    assert body["cues"]
    for cue in body["cues"]:
        assert cue.get("value") is None, cue
        assert cue.get("confidence") == 0.45


def test_assess_only_fills_value_when_metric_is_passed():
    cues = extract_cues(PositionTemplate.wr_release, metrics={"shin_angle": 32.0})
    by_id = {c.id.value: c for c in cues}
    assert by_id["shin_angle"].value == 32.0
    assert by_id["hip_height"].value is None
    assert by_id["first_step_separation"].value is None
