"""Golden-set gate.

Prescription, passport and NIL content stay blocked until the golden set is real:
10 WR + 10 DB coach-labeled clips of real film, inter-rater done, few disputes,
and the diversity mix in docs/film_first.md (3 surfaces, 2 lighting, 3 athletes
per position).

Progress is derived from data/golden_set/: a label counts only when its clip is
in the manifest, at least one camera file for that clip exists on disk, the
label is neither excluded nor disputed, and it has the five events and six
frozen cues for the clip's movement. A stub file is not a coach label. A labels file that is not a JSON object
is skipped, not counted, and must not crash the gate.
A symlink under labels/ is not a coach label, even when it points at a real JSON file.
A labels directory that is itself a symlink is not the coach-label store. A manifest.json that is a symlink is not the golden-set manifest, even when it points at a real JSON file.
A golden-set directory that is itself a symlink is not the store on disk, even when the link target has a real manifest, labels, and film.
A cue value of NaN or Infinity is not a measurement and does not complete a label.
Fixture entries (no film) never count. camera present must be JSON true; 1 and "true" are not film. A camera path that is not a string is not film and must not crash the gate. A camera value that is not an object is not film. A zero-byte file is not film. A symlink is not film, even when it points at a non-empty file inside the golden root. Only a non-empty clips/*.mp4 counts; manifest.json, a label file, or a .txt is not film. A renamed text, JSON, or JPEG file is not film: bytes 4:8 must be the ftyp box. The letters ftyp later in the header are not a box. An ftyp box whose size field is 0, 1, under 16, not a multiple of 4, or larger than the file is not camera film. A major brand that is a box type name (mdat, moov, free, skip, wide, ftyp) is not a phone brand. A major brand that is not a phone brand (isom, iso2, mp41, mp42, avc1, mp71) is not camera film. An ftyp box with no mdat or moov after it is not camera film. free, skip, wide, or uuid may sit between them. A compatible brand after the minor version that is not one of those phone brands is not camera film either. Two clips that resolve to the same camera file count once: the first manifest row keeps the file, later rows do not. A hardlink of that file is the same film even when the path differs. A byte copy is the same film even when the inode differs. Coach, athlete, surface, and lighting
ids are compared case-insensitively, after NFKC and after dropping Unicode format
characters and combining marks, so spelling variants, zero-width marks, and
combining dots cannot inflate progress. A token that still contains a
non-ASCII letter is not an identity: a Cyrillic lookalike is not a second coach,
athlete, surface, or lighting condition.
A number or boolean is not an athlete, surface, or lighting condition.
A manifest that is not a JSON object, and a clip row that is not an object, are skipped. They must not crash the gate or count as film.
When the manifest declares labeling_protocol_version, a label counts only if it
carries that same stamp. A missing or other protocol is not a coach label.
A number, bool, or blank protocol is not a declared stamp: it must not disable
the check and must not count.
A clip_id that is only whitespace is not a clip. A label clip_id must be the
same string the manifest row uses; a number is not that id.
Only WR and DB clips count toward labeled totals, inter-rater, and the
surface / lighting mix. An RB, OL, or other position cannot fill those bars.
"""

from __future__ import annotations

import hashlib
import json
import math
import unicodedata
from pathlib import Path
from typing import Any

from services.golden_set.labels import CUES, EVENTS

ROOT = Path(__file__).resolve().parents[2]
GOLDEN_DIR = ROOT / "data/golden_set"

GOLDEN_SET_GATE = {
    "wr_labeled_min": 10,
    "db_labeled_min": 10,
    "inter_rater_done": True,
    "inter_rater_clips_min": 4,
    "disputed_max": 2,
    "surfaces_min": 3,
    "lighting_min": 2,
    "athletes_per_position_min": 3,
}


def _norm_token(raw: Any) -> str:
    """Strip, casefold, and drop format and combining marks. Non-strings are not identities.

    A zero-width mark or a combining dot must not split one coach or surface into two.
    A non-ASCII letter left after that is a lookalike, not a second identity.
    """
    if not isinstance(raw, str):
        return ""
    folded = unicodedata.normalize("NFKC", raw).strip().casefold()
    # NFKC can precompose a combining mark. Decompose, then drop marks.
    folded = unicodedata.normalize("NFD", folded)
    token = "".join(
        ch
        for ch in folded
        if unicodedata.category(ch) != "Cf" and not unicodedata.category(ch).startswith("M")
    )
    # NFKC does not fold Cyrillic or Greek lookalikes. Those are not a second coach.
    if not token.isascii() or not all(ch.isalnum() or ch in "_-" for ch in token):
        return ""
    return token


