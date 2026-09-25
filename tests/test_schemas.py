from fastapi.testclient import TestClient

from packages.shared.models import Cue, NILBand
from packages.shared.schemas import drift
from packages.shared.slice2 import Slice2Assessment
from services.api.app import app

client = TestClient(app)


def test_committed_schemas_match_models():
    assert drift() == []


def test_pose_assess_payload_matches_schema():
    for movement in ("release", "break"):
        body = client.post("/pose/assess", json={"athlete_id": "s1", "clip_id": "clp_s1", "movement": movement}).json()
        Slice2Assessment.model_validate(body)


def test_slice1_assess_cues_match_schema():
    up = client.post("/upload", json={"athlete_id": "s1", "angle": "side", "uri": "demo://s"}).json()
    body = client.post("/assess", json={"clip_ids": [up["clip_id"]], "athlete_id": "s1"}).json()
    for cue in body["cues"]:
        Cue.model_validate(cue)


def test_nil_band_payload_matches_schema():
    NILBand.model_validate(client.get("/nil-band/s1").json())
