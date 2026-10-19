"""Pin that the live golden-set gate stays closed while only fixtures exist."""

from fastapi.testclient import TestClient

from services.api.app import app

client = TestClient(app)


def test_gates_golden_closed_on_current_manifest():
    res = client.get("/gates/golden")
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "closed"
    assert body.get("open") is not True
    # Fixture clips have no film; labeled counts must stay at zero.
    progress = body.get("progress") or {}
    assert progress.get("wr_labeled", 0) == 0
    assert progress.get("db_labeled", 0) == 0
