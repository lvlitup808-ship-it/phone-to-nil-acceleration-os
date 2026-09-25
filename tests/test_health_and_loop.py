from fastapi.testclient import TestClient

from packages.judgment.client import three_question_test
from services.api.app import app
from services.cv_worker.pipeline import run_stub
from services.valuation.engine import estimate_band

client = TestClient(app)


def test_three_question_test():
    assert three_question_test(bounded=True, glanceable=True, high_volume=True)
    assert not three_question_test(bounded=False, glanceable=True, high_volume=True)


def test_health():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_capture_assess_prescribe_nil():
    up = client.post(
        "/upload",
        json={
            "athlete_id": "a1",
            "angle": "side",
            "quality_score": 0.9,
            "blur": 0.05,
            "uri": "demo://side",
        },
    )
    assert up.status_code == 200
    clip_id = up.json()["clip_id"]
    assessed = client.post(
        "/assess",
        json={"clip_ids": [clip_id], "athlete_id": "a1", "template": "wr_release"},
    )
    assert assessed.status_code == 200
    aid = assessed.json()["id"]
    assert 1 <= len(assessed.json()["cues"]) <= 8
    report = client.get(f"/report/{aid}")
    assert report.status_code == 200
    prep = client.get(f"/prescribe/{aid}")
    assert prep.status_code == 200
    band = client.get("/nil-band/a1")
    body = band.json()
    assert body["p25"] <= body["p50"] <= body["p75"]
    assert body["disclaimer_version"]
    assert body["assumptions"]


def test_cv_stub():
    out = run_stub()
    assert out["quality"]["usable"] is True
    assert "first_step" in out["events"]


def test_valuation_is_a_range():
    band = estimate_band("a1")
    assert band.p25 < band.p75
    assert "synthetic" in " ".join(band.assumptions)
