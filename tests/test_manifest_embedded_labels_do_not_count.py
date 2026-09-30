"""Honesty: labels nested on the fixture manifest clip never count as film.

The live manifest stores placeholder event times under clips[].labels.
Those are fixtures. Gate progress must only count coach label files on
clips with real film on disk (see docs/film_first.md).
"""

from __future__ import annotations

import json
from pathlib import Path

from services.api import gates

ROOT = Path(__file__).resolve().parents[1]


def test_live_manifest_clips_have_embedded_fixture_labels_and_no_film():
    manifest = json.loads((ROOT / "data/golden_set/manifest.json").read_text())
    clips = manifest.get("clips") or []
    assert clips, "manifest has no clips"
    embedded = 0
    for clip in clips:
        labels = clip.get("labels") or {}
        events = labels.get("events") or {}
        if events:
            embedded += 1
        assert gates.has_film(clip, ROOT / "data/golden_set") is False
    assert embedded >= 1, "expected at least one fixture clip with nested labels.events"
    p = gates.get_progress()
    assert p["wr_labeled"] == 0
    assert p["db_labeled"] == 0


def test_embedded_manifest_labels_do_not_count_even_with_present_true(tmp_path):
    clips = [
        {
            "clip_id": "clp_fix",
            "position_target": "WR",
            "athlete_id": "ath_x",
            "surface": "turf",
            "lighting": "daylight",
            "camera_side": {"path": "clips/missing.mp4", "present": True},
            "labels": {
                "events": {
                    "motion_start": {"t_ms": 400, "tolerance_ms": 80},
                    "first_step": {"t_ms": 600, "tolerance_ms": 80},
                },
                "cues": {"shin_angle": "ok"},
            },
        }
    ]
    (tmp_path / "labels").mkdir()
    (tmp_path / "clips").mkdir()
    (tmp_path / "manifest.json").write_text(json.dumps({"clips": clips}))
    p = gates.get_progress(tmp_path)
    assert p["wr_labeled"] == 0
    assert p["wr_athletes"] == 0
    assert p["surfaces"] == 0
    assert gates.prescription_enabled(p) is False
