"""Retrieve → Judge → Filter → Assemble → Generate → Verify."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from packages.judgment.client import JudgmentClient

ROOT = Path(__file__).resolve().parents[2]


class EvidencePipeline:
    def __init__(self, judgment: JudgmentClient | None = None) -> None:
        self.judgment = judgment or JudgmentClient()
        self.drills = json.loads((ROOT / "data/samples/drills.json").read_text())
        self.comps = json.loads((ROOT / "data/samples/comp_clusters.json").read_text())

    def retrieve(self, query: str, cue: str | None = None) -> list[dict[str, Any]]:
        hits = []
        q = query.lower()
        for row in self.drills:
            hay = f"{row['name']} {row['cue']} {row['cue_language']}".lower()
            score = 1.0 if cue and row["cue"] == cue else (0.7 if cue and cue in hay else 0.0)
            if q and any(tok in hay for tok in q.split()):
                score += 0.4
            if score > 0:
                hits.append({**row, "kind": "drill", "score": score})
        for row in self.comps:
            hay = f"{row['id']} {row['position']} {' '.join(row.get('assumptions', []))}".lower()
            score = 0.5 if q.split() and any(tok in hay for tok in q.split()) else 0.2
            if cue and cue in hay:
                score += 0.3
            hits.append({**row, "kind": "comp", "score": score})
        hits.sort(key=lambda r: r["score"], reverse=True)
        return hits[:20]

    def filter_chunks(self, chunks: list[dict[str, Any]], k: int = 5) -> list[dict[str, Any]]:
        kept = []
        for chunk in chunks:
            decision = self.judgment.decide(
                {"chunk": chunk, "score": chunk.get("score", 0)},
                {"useful": {"type": "noul", "instructions": "Is this chunk useful evidence?"}},
            )
            useful = float(decision["useful"].value)
            if useful >= 0.5 and chunk.get("score", 0) >= 0.3:
                kept.append(chunk)
            if len(kept) >= k:
                break
        return kept

    def assemble(self, chunks: list[dict[str, Any]]) -> dict[str, Any]:
        return {
            "drills": [c for c in chunks if c.get("kind") == "drill"][:3],
            "comps": [c for c in chunks if c.get("kind") == "comp"][:3],
            "citations": [c.get("id") for c in chunks if c.get("id")],
        }

    def verify(self, payload: dict[str, Any]) -> bool:
        decision = self.judgment.decide(
            {"citations": payload.get("citations")},
            {"grounded": {"type": "noul", "instructions": "Are claims grounded in retrieved evidence?"}},
        )
        return float(decision["grounded"].value) >= 0.7

    def run(self, query: str, cue: str | None = None) -> dict[str, Any]:
        raw = self.retrieve(query, cue)
        filtered = self.filter_chunks(raw)
        assembled = self.assemble(filtered)
        assembled["grounded"] = self.verify(assembled)
        if not assembled["grounded"] and query:
            raw = self.retrieve(query + " drill progression " + (cue or ""), cue)
            assembled = self.assemble(self.filter_chunks(raw))
            assembled["grounded"] = self.verify(assembled)
        return assembled
