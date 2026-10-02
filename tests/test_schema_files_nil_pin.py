"""Honesty: committed schemas must not publish NIL point estimates.

OpenAPI is pinned separately. These files are the checked-in contract.
`nil_band.schema.json` may name p25/p50/p75 only as nullable fields with a
null default. No schema or example payload may ship a dollar amount, a
numeric percentile, or a numeric MAE. The illustrative coach session must
stay labeled made-up and must not grow a valuation.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "data" / "schemas"
NIL_BAND = SCHEMAS / "nil_band.schema.json"
COACH_SESSION = SCHEMAS / "coach_session.json"

_DOLLAR = re.compile(r"\$\s*\d")
_PERCENTILE = re.compile(
    r'"(p25|p50|p75|confidence)"\s*:\s*-?\d+(?:\.\d+)?',
    re.IGNORECASE,
)
_MAE = re.compile(r"\bMAE\b\s*[:=]\s*\d", re.IGNORECASE)


def test_nil_band_schema_stays_nullable_with_null_defaults() -> None:
    schema = json.loads(NIL_BAND.read_text())
    props = schema["properties"]
    for key in ("p25", "p50", "p75", "confidence"):
        field = props[key]
        types = {item.get("type") for item in field["anyOf"]}
        assert "null" in types, f"{key} is not nullable: {field}"
        assert field.get("default") is None, f"{key} default is not null: {field}"
    assert schema["properties"]["status"]["default"] == "schema_only"
    assert "null until a sourced comp dataset exists" in schema["description"]
    published = NIL_BAND.read_text()
    assert _PERCENTILE.search(published) is None
    assert _DOLLAR.search(published) is None


def test_committed_schemas_publish_no_nil_numbers() -> None:
    offenders: list[str] = []
    for path in sorted(SCHEMAS.iterdir()):
        if path.suffix not in {".json", ".sql"}:
            continue
        text = path.read_text()
        if _DOLLAR.search(text):
            offenders.append(f"{path.name}:dollar")
        if _PERCENTILE.search(text):
            offenders.append(f"{path.name}:percentile")
        if _MAE.search(text):
            offenders.append(f"{path.name}:mae")
    assert offenders == []


def test_coach_session_example_is_not_a_valuation() -> None:
    text = COACH_SESSION.read_text()
    payload = json.loads(text)
    assert "made up" in payload["_note"]
    assert "not real session data" in payload["_note"]
    blob = json.dumps(payload["coach_session"])
    assert "p25" not in blob and "p50" not in blob and "p75" not in blob
    assert "nil" not in blob.lower()
    assert _DOLLAR.search(text) is None
    assert _MAE.search(text) is None