def _load_json(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text())
    except (OSError, ValueError):
        return None


def _film_paths(clip: dict[str, Any], root: Path) -> list[Path]:
    """Resolved non-empty camera files for this clip, inside the golden root."""
    found: list[Path] = []
    root_resolved = root.resolve()
    for key in ("camera_side", "camera_45"):
        cam = clip.get(key) or {}
        # Only JSON true counts. 1 and "true" are hand-edited lies, not film.
        # A numeric or list path is not a file and must not raise.
        # A string or list in the camera slot is not a camera object.
        if not isinstance(cam, dict):
            continue
        path_value = cam.get("path")
        if cam.get("present") is not True or not isinstance(path_value, str) or not path_value.strip():
            continue
        raw = root / path_value
        # resolve() follows links. A symlink is not the clip on disk.
        if raw.is_symlink():
            continue
        path = raw.resolve()
        # Empty files are placeholders, not filmed clips.
        # A JSON, README, or notes file inside the golden root is not a clip.
        # The intake contract is clips/<name>.mp4.
        if not _is_camera_file(path, root_resolved):
            continue
        found.append(path)
    return found



def _is_camera_file(path: Path, root_resolved: Path) -> bool:
    """True only for a non-empty regular file at clips/<name>.mp4 under the golden root."""
    if not path.is_relative_to(root_resolved) or not path.is_file():
        return False
    try:
        relative = path.relative_to(root_resolved)
    except ValueError:
        return False
    if relative.parts[:1] != ("clips",) or len(relative.parts) != 2:
        return False
    if relative.suffix.casefold() != ".mp4":
        return False
    try:
        file_size = path.stat().st_size
        if file_size <= 0:
            return False
        with path.open("rb") as handle:
            head = handle.read(32)
    except OSError:
        return False
    # ISO BMFF: 4-byte size, 'ftyp', then a 4-byte major brand.
    # An 8-byte header, or a brand of NULs, is not a phone file.
    # Size 0 means to EOF, size 1 means a 64-bit largesize. A phone ftyp
    # declares a box of at least 16 bytes, on a 4-byte boundary. Trailing bytes that look like a
    # brand do not enlarge a short box. A size bigger than the file is a
    # truncated claim, not a box the phone wrote. Brands are 4 bytes, so a
    # size that is not a multiple of 4 is a partial claim, not a phone box.
    if len(head) < 16 or head[4:8] != b"ftyp":
        return False
    box_size = int.from_bytes(head[:4], "big")
    if box_size < 16 or box_size > file_size or box_size % 4 != 0:
        return False
    brand = head[8:12]
    if not all(48 <= b <= 57 or 65 <= b <= 90 or 97 <= b <= 122 for b in brand):
        return False
    # mdat/moov/free/skip/wide/ftyp are box types, not brands a phone writes.
    # Any other 4 letters (test, fake, note) are not a phone brand either.
    # Near-misses (iso3, mp43, avc3, mp4a, dash) and uppercase ISOM/MP42 are not either.
    # Phones write isom / iso2 / mp41 / mp42 / avc1 / mp71.
    # Compatible brands sit after the 4-byte minor version. film/test/note
    # in that slot is a renamed header, not a second phone brand.
    phone_brands = {b"isom", b"iso2", b"mp41", b"mp42", b"avc1", b"mp71"}
    if brand not in phone_brands:
        return False
    if box_size > len(head):
        try:
            with path.open("rb") as handle:
                body = handle.read(box_size)
        except OSError:
            return False
    else:
        body = head
    if len(body) < box_size:
        return False
    compatible = body[16:box_size]
    if not all(compatible[i : i + 4] in phone_brands for i in range(0, len(compatible), 4)):
        return False
    # A header is not a filmed clip. Phone files carry mdat or moov after ftyp.
    # free, skip, wide, or uuid may sit between them. Notes are not a box.
    return _has_media_box(path, file_size, box_size)


def _has_media_box(path: Path, file_size: int, ftyp_size: int) -> bool:
    """True when a later box is mdat or moov and every box size fits the file."""
    offset = ftyp_size
    try:
        with path.open("rb") as handle:
            while offset + 8 <= file_size:
                handle.seek(offset)
                header = handle.read(8)
                if len(header) < 8:
                    return False
                size = int.from_bytes(header[:4], "big")
                kind = header[4:8]
                if size == 0:
                    size = file_size - offset
                # size 1 is a 64-bit largesize. A phone capture does not use it here.
                if size == 1 or size < 8 or offset + size > file_size:
                    return False
                if kind in {b"mdat", b"moov"}:
                    return True
                if kind not in {b"free", b"skip", b"wide", b"uuid"}:
                    return False
                offset += size
    except OSError:
        return False
    return False


