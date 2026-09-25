from services.api.gates import blocked_reason, prescription_enabled
from services.cv_worker.ingest.naming import validate_name
from services.golden_set.inter_rater import should_trigger_inter_rater


def test_naming_accepts_contract():
    ok, err = validate_name("ath_0042_WR_release_side_20260925.mp4")
    assert ok and err is None


def test_naming_rejects():
    ok, err = validate_name("clip.mp4")
    assert not ok
    assert "Rename to" in err


def test_inter_rater_triggers():
    assert should_trigger_inter_rater(4) is True
    assert should_trigger_inter_rater(5) is False
    assert should_trigger_inter_rater(10) is True
    assert should_trigger_inter_rater(16) is True


def test_gate_blocks_empty_set():
    assert prescription_enabled() is False
    body = blocked_reason()
    assert body["status"] == "blocked_on_golden_set"
    assert "wr_labeled 0/10" in body["missing"]
