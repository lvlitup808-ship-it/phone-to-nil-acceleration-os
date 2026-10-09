"""/golden/labels persists coach labels to data/golden_set/labels/<clip_id>_<coach_id>.json."""

import json
import re
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from services.api import gates
from services.api.app import app
from services.golden_set import labels

client = TestClient(app)
ROOT = Path(__file__).resolve().parents[1]

WR_EVENTS = ["motion_start", "first_step", "second_step", "release", "peak_velocity"]
WR_CUES = [
    "first_step_separation", "shin_angle_at_contact", "hip_height_at_contact",
    "ground_contact_time_first_step", "lean_at_release", "arm_drive_symmetry",
]


@pytest.fixture
def golden(tmp_path, monkeypatch):
    (tmp_path / "labels").mkdir()
    (tmp_path / "clips").mkdir()
    (tmp_path / "clips" / "clp_0100_side.mp4").write_bytes(b"\x00\x00\x00\x10ftypisom\x00\x00\x00\x00\x00\x00\x00\x09mdatx")
    manifest = {
        "labeling_protocol_version": "1.0.0",
        "clips": [
            {
                "clip_id": "clp_0100", "athlete_id": "ath_0100", "position_target": "WR",
                "movement": "release", "surface": "turf", "lighting": "daylight",
                "camera_side": {"path": "clips/clp_0100_side.mp4", "fps": 60, "present": True},
            },
            {"clip_id": "clp_0200", "position_target": "DB", "movement": "break"},
        ],
    }
    (tmp_path / "manifest.json").write_text(json.dumps(manifest))
    monkeypatch.setattr(labels, "GOLDEN_DIR", tmp_path)
    return tmp_path


def _body(**over):
    body = {
        "clip_id": "clp_0100",
        "coach_id": "coach_ab",
        "events": {name: {"t_ms": 100 * (i + 1)} for i, name in enumerate(WR_EVENTS)},
        "cues": {name: {"value": 1.0} for name in WR_CUES},
    }
    body.update(over)
    return body


def test_spec_lists_frozen_events_and_cues(golden):
    r = client.get("/golden/labels/clp_0100/spec")
    assert r.status_code == 200
    spec = r.json()
    assert spec["movement"] == "release"
    assert spec["events"] == WR_EVENTS
    assert spec["cues"] == WR_CUES
    assert spec["labeling_protocol_version"] == "1.0.0"


def test_save_writes_label_file_with_protocol_version(golden):
    r = client.post("/golden/labels", json=_body())
    assert r.status_code == 201, r.text
    path = golden / "labels" / "clp_0100_coach_ab.json"
    assert path.is_file()
    saved = json.loads(path.read_text())
    assert saved["clip_id"] == "clp_0100" and saved["coach_id"] == "coach_ab"
    assert saved["labeling_protocol_version"] == "1.0.0"
    assert saved["disputed"] is False and saved["excluded"] is False
    assert saved["cues"]["lean_at_release"] == {"value": 1.0, "disputed": False}


def test_saved_label_counts_toward_gate_progress(golden):
    assert gates.get_progress(golden)["wr_labeled"] == 0
    client.post("/golden/labels", json=_body())
    assert gates.get_progress(golden)["wr_labeled"] == 1


def test_coach_id_required(golden):
    body = _body()
    del body["coach_id"]
    assert client.post("/golden/labels", json=body).status_code == 422
    assert client.post("/golden/labels", json=_body(coach_id="")).status_code == 422


@pytest.mark.parametrize("bad", ["../x", "coach_a/b", "coach_a.json", "alice"])
def test_ids_cannot_escape_labels_dir(golden, bad):
    assert client.post("/golden/labels", json=_body(coach_id=bad)).status_code == 422
    assert client.post("/golden/labels", json=_body(clip_id=bad)).status_code == 422
    assert [p.name for p in (golden / "labels").iterdir()] == []


def test_unknown_clip_is_404(golden):
    assert client.post("/golden/labels", json=_body(clip_id="clp_9999")).status_code == 404
    assert client.get("/golden/labels/clp_9999/spec").status_code == 404


def test_append_only(golden):
    assert client.post("/golden/labels", json=_body()).status_code == 201
    r = client.post("/golden/labels", json=_body(cues={n: {"value": 2.0} for n in WR_CUES}))
    assert r.status_code == 409
    saved = json.loads((golden / "labels" / "clp_0100_coach_ab.json").read_text())
    assert saved["cues"]["lean_at_release"]["value"] == 1.0


def test_needs_all_five_events_and_six_cues(golden):
    events = _body()["events"]
    del events["peak_velocity"]
    assert client.post("/golden/labels", json=_body(events=events)).status_code == 422
    cues = _body()["cues"]
    del cues["arm_drive_symmetry"]
    assert client.post("/golden/labels", json=_body(cues=cues)).status_code == 422
    cues = {**_body()["cues"], "cue_number_seven": {"value": 1.0}}
    assert client.post("/golden/labels", json=_body(cues=cues)).status_code == 422
    assert list((golden / "labels").iterdir()) == []


def test_db_cues_rejected_on_wr_clip(golden):
    cues = {"pad_level_at_break": {"value": 1.0}, **{n: {"value": 1.0} for n in WR_CUES[1:]}}
    assert client.post("/golden/labels", json=_body(cues=cues)).status_code == 422


def test_unsure_cue_must_be_marked_disputed(golden):
    cues = {**_body()["cues"], "lean_at_release": {"value": None}}
    assert client.post("/golden/labels", json=_body(cues=cues)).status_code == 422
    cues["lean_at_release"] = {"value": None, "disputed": True}
    assert client.post("/golden/labels", json=_body(cues=cues)).status_code == 201


def test_cannot_label_saves_excluded_without_cues(golden):
    r = client.post("/golden/labels", json=_body(events={}, cues={}, excluded=True))
    assert r.status_code == 201
    saved = json.loads((golden / "labels" / "clp_0100_coach_ab.json").read_text())
    assert saved["excluded"] is True
    assert gates.get_progress(golden)["wr_labeled"] == 0


def test_label_cues_match_cue_freeze_doc():
    text = (ROOT / "docs/product/cue_freeze_v1.md").read_text()
    wr_doc = re.findall(r"^\d\. (\w+)$", text.split("## DB break")[0], flags=re.M)
    db_doc = re.findall(r"^\d\. (\w+)$", text.split("## DB break")[1], flags=re.M)
    assert labels.CUES["release"] == wr_doc
    assert labels.CUES["break"] == db_doc


def test_repo_labels_dir_untouched():
    names = sorted(p.name for p in (ROOT / "data/golden_set/labels").iterdir())
    assert names == ["_template.json"]