def has_film(clip: dict[str, Any], root: Path) -> bool:
    return bool(_film_paths(clip, root))


def _event_stamped(event: Any) -> bool:
    if not isinstance(event, dict):
        return False
    t_ms = event.get("t_ms")
    return isinstance(t_ms, int) and not isinstance(t_ms, bool) and t_ms >= 0


def _cue_answered(cue: Any) -> bool:
    """A counted cue has a number, or is explicitly disputed. Empty objects are stubs."""
    if not isinstance(cue, dict):
        return False
    if cue.get("disputed") is True:
        return True
    value = cue.get("value")
    # NaN and Infinity are floats, but they are not measurements.
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
    )


def _complete_label(label: dict[str, Any], clip: dict[str, Any]) -> bool:
    """A gate-counting label has the movement's events and frozen cues.

    POST /golden/labels already rejects incomplete saves. Hand-written files
    under labels/ must not open the gate by skipping that check. Event names
    without t_ms, and cue names without a value or disputed flag, do not count.
    """
    movement = clip.get("movement")
    if movement not in EVENTS:
        return False
    events = label.get("events")
    cues = label.get("cues")
    if not isinstance(events, dict) or set(events) != set(EVENTS[movement]):
        return False
    if not isinstance(cues, dict) or set(cues) != set(CUES[movement]):
        return False
    if not all(_event_stamped(events[name]) for name in EVENTS[movement]):
        return False
    return all(_cue_answered(cues[name]) for name in CUES[movement])



def _protocol_ok(label: dict[str, Any], manifest: dict[str, Any]) -> bool:
    """Count a label only under the protocol the manifest declares.

    POST /golden/labels stamps labeling_protocol_version. Hand-written files
    that omit the stamp, or name another protocol, must not open the gate.
    A manifest with no protocol key does not add this check. A number, bool,
    or blank string is not a protocol: fail closed so it cannot skip the stamp.
    """
    if "labeling_protocol_version" not in manifest:
        return True
    expected = manifest.get("labeling_protocol_version")
    if not isinstance(expected, str) or not expected.strip():
        return False
    got = label.get("labeling_protocol_version")
    if not isinstance(got, str):
        return False
    return got.strip() == expected.strip()


def _file_id(path: Path) -> tuple[int, int] | None:
    """Device and inode. Hardlinks share this even when the path differs."""
    try:
        stat = path.stat()
    except OSError:
        return None
    return (stat.st_dev, stat.st_ino)


def _content_id(path: Path) -> str | None:
    """SHA-256 of the camera bytes. A copy is the same film with a new inode."""
    digest = hashlib.sha256()
    try:
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
    except OSError:
        return None
    return digest.hexdigest()


def _empty_progress() -> dict[str, Any]:
    return {
        "wr_labeled": 0,
        "db_labeled": 0,
        "inter_rater_done": False,
        "disputed": 0,
        "inter_rater_clips": 0,
        "surfaces": 0,
        "lighting_conditions": 0,
        "wr_athletes": 0,
        "db_athletes": 0,
    }


