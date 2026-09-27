"""Claude Code skills in .claude/skills must load and keep their hard rules."""

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / ".claude/skills"


def _frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text()
    assert text.startswith("---\n"), f"{path}: no frontmatter"
    head = text.split("---\n", 2)[1]
    return dict(line.split(": ", 1) for line in head.strip().splitlines())


@pytest.mark.parametrize("name", ["accel-os-operator", "accel-os-swe"])
def test_skill_frontmatter(name):
    meta = _frontmatter(SKILLS / name / "SKILL.md")
    assert meta["name"] == name
    assert meta["description"].strip()


def test_swe_skill_keeps_hard_rules():
    text = (SKILLS / "accel-os-swe/SKILL.md").read_text()
    for rule in (
        "Do not invent NIL dollars",
        "Do not start Slice 3",
        "Do not commit athlete video",
        "Do not merge to main or deploy without an explicit owner yes",
        "Do not silently swap real film for fixture poses",
        "A fix is not done until a test fails with the fix reverted",
    ):
        assert rule in text, rule
