"""Bounded decisions: Jev when keyed, heuristic fallback otherwise.

Jev question types: choice, score, noul.
https://docs.typesafe.ai/sdk/python
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any


def three_question_test(*, bounded: bool, glanceable: bool, high_volume: bool) -> bool:
    return bounded and glanceable and high_volume


@dataclass
class Judgment:
    name: str
    kind: str
    value: Any
    confidence: float
    source: str
    probabilities: dict[str, float] | None = None


class JudgmentClient:
    def __init__(self) -> None:
        self.api_key = os.getenv("TYPESAFE_API_KEY", "")
        self.model = os.getenv("JEV_MODEL", "jev-latest")
        self.threshold = float(os.getenv("JEV_ACCEPT_THRESHOLD", "0.72"))
        self.fallback = os.getenv("JUDGMENT_FALLBACK", "heuristic")

    def decide(self, state: dict[str, Any], questions: dict[str, dict[str, Any]]) -> dict[str, Judgment]:
        if self.api_key:
            live = self._jev(state, questions)
            if live:
                return live
        return self._heuristic(state, questions)

    def _jev(self, state: dict[str, Any], questions: dict[str, dict[str, Any]]) -> dict[str, Judgment] | None:
        try:
            from typesafe_sdk import Choice, Noul, Score, TypeSafeClient
        except Exception:
            return None
        mapped: dict[str, Any] = {}
        for name, q in questions.items():
            kind = q.get("type")
            if kind == "choice":
                mapped[name] = Choice(instructions=q.get("instructions", name), criteria=q.get("criteria", {}))
            elif kind == "score":
                mapped[name] = Score(instructions=q.get("instructions", name), criteria=q.get("criteria", []))
            else:
                mapped[name] = Noul(instructions=q.get("instructions", name))
        try:
            with TypeSafeClient() as client:
                response = client.system_one(state=state, questions=mapped, model=self.model)
        except Exception:
            return None
        out: dict[str, Judgment] = {}
        answers = getattr(response, "answers", None) or {}
        for name, q in questions.items():
            ans = answers.get(name)
            kind = q.get("type", "noul")
            if ans is None:
                continue
            value = getattr(ans, "choice", None)
            if value is None:
                value = getattr(ans, "score", None)
            if value is None:
                value = getattr(ans, "noul", None)
            out[name] = Judgment(
                name=name,
                kind=kind,
                value=value,
                confidence=float(getattr(ans, "confidence", 0.5) or 0.5),
                source="jev",
            )
        return out or None

    def _heuristic(self, state: dict[str, Any], questions: dict[str, dict[str, Any]]) -> dict[str, Judgment]:
        quality = float(state.get("quality_score", 0.8))
        blur = float(state.get("blur", 0.1))
        out: dict[str, Judgment] = {}
        for name, q in questions.items():
            kind = q.get("type", "noul")
            if kind == "noul":
                if "synthetic" in name:
                    value = 0.12
                elif "usable" in name or "ok" in name:
                    value = max(0.0, min(1.0, quality if quality >= 0.6 else quality - blur))
                elif "grounded" in name:
                    value = 0.86 if state.get("citations") else 0.2
                else:
                    value = 0.75
                out[name] = Judgment(name, kind, value, 0.6, "heuristic")
            elif kind == "choice":
                criteria = list((q.get("criteria") or {"unknown": ""}).keys())
                pref = state.get("template") or state.get("cue") or criteria[0]
                value = pref if pref in criteria else criteria[0]
                out[name] = Judgment(name, kind, value, 0.55, "heuristic")
            else:
                out[name] = Judgment(name, kind, 1.0, 0.55, "heuristic")
        return out
