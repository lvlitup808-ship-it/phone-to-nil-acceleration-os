from typing import Any

from fastapi import FastAPI

from packages.shared.nil_openapi import NIL_BAND_OPENAPI
from services.valuation.engine import estimate_band

app = FastAPI(title="Acceleration OS Valuation", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/nil-band/{athlete_id}", response_model=None, responses=NIL_BAND_OPENAPI)
def band(athlete_id: str, template: str = "wr_release", school_level: str = "hs") -> dict[str, Any]:
    return estimate_band(athlete_id, template, school_level).model_dump()