def get_progress(golden_dir: Path = GOLDEN_DIR) -> dict[str, Any]:
    # is_dir() and read_text() follow a directory symlink. An outside packet
    # linked in as data/golden_set is not the golden set on disk.
    if golden_dir.is_symlink():
        return _empty_progress()
    manifest_path = golden_dir / "manifest.json"
    # read_text follows a symlink. An outside packet linked in as manifest.json
    # is not the golden-set manifest on disk.
    loaded = None if manifest_path.is_symlink() else _load_json(manifest_path)
    # A list or string is truthy, so `or {}` would not save the gate from .get.
    manifest = loaded if isinstance(loaded, dict) else {}
    raw_clips = manifest.get("clips", [])
    clips: dict[str, dict[str, Any]] = {}
    if isinstance(raw_clips, list):
        for row in raw_clips:
            if not isinstance(row, dict):
                continue
            cid = row.get("clip_id")
            # "   " is truthy. It is not a clip the intake form named.
            if isinstance(cid, str) and cid.strip() and cid.strip() == cid:
                clips[cid] = row
    filmed: dict[str, dict[str, Any]] = {}
    claimed: set[Path] = set()
    claimed_files: set[tuple[int, int]] = set()
    claimed_hashes: set[str] = set()
    for cid, clip in clips.items():
        paths = _film_paths(clip, golden_dir)
        file_ids = {file_id for path in paths if (file_id := _file_id(path))}
        content_ids = {content_id for path in paths if (content_id := _content_id(path))}
        # Unreadable bytes are not film we can prove unique.
        if (
            not paths
            or not content_ids
            or any(path in claimed for path in paths)
            or bool(file_ids & claimed_files)
            or bool(content_ids & claimed_hashes)
        ):
            continue
        claimed.update(paths)
        claimed_files.update(file_ids)
        claimed_hashes.update(content_ids)
        filmed[cid] = clip

    coaches: dict[str, set[str]] = {}
    disputed: set[str] = set()
    labels_dir = golden_dir / "labels"
    # is_dir() follows a directory symlink. glob would then read a label packet
    # that is not the store on disk. A link is not labels/.
    label_paths = []
    if labels_dir.is_dir() and not labels_dir.is_symlink():
        label_paths = sorted(labels_dir.glob("*.json"))
    for path in label_paths:
        if path.name.startswith("_"):
            continue
        # A symlink is not a coach label on disk. read_text() would follow it.
        if path.is_symlink() or not path.is_file():
            continue
        label = _load_json(path)
        if not isinstance(label, dict):
            continue
        # str(1234) must not attach a numeric label to the manifest row "1234".
        cid = label.get("clip_id")
        coach = _norm_token(label.get("coach_id"))
        if not isinstance(cid, str) or cid not in filmed or label.get("excluded") or not coach:
            continue
        if not _complete_label(label, filmed[cid]):
            continue
        if not _protocol_ok(label, manifest):
            continue
        if label.get("disputed") or filmed[cid].get("disputed"):
            disputed.add(cid)
            continue
        coaches.setdefault(cid, set()).add(coach)

    labeled = [filmed[cid] for cid in coaches if cid not in disputed]
    wr = [c for c in labeled if c.get("position_target") == "WR"]
    db = [c for c in labeled if c.get("position_target") == "DB"]
    counted = wr + db
    overlap = sum(
        1
        for cid, who in coaches.items()
        if cid not in disputed
        and len(who) >= 2
        and filmed[cid].get("position_target") in ("WR", "DB")
    )

    def distinct(rows: list[dict[str, Any]], key: str) -> int:
        values: set[str] = set()
        for row in rows:
            token = _norm_token(row.get(key))
            if token:
                values.add(token)
        return len(values)

    return {
        "wr_labeled": len(wr),
        "db_labeled": len(db),
        "inter_rater_done": overlap >= GOLDEN_SET_GATE["inter_rater_clips_min"],
        "disputed": len(disputed),
        "inter_rater_clips": overlap,
        "surfaces": distinct(counted, "surface"),
        "lighting_conditions": distinct(counted, "lighting"),
        "wr_athletes": distinct(wr, "athlete_id"),
        "db_athletes": distinct(db, "athlete_id"),
    }


def _missing(p: dict[str, Any]) -> list[str]:
    g = GOLDEN_SET_GATE
    missing = []
    if p.get("wr_labeled", 0) < g["wr_labeled_min"]:
        missing.append(f"wr_labeled {p.get('wr_labeled', 0)}/{g['wr_labeled_min']}")
    if p.get("db_labeled", 0) < g["db_labeled_min"]:
        missing.append(f"db_labeled {p.get('db_labeled', 0)}/{g['db_labeled_min']}")
    if not p.get("inter_rater_done"):
        missing.append("inter_rater")
    if p.get("disputed", 0) > g["disputed_max"]:
        missing.append(f"disputed {p.get('disputed', 0)}")
    if p.get("surfaces", 0) < g["surfaces_min"]:
        missing.append(f"surfaces {p.get('surfaces', 0)}/{g['surfaces_min']}")
    if p.get("lighting_conditions", 0) < g["lighting_min"]:
        missing.append(f"lighting {p.get('lighting_conditions', 0)}/{g['lighting_min']}")
    for pos in ("wr", "db"):
        n = p.get(f"{pos}_athletes", 0)
        if n < g["athletes_per_position_min"]:
            missing.append(f"{pos}_athletes {n}/{g['athletes_per_position_min']}")
    return missing


def prescription_enabled(progress: dict[str, Any] | None = None) -> bool:
    p = progress if progress is not None else get_progress()
    return not _missing(p)


def blocked_reason(progress: dict[str, Any] | None = None) -> dict[str, Any]:
    p = progress if progress is not None else get_progress()
    return {"status": "blocked_on_golden_set", "missing": _missing(p), "progress": p}


def gate_state() -> dict[str, Any]:
    """Current gate as served on /gates/golden: open, or blocked with what is missing."""
    p = get_progress()
    if prescription_enabled(p):
        return {"status": "open", "missing": [], "progress": p}
    return blocked_reason(p)
