import json

import pytest
from pydantic import ValidationError

from packages.shared.golden import GoldenManifest, ManifestClip
from services.golden_set.manifest import MANIFEST, check

BASE = {"clip_id": "clp_0101", "position_target": "WR", "movement": "release"}
FILMED = {"camera_side": {"path": "clips/clp_0101_side.mp4", "fps": 60, "present": True}}


def test_committed_manifest_validates():
    GoldenManifest.model_validate(json.loads(MANIFEST.read_text()))


def test_committed_fixtures_carry_the_fields_as_null():
    """Fixtures have no film, so the fields are present but explicitly null (nothing invented)."""
    raw = json.loads(MANIFEST.read_text())
    assert raw["schema_version"] == "1.1.0"
    for clip in raw["clips"]:
        for field in ("athlete_id", "surface", "lighting"):
            assert field in clip and clip[field] is None, (clip["clip_id"], field)


def test_filmed_clip_must_record_athlete_surface_lighting():
    with pytest.raises(ValidationError, match="athlete_id, surface, lighting"):
        ManifestClip.model_validate({**BASE, **FILMED})
    ok = ManifestClip.model_validate(
        {**BASE, **FILMED, "athlete_id": "ath_0042", "surface": "turf", "lighting": "daylight"}
    )
    assert ok.surface == "turf"


def test_unfilmed_clip_may_leave_them_null():
    assert ManifestClip.model_validate(BASE).surface is None


@pytest.mark.parametrize(
    ("field", "bad"),
    [("surface", "gym_floor"), ("lighting", "sunset"), ("athlete_id", "0042"), ("clip_id", "clip1"),
     ("position_target", "RB"), ("movement", "cut")],
)
def test_values_outside_the_intake_vocabulary_are_rejected(field, bad):
    with pytest.raises(ValidationError):
        ManifestClip.model_validate({**BASE, field: bad})


def test_typo_field_names_are_rejected():
    with pytest.raises(ValidationError):
        ManifestClip.model_validate({**BASE, "lightning": "daylight"})


def test_duplicate_clip_ids_are_rejected():
    with pytest.raises(ValidationError, match="duplicate clip_id"):
        GoldenManifest.model_validate({"golden_set": "pending", "clips": [BASE, BASE]})


def test_check_reports_ok_on_committed_manifest():
    ok, lines = check()
    assert ok, lines


def test_check_reports_errors(tmp_path):
    bad = tmp_path / "manifest.json"
    bad.write_text(json.dumps({"golden_set": "pending", "clips": [{**BASE, **FILMED}]}))
    ok, lines = check(bad)
    assert not ok
    assert any("athlete_id, surface, lighting" in line for line in lines)


def test_gate_counts_diversity_from_manifest_fields(tmp_path):
    from services.api import gates

    (tmp_path / "labels").mkdir()
    (tmp_path / "clips").mkdir()
    clips = []
    for i, (surface, lighting) in enumerate([("turf", "daylight"), ("grass", "night_lit"), ("track", "daylight")]):
        cid = f"clp_010{i}"
        (tmp_path / "clips" / f"{cid}_side.mp4").write_bytes(b"x")
        clips.append({
            "clip_id": cid, "position_target": "WR", "movement": "release", "athlete_id": f"ath_000{i}",
            "surface": surface, "lighting": lighting,
            "camera_side": {"path": f"clips/{cid}_side.mp4", "fps": 60, "present": True},
        })
        (tmp_path / "labels" / f"{cid}.json").write_text(json.dumps({"clip_id": cid, "coach_id": "coach_001"}))
    manifest = {"golden_set": "pending", "clips": clips}
    GoldenManifest.model_validate(manifest)
    (tmp_path / "manifest.json").write_text(json.dumps(manifest))
    p = gates.get_progress(tmp_path)
    assert (p["surfaces"], p["lighting_conditions"], p["wr_athletes"]) == (3, 2, 3)
