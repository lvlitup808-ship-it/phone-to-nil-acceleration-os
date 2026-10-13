"""Honesty pin: an mdat or moov whose payload is only the unit separator (0x1F) is not camera film.

0x1F is a C0 control character, not a sample. has_film must reject it so a padded box cannot open the golden-set gate.
A printable byte still counts.

Gate stays closed. No NIL numbers.
"""

from pathlib import Path

from services.api.gates import has_film


def _box(kind: bytes, payload: bytes) -> bytes:
    size = 8 + len(payload)
    return size.to_bytes(4, "big") + kind + payload


def _ftyp() -> bytes:
    return (16).to_bytes(4, "big") + b"ftyp" + b"isom" + (0).to_bytes(4, "big")


def test_unit_separator_mdat_is_not_film(tmp_path: Path):
    clips = tmp_path / "clips"
    clips.mkdir()
    path = clips / "clp_test.mp4"
    path.write_bytes(_ftyp() + _box(b"mdat", b"\x1f" * 8))
    clip = {
        "clip_id": "clp_test",
        "position_target": "WR",
        "camera_side": {"path": "clips/clp_test.mp4", "present": True},
        "camera_45": {"path": "clips/clp_test_45.mp4", "present": False},
    }
    assert has_film(clip, tmp_path) is False


def test_unit_separator_moov_is_not_film(tmp_path: Path):
    clips = tmp_path / "clips"
    clips.mkdir()
    path = clips / "clp_test.mp4"
    path.write_bytes(_ftyp() + _box(b"moov", b"\x1f" * 4))
    clip = {
        "clip_id": "clp_test",
        "position_target": "DB",
        "camera_side": {"path": "clips/clp_test.mp4", "present": True},
        "camera_45": {"path": "clips/clp_test_45.mp4", "present": False},
    }
    assert has_film(clip, tmp_path) is False


def test_printable_still_counts(tmp_path: Path):
    clips = tmp_path / "clips"
    clips.mkdir()
    path = clips / "clp_test.mp4"
    path.write_bytes(_ftyp() + _box(b"mdat", b"\x1f" * 3 + b"!"))
    clip = {
        "clip_id": "clp_test",
        "position_target": "WR",
        "camera_side": {"path": "clips/clp_test.mp4", "present": True},
        "camera_45": {"path": "clips/clp_test_45.mp4", "present": False},
    }
    assert has_film(clip, tmp_path) is True
