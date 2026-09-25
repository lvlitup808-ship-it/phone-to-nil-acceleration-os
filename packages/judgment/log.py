from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]


def log_jev(question: str, inputs: dict[str, Any], output: Any, latency_ms: float, fallback: bool) -> None:
    day = datetime.now(UTC).strftime("%Y-%m-%d")
    folder = ROOT / "logs" / "jev"
    folder.mkdir(parents=True, exist_ok=True)
    payload = {
        "ts": datetime.now(UTC).isoformat(),
        "question": question,
        "inputs_hash": hashlib.sha256(json.dumps(inputs, sort_keys=True, default=str).encode()).hexdigest()[:16],
        "output": output if isinstance(output, (str, int, float, bool, dict, list)) else str(output),
        "latency_ms": latency_ms,
        "fallback": fallback,
    }
    with (folder / f"{day}.jsonl").open("a") as fh:
        fh.write(json.dumps(payload) + "\n")
