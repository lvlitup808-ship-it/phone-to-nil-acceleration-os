import pytest


@pytest.fixture(autouse=True)
def _artifacts_outside_repo(tmp_path, monkeypatch):
    """Keep /pose/assess debug files out of the working tree during tests."""
    monkeypatch.setenv("ARTIFACTS_DIR", str(tmp_path / "artifacts"))
