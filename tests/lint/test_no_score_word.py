from pathlib import Path

# Built by concatenation so this file does not match its own ban list.
FORBIDDEN = tuple(f"{prefix}_{'score'}" for prefix in ("overall", "composite", "athlete", "readiness"))
ROOT = Path(__file__).resolve().parents[2]
SKIP = {".git", "node_modules", ".venv", "logs", "artifacts", "__pycache__"}
SUFFIXES = {".py", ".ts", ".tsx", ".md", ".json"}


def test_no_composite_metric_identifier():
    hits = []
    for path in ROOT.rglob("*"):
        if any(part in SKIP for part in path.parts):
            continue
        if path.suffix not in SUFFIXES or not path.is_file():
            continue
        text = path.read_text(errors="ignore")
        for token in FORBIDDEN:
            if token in text:
                hits.append(f"{path}:{token}")
    assert hits == [], hits


def test_ban_list_is_not_empty():
    assert len(FORBIDDEN) == 4
    assert all(t.endswith("_score") for t in FORBIDDEN)
