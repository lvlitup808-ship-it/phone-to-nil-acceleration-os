from __future__ import annotations

import hashlib
import json
from collections.abc import Callable
from datetime import UTC, datetime
from typing import Any

from packages.shared.slice2 import AssessmentStatus


class ConsentStore:
    def __init__(self) -> None:
        self.consents: dict[str, dict[str, Any]] = {}
        self.receipts: dict[str, dict[str, Any]] = {}
        # Called on revoke with the consent row; each returns {artifact_kind: n_deleted}.
        self.purgers: list[Callable[[dict[str, Any]], dict[str, int]]] = []

    def grant(self, athlete_id: str, scope: list[str], parent: bool = False) -> dict[str, Any]:
        cid = f"cns_{hashlib.sha256(f'{athlete_id}:{datetime.now(UTC).isoformat()}'.encode()).hexdigest()[:10]}"
        row = {
            "consent_id": cid,
            "athlete_id": athlete_id,
            "consent_scope": scope,
            "revoked": False,
            "parent_attested": parent,
            "granted_at": datetime.now(UTC).isoformat(),
        }
        self.consents[cid] = row
        return row

    def revoke(self, consent_id: str, artifacts: list[str]) -> dict[str, Any]:
        row = self.consents.get(consent_id)
        if not row:
            raise KeyError(consent_id)
        row["revoked"] = True
        row["revoked_at"] = datetime.now(UTC).isoformat()
        counts = dict.fromkeys(artifacts, 0)
        for purge in self.purgers:
            for kind, n in purge(row).items():
                counts[kind] = counts.get(kind, 0) + n
        payload = {
            "consent_id": consent_id,
            "athlete_id": row["athlete_id"],
            "deleted_artifacts": artifacts,
            "deleted_counts": counts,
            "revoked_at": row["revoked_at"],
        }
        sig = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
        receipt = {**payload, "receipt_id": f"rcp_{sig[:12]}", "signature": sig}
        self.receipts[receipt["receipt_id"]] = receipt
        return receipt

    def active_scopes(self, athlete_id: str) -> dict[str, bool]:
        """Scopes currently granted and not revoked. Nothing on file means all False."""
        granted: set[str] = set()
        for row in self.consents.values():
            if row["athlete_id"] == athlete_id and not row.get("revoked"):
                granted.update(row["consent_scope"])
        return {"capture": "capture" in granted, "coach": "coach" in granted, "public": "public" in granted}

    def attach(self, assessment: dict[str, Any], consent_id: str) -> dict[str, Any]:
        row = self.consents.get(consent_id)
        assessment["consent_id"] = consent_id
        assessment["consent_scope"] = list(row["consent_scope"]) if row else []
        return self.cascade(assessment)

    def cascade(self, assessment: dict[str, Any]) -> dict[str, Any]:
        cid = assessment.get("consent_id")
        row = self.consents.get(cid) if cid else None
        if row and row.get("revoked"):
            assessment["assessment_status"] = AssessmentStatus.scope_revoked.value
            assessment["cues"] = []
            assessment["events"] = []
            assessment["nil_band_blocked"] = True
            assessment["fix_this_first"] = None
        return assessment
