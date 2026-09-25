import numpy as np

from packages.consent.store import ConsentStore
from packages.shared.slice2 import AssessmentStatus, CueStatus
from services.cv_worker.confidence import RETAKE
from services.cv_worker.pipeline_v2 import run_pose_assessment


def test_cue_status_is_subset_of_assessment_status():
    assert {s.value for s in CueStatus} <= {s.value for s in AssessmentStatus}


def test_retake_keys_are_assessment_statuses():
    assert set(RETAKE) <= {s.value for s in AssessmentStatus}


def test_pipeline_emits_only_enum_values():
    for movement in ("release", "break"):
        for height in (185, None):
            out = run_pose_assessment(movement=movement, clip_id="c", height_cm=height)
            AssessmentStatus(out["assessment_status"])
            for cue in out["cues"]:
                CueStatus(cue["cue_status"])


def test_consent_cascade_status_is_in_enum():
    store = ConsentStore()
    c = store.grant("a1", ["capture"])
    row = store.attach({"cues": [1], "events": [1]}, c["consent_id"])
    store.revoke(c["consent_id"], ["clips"])
    AssessmentStatus(store.cascade(row)["assessment_status"])


def test_fixture_run_is_labeled_as_fixture():
    out = run_pose_assessment(movement="release", clip_id="c")
    assert out["pose_source"] == "fixture"
    assert out["versions"]["pose_model_version"] == "fixture_synth_v0"


def test_adapter_failure_on_real_frames_is_error_not_synthetic(monkeypatch):
    monkeypatch.setenv("POSE_ADAPTER", "rtmpose")
    frames = [np.zeros((72, 128, 3), dtype=np.uint8) for _ in range(10)]
    out = run_pose_assessment(movement="release", clip_id="c", frames=frames)
    assert out["assessment_status"] == "error"
    assert out["cues"] == [] and out["events"] == []
    assert out["pose_source"] == "error"
    assert "RTMPose" in out["pose_error"]
