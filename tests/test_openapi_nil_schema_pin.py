"""Pin OpenAPI so published NIL band docs cannot show point estimates.

GET /nil-band must declare p25/p50/p75/confidence as nullable and must not
ship a numeric example. The golden-set gate is closed; docs are not a
valuation.
"""

from __future__ import annotations

import json
import re

from services.api.app import app
from services.valuation.app import app as valuation_app

NUMERIC_EXAMPLE = re.compile(r'"(p25|p50|p75|confidence)"\s*:\s*-?\d+(?:\.\d+)?')


def _ok_schema(spec: dict, path: str) -> dict:
    operation = spec["paths"][path]["get"]
    content = operation["responses"]["200"]["content"]["application/json"]
    schema = content["schema"]
    assert "properties" in schema, f"{path} 200 schema has no properties"
    return content


def _assert_null_band_schema(content: dict, path: str) -> None:
    props = content["schema"]["properties"]
    for key in ("p25", "p50", "p75", "confidence"):
        blob = json.dumps(props.get(key))
        assert "null" in blob, f"{path} {key} is not nullable: {blob}"
    published = json.dumps(content)
    hit = NUMERIC_EXAMPLE.search(published)
    assert hit is None, f"{path} OpenAPI publishes a numeric band example: {hit.group(0)}"


def test_api_nil_band_openapi_has_no_point_estimate() -> None:
    spec = app.openapi()
    content = _ok_schema(spec, "/nil-band/{athlete_id}")
    _assert_null_band_schema(content, "/nil-band/{athlete_id}")


def test_valuation_nil_band_openapi_has_no_point_estimate() -> None:
    spec = valuation_app.openapi()
    content = _ok_schema(spec, "/nil-band/{athlete_id}")
    _assert_null_band_schema(content, "/nil-band/{athlete_id}")
