from __future__ import annotations

import json
from pathlib import Path

from packages.shared.slice2 import Slice2Cue
from services.cv_worker.pipeline_v2 import run_pose_assessment

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / "docs/validation/slice2_report.md"


def test_wr_six_cues_and_status():
    out = run_pose_assessment(movement="release", clip_id="clp_0001", height_cm=185)
    assert len(out["cues"]) == 6
    assert [c["name"] for c in out["cues"]][0] == "first_step_separation"
    assert out["golden_set"] == "pending"


def test_db_six_cues():
    out = run_pose_assessment(movement="break", clip_id="clp_0002", height_cm=183)
    assert len(out["cues"]) == 6
    assert out["cues"][0]["name"] == "pad_level_at_break"


def test_uncalibrated_never_emits_a_number():
    out = run_pose_assessment(movement="release", clip_id="clp_x", height_cm=None)
    for cue in out["cues"]:
        model = Slice2Cue.model_validate(cue)
        if model.cue_status.value == "uncalibrated":
            assert model.value is None


def test_pose_api_additive():
    from fastapi.testclient import TestClient
    from services.api.app import app

    c = TestClient(app)
    res = c.post("/pose/assess", json={"athlete_id": "a1", "clip_id": "clp_0001", "movement": "release", "height_cm": 185})
    assert res.status_code == 200
    body = res.json()
    assert "assessment_status" in body
    assert not [k for k in body if k.endswith("_score")]


def test_golden_harness_writes_pending_report():
    manifest = json.loads((ROOT / "data/golden_set/manifest.json").read_text())
    lines = [
        "# Slice 2 validation report",
        "",
        f"golden_set: {manifest.get('golden_set')}",
        "real_mp4_present: false",
        "Do not treat this file as a performance claim.",
        "",
    ]
    for clip in manifest["clips"]:
        movement = "release" if clip["movement"] == "release" else "break"
        out = run_pose_assessment(movement=movement, clip_id=clip["clip_id"], height_cm=clip.get("athlete_height_cm"))
        lines.append(f"- {clip['clip_id']}: status={out['assessment_status']} cues={len(out['cues'])} source=fixture")
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(lines) + "\n")
    assert "pending" in REPORT.read_text()


def test_pose_api_rejects_path_traversal(tmp_path):
    from fastapi.testclient import TestClient

    from services.api.app import app

    c = TestClient(app)
    for bad in ("../../tmp/x", "a/b", "..", "clp 1"):
        res = c.post("/pose/assess", json={"athlete_id": "a1", "clip_id": bad, "movement": "release"})
        assert res.status_code == 422, bad
    assert not (tmp_path.parent / "tmp").exists()
