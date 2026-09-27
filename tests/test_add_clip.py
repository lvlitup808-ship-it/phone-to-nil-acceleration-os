"""Red-green tests for services.golden_set.add_clip.

A real clip must land in the manifest with athlete_id / surface / lighting set
and present=true cameras. Video bytes themselves are never asserted (gitignored).
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest import mock

import pytest

from packages.shared.golden import GoldenManifest
from services.golden_set import add_clip as add_mod


@pytest.fixture
def golden_root(tmp_path, monkeypatch):
    """Isolate manifest + clips under tmp_path."""
    root = tmp_path
    gs = root / "data" / "golden_set"
    clips = gs / "clips"
    clips.mkdir(parents=True)
    manifest = {
        "schema_version": "1.1.0",
        "golden_set": "pending",
        "note": "test",
        "clips": [
            {
                "clip_id": "clp_0001",
                "athlete_id": None,
                "position_target": "WR",
                "movement": "release",
                "surface": None,
                "lighting": None,
                "camera_side": {"path": "clips/clp_0001_side.mp4", "fps": 60, "present": False},
                "camera_45": {"path": "clips/clp_0001_45.mp4", "fps": 60, "present": False},
                "disputed": False,
                "labels": {},
            }
        ],
    }
    (gs / "manifest.json").write_text(json.dumps(manifest, indent=2))
    monkeypatch.setattr(add_mod, "ROOT", root)
    monkeypatch.setattr(add_mod, "MANIFEST_PATH", gs / "manifest.json")
    monkeypatch.setattr(add_mod, "CLIPS_DIR", clips)
    return root


def test_add_clip_writes_filmed_entry_and_copies_side(golden_root):
    side = golden_root / "incoming_side.mp4"
    side.write_bytes(b"fake-mp4")
    clip, lines = add_mod.add_clip(
        clip_id="clp_0003",
        athlete_id="ath_0007",
        position_target="WR",
        movement="release",
        surface="turf",
        lighting="daylight",
        athlete_height_cm=180.0,
        side_src=side,
        side_fps=60.0,
        fortyfive_src=None,
        fortyfive_fps=None,
        dry_run=False,
    )
    assert clip.clip_id == "clp_0003"
    assert clip.athlete_id == "ath_0007"
    assert clip.surface == "turf"
    assert clip.lighting == "daylight"
    assert clip.camera_side is not None and clip.camera_side.present is True
    assert (golden_root / "data/golden_set/clips/clp_0003_side.mp4").is_file()
    raw = json.loads((golden_root / "data/golden_set/manifest.json").read_text())
    GoldenManifest.model_validate(raw)
    assert any(c["clip_id"] == "clp_0003" for c in raw["clips"])
    assert any("copied side" in ln for ln in lines)


def test_add_clip_rejects_missing_film_sources(golden_root):
    with pytest.raises(SystemExit, match="at least one of --side or --fortyfive"):
        add_mod.add_clip(
            clip_id="clp_0004",
            athlete_id="ath_0001",
            position_target="DB",
            movement="break",
            surface="grass",
            lighting="night_lit",
            athlete_height_cm=None,
            side_src=None,
            side_fps=None,
            fortyfive_src=None,
            fortyfive_fps=None,
        )


def test_add_clip_rejects_duplicate_id(golden_root):
    side = golden_root / "s.mp4"
    side.write_bytes(b"x")
    with pytest.raises(SystemExit, match="already in manifest"):
        add_mod.add_clip(
            clip_id="clp_0001",
            athlete_id="ath_0001",
            position_target="WR",
            movement="release",
            surface="turf",
            lighting="daylight",
            athlete_height_cm=None,
            side_src=side,
            side_fps=30.0,
            fortyfive_src=None,
            fortyfive_fps=None,
        )


def test_cli_dry_run_does_not_write(golden_root):
    side = golden_root / "s.mp4"
    side.write_bytes(b"x")
    rc = add_mod.main(
        [
            "--clip-id", "clp_0009",
            "--athlete-id", "ath_0009",
            "--position", "WR",
            "--movement", "release",
            "--surface", "track",
            "--lighting", "indoor",
            "--side", str(side),
            "--side-fps", "120",
            "--dry-run",
        ]
    )
    assert rc == 0
    raw = json.loads((golden_root / "data/golden_set/manifest.json").read_text())
    assert not any(c["clip_id"] == "clp_0009" for c in raw["clips"])
