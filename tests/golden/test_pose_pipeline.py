from __future__ import annotations

from packages.shared.slice2 import Slice2Cue
from services.cv_worker.pipeline_v2 import run_pose_assessment


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


def test_golden_harness_prints_honesty_line_and_writes_pending_report(tmp_path, capsys):
    from services.golden_set.harness import HONESTY_LINE, main

    out = tmp_path / "slice2_report.md"
    assert main(["--write", "--out", str(out)]) == 0
    printed = capsys.readouterr().out
    assert HONESTY_LINE in printed
    assert "do not treat this as athlete validation" in printed.lower()
    text = out.read_text()
    assert text == printed
    assert "golden_set: pending" in text
    assert "real_mp4_present: false" in text
    assert "MAE" not in text.replace("No athlete-film MAE is published", "")


def test_committed_report_matches_harness():
    from services.golden_set.harness import REPORT, build_report

    assert REPORT.read_text() == build_report()


def test_pose_api_rejects_path_traversal(tmp_path):
    from fastapi.testclient import TestClient

    from services.api.app import app

    c = TestClient(app)
    for bad in ("../../tmp/x", "a/b", "..", "clp 1"):
        res = c.post("/pose/assess", json={"athlete_id": "a1", "clip_id": bad, "movement": "release"})
        assert res.status_code == 422, bad
    assert not (tmp_path.parent / "tmp").exists()
