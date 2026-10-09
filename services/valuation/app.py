from typing import Any

from fastapi import FastAPI

from packages.shared.nil_openapi import NIL_BAND_OPENAPI
from services.api.gates import gate_state
from services.valuation.engine import estimate_band

app = FastAPI(title="Acceleration OS Valuation", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/nil-band/{athlete_id}", response_model=None, responses=NIL_BAND_OPENAPI)
def band(athlete_id: str, template: str = "wr_release", school_level: str = "hs") -> dict[str, Any]:
    payload = estimate_band(athlete_id, template, school_level).model_dump()
    # Same honesty as the product API: schema_only is not an open valuation.
    gate = gate_state()
    if gate["status"] != "open":
        payload.update(gate)
        # A closed gate must not forward engine dollars, even if estimate_band lies.
        payload["p25"] = None
        payload["p50"] = None
        payload["p75"] = None
        payload["confidence"] = None
        payload["comp_cluster_ids"] = []
        payload["counterfactuals"] = {}
    return payload
