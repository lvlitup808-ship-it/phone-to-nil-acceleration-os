from pathlib import Path

FORBIDDEN = ("overall_score", "composite_score", "athlete_score", "readiness_score")
ROOT = Path(__file__).resolve().parents[2]
SKIP = {".git", "node_modules", ".venv", "logs", "artifacts", "__pycache__"}


def test_no_composite_score_identifier():
    hits = []
    for path in ROOT.rglob("*"):
        if any(part in SKIP for part in path.parts):
            continue
        if path.suffix not in {".py", ".ts", ".tsx", ".md"}:
            continue
        text = path.read_text(errors="ignore")
        for token in FORBIDDEN:
            if token in text:
                hits.append(f"{path}:{token}")
    assert hits == [], hits
