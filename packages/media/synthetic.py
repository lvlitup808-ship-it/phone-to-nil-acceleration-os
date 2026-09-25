from __future__ import annotations

from typing import Any

import numpy as np


def corroborate(frames: list[np.ndarray] | None, jev_risk: str) -> dict[str, Any]:
    return {
        "jev_risk": jev_risk,
        "second_model": {"name": "xception_finetune", "status": "not_shipped"},
        "review_required": jev_risk == "high",
    }
