"""python -m services.golden_set.add_clip: add a filmed clip to the golden-set manifest."""

import json
import shutil
from pathlib import Path

import pytest

from services.golden_set import add_clip
from services.golden_set.manifest import check

ROOT = Path(__file__).resolve().parents[1]
SIDE = "ath_0042_WR_release_side_20260925.mp4"
FORTY_FIVE = "ath_0042_WR_release_45_20260925.mp4"


@pytest.fixture
def golden(tmp_path):
    shutil.copy(ROOT / "data/golden_set/manifest.json", tmp_path / "manifest.json")
    (tmp_path / "clips").mkdir()
    for name in (SIDE, FORTY_FIVE):
        (tmp_path / "clips" / name).write_bytes(b"x")
    return tmp_path


def _add(golden, argv_extra=(), side=SIDE, forty_five=FORTY_FIVE, surface="turf", lighting="daylight"):
    argv = ["--golden-dir", str(golden), "--side", side, "--45", forty_five]
    if surface:
        argv += ["--surface", surface]
    if lighting:
        argv += ["--lighting", lighting]
    return add_clip.main([*argv, *argv_extra])


def _clips(golden):
    return json.loads((golden / "manifest.json").read_text())["clips"]


def test_adds_filmed_clip_with_fields_from_filenames(golden):
    assert _add(golden, ["--fps", "60"]) == 0
    clip = _clips(golden)[-1]
    assert clip["clip_id"] == "clp_0003"
    assert (clip["athlete_id"], clip["position_target"], clip["movement"]) == ("ath_0042", "WR", "release")
    assert (clip["surface"], clip["lighting"]) == ("turf", "daylight")
    assert clip["camera_side"] == {"path": f"clips/{SIDE}", "fps": 60.0, "present": True}
    assert clip["camera_45"] == {"path": f"clips/{FORTY_FIVE}", "fps": 60.0, "present": True}
    assert clip["athlete_height_cm"] is None and clip["labels"] == {}
    ok, _ = check(golden / "manifest.json")
    assert ok


@pytest.mark.parametrize("missing", ["surface", "lighting"])
def test_rejects_missing_surface_or_lighting(golden, missing, capsys):
    before = (golden / "manifest.json").read_text()
    assert _add(golden, **{missing: None}) == 1
    assert missing in capsys.readouterr().err
    assert (golden / "manifest.json").read_text() == before


def test_rejects_values_outside_intake_vocabulary(golden):
    before = (golden / "manifest.json").read_text()
    assert _add(golden, surface="gym_floor") == 1
    assert _add(golden, lighting="sunset") == 1
    assert (golden / "manifest.json").read_text() == before


def test_rejects_filename_without_athlete_id(golden, capsys):
    (golden / "clips" / "clip_side.mp4").write_bytes(b"x")
    assert _add(golden, side="clip_side.mp4") == 1
    assert "Rename" in capsys.readouterr().err


@pytest.mark.parametrize("gone", [SIDE, FORTY_FIVE])
def test_rejects_camera_not_present_on_disk(golden, gone, capsys):
    (golden / "clips" / gone).unlink()
    before = (golden / "manifest.json").read_text()
    assert _add(golden) == 1
    assert "missing_side_or_45" in capsys.readouterr().err
    assert (golden / "manifest.json").read_text() == before


def test_rejects_mismatched_pair(golden):
    other = "ath_0043_WR_release_45_20260925.mp4"
    (golden / "clips" / other).write_bytes(b"x")
    assert _add(golden, forty_five=other) == 1


def test_rejects_wrong_angles(golden):
    assert _add(golden, forty_five=SIDE) == 1


def test_rejects_paths_outside_clips(golden, tmp_path_factory):
    outside = tmp_path_factory.mktemp("elsewhere") / SIDE
    outside.write_bytes(b"x")
    assert _add(golden, side=str(outside)) == 1
    assert _add(golden, side=f"../{SIDE}") == 1


def test_rejects_same_film_twice(golden):
    assert _add(golden) == 0
    assert _add(golden) == 1
    assert len(_clips(golden)) == 3


def test_dry_run_writes_nothing(golden):
    before = (golden / "manifest.json").read_text()
    assert _add(golden, ["--dry-run"]) == 0
    assert (golden / "manifest.json").read_text() == before


# Manifest-check rule (python -m services.golden_set.manifest, run by make lint): a camera
# marked present must be a contract-named clip under clips/ matching the clip's athlete,
# position and movement.

FIELDS = {"athlete_id": "ath_0042", "surface": "turf", "lighting": "daylight"}
BASE = {"clip_id": "clp_0101", "position_target": "WR", "movement": "release", **FIELDS}


def _check_clip(tmp_path, clip):
    path = tmp_path / "m.json"
    path.write_text(json.dumps({"golden_set": "pending", "clips": [clip]}))
    return check(path)


def test_present_camera_needs_contract_name(tmp_path):
    ok, lines = _check_clip(tmp_path, {**BASE, "camera_side": {"path": "clips/clp_0101_side.mp4", "present": True}})
    assert not ok and "naming contract" in lines[0]


def test_present_camera_must_match_clip(tmp_path):
    cam = {"path": "clips/ath_0043_WR_release_side_20260925.mp4", "present": True}
    ok, lines = _check_clip(tmp_path, {**BASE, "camera_side": cam})
    assert not ok and "does not match" in lines[0]


def test_present_camera_path_stays_in_clips(tmp_path):
    ok, lines = _check_clip(tmp_path, {**BASE, "camera_side": {"path": f"../clips/{SIDE}", "present": True}})
    assert not ok and "clips/" in lines[0]


def test_matching_present_camera_passes(tmp_path):
    ok, _ = _check_clip(tmp_path, {**BASE, "camera_side": {"path": f"clips/{SIDE}", "present": True}})
    assert ok


def test_absent_fixture_cameras_keep_their_paths(tmp_path):
    clip = {"clip_id": "clp_0001", "position_target": "WR", "movement": "release",
            "camera_side": {"path": "clips/clp_0001_side.mp4", "present": False}}
    ok, _ = _check_clip(tmp_path, clip)
    assert ok
