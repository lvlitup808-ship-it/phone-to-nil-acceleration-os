"""OpenAPI fragment for NIL band routes.

Docs must not publish a point estimate. Runtime responses are unchanged;
this only describes the contract (null percentiles while the gate is closed).
"""

from __future__ import annotations

from typing import Any

NULL_BAND_EXAMPLE = {
    "athlete_id": "ath_example",
    "status": "blocked_on_golden_set",
    "currency": "USD",
    "p25": None,
    "p50": None,
    "p75": None,
    "confidence": None,
    "comp_cluster_ids": [],
    "assumptions": ["no comp dataset exists; band fields are null placeholders"],
}

NIL_BAND_OPENAPI: dict[int, dict[str, Any]] = {
    200: {
        "description": (
            "Placeholder band. p25/p50/p75 and confidence stay null until a "
            "sourced comp dataset exists and the golden-set gate is open."
        ),
        "content": {
            "application/json": {
                "schema": {
                    "type": "object",
                    "additionalProperties": True,
                    "required": ["athlete_id", "p25", "p50", "p75", "confidence"],
                    "properties": {
                        "athlete_id": {"type": "string"},
                        "status": {"type": "string"},
                        "currency": {"type": "string"},
                        "p25": {"type": ["integer", "null"]},
                        "p50": {"type": ["integer", "null"]},
                        "p75": {"type": ["integer", "null"]},
                        "confidence": {"type": ["number", "null"]},
                        "comp_cluster_ids": {"type": "array", "items": {"type": "string"}},
                        "assumptions": {"type": "array", "items": {"type": "string"}},
                    },
                },
                "example": NULL_BAND_EXAMPLE,
            }
        },
    }
}
