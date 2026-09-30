"""Executable reference model. Trusted gateway code, NOT a security sandbox."""
import hashlib
import json
import sqlite3
import time
import uuid
from contextlib import contextmanager
from pathlib import Path


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def validate_action(body):
    required = {"action_type", "recipient", "amount", "resource", "content", "permission",
                "cost", "reversible", "consent_ok", "sensitivity_ok", "uncertainty_ok"}
    if not required <= body.keys() or type(body["cost"]) not in (int, float) or body["cost"] < 0:
        raise Rejected("invalid action schema")
    if any(type(body[k]) is not bool for k in
           ("reversible", "consent_ok", "sensitivity_ok", "uncertainty_ok")):
        raise Rejected("invalid policy flags")
    canonical(body)


class Rejected(Exception):
    pass


class Engine:
    """Single gateway reference; SQLite persists decisions before external calls."""

    def __init__(self, path, adapter, clock=time.time, policy_service=None):
        self.adapter, self.clock = adapter, clock
        self.policy_service = policy_service
        self.spec = json.loads(Path(__file__).with_name("acceptance_spec.json").read_text())
        self.db = sqlite3.connect(path, isolation_level=None)
        self.db.row_factory = sqlite3.Row
        self.db.executescript('''
        PRAGMA journal_mode=WAL;
        PRAGMA synchronous=FULL;
        CREATE TABLE IF NOT EXISTS contracts(id TEXT PRIMARY KEY, body TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS principals(id TEXT PRIMARY KEY, permissions TEXT NOT NULL,
            parent TEXT, task_scope TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS actions(id TEXT PRIMARY KEY, contract_id TEXT NOT NULL,
            actor TEXT NOT NULL, body TEXT NOT NULL, state TEXT NOT NULL,
            cancel_requested INTEGER NOT NULL DEFAULT 0);
        CREATE TABLE IF NOT EXISTS approvals(nonce TEXT PRIMARY KEY, action_id TEXT NOT NULL,
            action_hash TEXT NOT NULL, expires REAL NOT NULL, consumed INTEGER NOT NULL DEFAULT 0,
            revoked INTEGER NOT NULL DEFAULT 0);
        CREATE TABLE IF NOT EXISTS ledger(seq INTEGER PRIMARY KEY AUTOINCREMENT,
            action_id TEXT, event TEXT NOT NULL, body TEXT NOT NULL, at REAL NOT NULL);
        CREATE TABLE IF NOT EXISTS evidence(action_id TEXT, kind TEXT, body TEXT,
            PRIMARY KEY(action_id, kind));
        ''')

    def close(self):
        self.db.close()

    @contextmanager
    def transaction(self):
        self.db.execute("BEGIN IMMEDIATE")
        try:
            yield
            self.db.execute("COMMIT")
        except BaseException:
            self.db.execute("ROLLBACK")
            raise

    def log(self, aid, event, body):
        self.db.execute("INSERT INTO ledger(action_id,event,body,at) VALUES(?,?,?,?)",
                        (aid, event, canonical(body), self.clock()))

    def reject(self, aid, reason):
        self.log(aid, "DENIED", {"reason": reason})
        raise Rejected(reason)

    def contract(self, body):
        required = {"baseline", "success_criteria", "deadline", "budget", "constraints",
                    "owner", "measurement_plan"}
        if not required <= body.keys() or any(body[k] is None for k in required):
            raise Rejected("incomplete outcome contract")
        if body["deadline"] <= self.clock() or body["budget"] < 0:
            raise Rejected("invalid deadline or budget")
        cid = str(uuid.uuid4())
        with self.transaction():
            self.db.execute("INSERT INTO contracts VALUES(?,?)", (cid, canonical(body)))
            self.log(None, "CONTRACTED", {"contract_id": cid, "hash": digest(body)})
        return cid

    def principal(self, actor, permissions, parent=None, task_scope=None):
        """Trusted administrative operation; agents must never receive this API."""
        if parent == actor:
            raise Rejected("cyclic delegation")
        cursor, seen = parent, {actor}
        while cursor:
            if cursor in seen:
                raise Rejected("cyclic delegation")
            seen.add(cursor)
            row = self.db.execute("SELECT parent FROM principals WHERE id=?", (cursor,)).fetchone()
            if row is None:
                raise Rejected("unknown parent")
            cursor = row[0]
        with self.transaction():
            self.db.execute("INSERT OR REPLACE INTO principals VALUES(?,?,?,?)",
                            (actor, canonical(sorted(permissions)), parent,
                             canonical(sorted(task_scope if task_scope is not None else permissions))))
            self.log(None, "AUTHORITY_UPDATED", {"actor": actor})

    def effective(self, actor, seen=None):
        seen = set() if seen is None else seen
        if actor in seen:
            raise Rejected("cyclic delegation")
        seen.add(actor)
        row = self.db.execute("SELECT * FROM principals WHERE id=?", (actor,)).fetchone()
        if row is None:
            return set()
        result = set(json.loads(row["permissions"])) & set(json.loads(row["task_scope"]))
        if row["parent"]:
            result &= self.effective(row["parent"], seen)
        return result

    def plan(self, cid, actor, body):
        validate_action(body)
        if not self.db.execute("SELECT 1 FROM contracts WHERE id=?", (cid,)).fetchone():
            raise Rejected("unknown contract")
        aid = str(uuid.uuid4())
        with self.transaction():
            self.db.execute("INSERT INTO actions(id,contract_id,actor,body,state) VALUES(?,?,?,?,?)",
                            (aid, cid, actor, canonical(body), "PLANNED"))
            self.log(aid, "PLANNED", {"hash": digest(body)})
        return aid

    def action(self, aid):
        row = self.db.execute("SELECT * FROM actions WHERE id=?", (aid,)).fetchone()
        if row is None:
            raise Rejected("unknown action")
        return dict(row)

    def state(self, aid):
        return self.action(aid)["state"]

    def update(self, aid, state):
        current = self.state(aid)
        if state not in self.spec["transitions"].get(current, []):
            raise Rejected("forbidden state transition: " + current + " -> " + state)
        self.db.execute("UPDATE actions SET state=? WHERE id=?", (state, aid))
        self.log(aid, state, {})

    def policy(self, row):
        body = json.loads(row["body"])
        contract = json.loads(self.db.execute("SELECT body FROM contracts WHERE id=?",
                                             (row["contract_id"],)).fetchone()[0])
        if body["permission"] not in self.effective(row["actor"]):
            raise Rejected("missing current authority")
        # Agent-supplied risk flags are descriptive ONLY. Authority comes from this
        # trusted service, which must obtain facts independently of the model.
        if self.policy_service is None:
            raise Rejected("independent policy service required")
        facts = self.policy_service(row["actor"], body, contract)
        if not isinstance(facts, dict) or not all(facts.get(k) is True for k in
                ("consent_ok", "sensitivity_ok", "uncertainty_ok", "constraints_ok")):
            raise Rejected("hard policy veto")
        if contract["deadline"] <= self.clock():
            raise Rejected("contract expired")
        reserved = sum(json.loads(r[0])["cost"] for r in self.db.execute(
            "SELECT body FROM actions WHERE contract_id=? AND state IN "
            "('DISPATCHED','UNKNOWN','CONFIRMED','VERIFIED','EVALUATED','CLOSED','RECONCILED_FAILED')",
            (row["contract_id"],)))
        if reserved + body["cost"] > contract["budget"]:
            raise Rejected("budget exceeded")

    def approve(self, aid, expires):
        """Trusted approver API. Production needs authenticated approval service."""
        nonce = str(uuid.uuid4())
        try:
            with self.transaction():
                row = self.action(aid)
                if row["state"] != "PLANNED" or expires <= self.clock():
                    raise Rejected("invalid approval state or expiry")
                self.policy(row)
                self.db.execute("INSERT INTO approvals(nonce,action_id,action_hash,expires) VALUES(?,?,?,?)",
                                (nonce, aid, digest({"actor": row["actor"], "contract": row["contract_id"],
                                                   "action": json.loads(row["body"])}), expires))
                self.update(aid, "AUTHORIZED")
        except Rejected as exc:
            self.reject(aid, str(exc))
        return nonce

    def mutate(self, aid, body):
        row = self.action(aid)
        if row["state"] not in {"PLANNED", "AUTHORIZED"}:
            self.reject(aid, "mutation forbidden after dispatch intent")
        # Reuse schema validation without creating a temporary plan.
        if set(body) != set(json.loads(row["body"])):
            self.reject(aid, "mutation changes schema")
        validate_action(body)
        with self.transaction():
            self.db.execute("UPDATE actions SET body=? WHERE id=?", (canonical(body), aid))
            if row["state"] == "AUTHORIZED":
                self.update(aid, "PLANNED")
            self.db.execute("UPDATE approvals SET revoked=1 WHERE action_id=?", (aid,))
            self.log(aid, "APPROVAL_INVALIDATED", {"hash": digest(body)})

    def dispatch(self, aid, nonce):
        try:
            with self.transaction():
                row = self.action(aid)
                approval = self.db.execute("SELECT * FROM approvals WHERE nonce=?", (nonce,)).fetchone()
                bound = digest({"actor": row["actor"], "contract": row["contract_id"],
                                "action": json.loads(row["body"])})
                if row["state"] != "AUTHORIZED" or approval is None:
                    raise Rejected("authorization required")
                if (approval["action_id"] != aid or approval["action_hash"] != bound or
                    approval["consumed"] or approval["revoked"] or approval["expires"] <= self.clock()):
                    raise Rejected("invalid, expired, changed, or replayed approval")
                self.policy(row)
                self.db.execute("UPDATE approvals SET consumed=1 WHERE nonce=?", (nonce,))
                self.update(aid, "DISPATCHED")
                self.log(aid, "DISPATCH_INTENT", {"idempotency_key": aid})
        except Rejected as exc:
            self.reject(aid, str(exc))
        except Exception:
            self.log(aid, "PRE_DISPATCH_FAILURE", {"dispatched": False})
            raise
        # Intent is durable BEFORE the call; it is not evidence the network call happened.
        try:
            result = self.adapter.execute(aid, json.loads(row["body"]))
        except Exception:
            with self.transaction():
                self.update(aid, "UNKNOWN")
            return "UNKNOWN"
        self.resolve(aid, result, reconciliation=False)
        return self.state(aid)

    def resolve(self, aid, result, reconciliation):
        expected = "UNKNOWN" if reconciliation else "DISPATCHED"
        if self.state(aid) != expected:
            self.reject(aid, "invalid result transition")
        if result.get("status") not in {"executed", "not_executed", "unknown"}:
            result = {"status": "unknown"}
        if result["status"] != "unknown" and not result.get("record_id"):
            result = {"status": "unknown"}
        with self.transaction():
            self.log(aid, "RECONCILIATION" if reconciliation else "ADAPTER_RESULT", result)
            if result["status"] == "executed":
                self.db.execute("INSERT OR REPLACE INTO evidence VALUES(?,?,?)",
                                (aid, "execution", canonical(result)))
                self.update(aid, "CONFIRMED")
            elif result["status"] == "not_executed":
                self.update(aid, "RECONCILED_FAILED" if reconciliation else "FAILED")
            elif expected == "DISPATCHED":
                self.update(aid, "UNKNOWN")

    def recover(self):
        with self.transaction():
            for row in self.db.execute("SELECT id FROM actions WHERE state='DISPATCHED'").fetchall():
                self.update(row[0], "UNKNOWN")

    def reconcile(self, aid):
        if self.state(aid) != "UNKNOWN":
            self.reject(aid, "reconciliation requires UNKNOWN")
        try:
            result = self.adapter.reconcile(aid)
        except Exception:
            self.log(aid, "RECONCILIATION_UNAVAILABLE", {"human_review_required": True})
            return "UNKNOWN"
        self.resolve(aid, result, reconciliation=True)
        return self.state(aid)

    def cancel(self, aid):
        row = self.action(aid)
        with self.transaction():
            if row["state"] in {"PLANNED", "AUTHORIZED"}:
                self.update(aid, "CANCELLED")
                self.db.execute("UPDATE approvals SET revoked=1 WHERE action_id=?", (aid,))
            elif row["state"] in {"DISPATCHED", "UNKNOWN", "CONFIRMED"}:
                self.db.execute("UPDATE actions SET cancel_requested=1 WHERE id=?", (aid,))
                self.log(aid, "CANCEL_REQUESTED", {"external_rollback_not_guaranteed": True})
            else:
                self.log(aid, "CANCEL_NOT_APPLICABLE", {"state": row["state"]})

    def verify(self, aid):
        if self.state(aid) != "CONFIRMED":
            self.reject(aid, "external execution confirmation required")
        if not self.db.execute("SELECT 1 FROM evidence WHERE action_id=? AND kind='execution'", (aid,)).fetchone():
            self.reject(aid, "missing execution evidence")
        with self.transaction():
            self.update(aid, "VERIFIED")

    def evaluate(self, aid, report):
        row = self.action(aid)
        if row["state"] != "VERIFIED":
            self.reject(aid, "verification required")
        contract = json.loads(self.db.execute("SELECT body FROM contracts WHERE id=?",
                                             (row["contract_id"],)).fetchone()[0])
        if report.get("measurement_plan_hash") != digest(contract["measurement_plan"]):
            self.reject(aid, "measurement plan changed")
        if report.get("impact") not in {"unresolved", "unsuccessful", "supported"}:
            self.reject(aid, "invalid impact classification")
        if report["impact"] == "supported" and not (report.get("comparison_record") and
                                                    report.get("analysis_record")):
            self.reject(aid, "comparison and analysis evidence required")
        with self.transaction():
            self.db.execute("INSERT OR REPLACE INTO evidence VALUES(?,?,?)", (aid, "impact_report", canonical(report)))
            self.update(aid, "EVALUATED")
        # This validates schema/provenance linkage, NOT causal validity.

    def finish(self, aid):
        if self.state(aid) != "EVALUATED":
            self.reject(aid, "evaluation required")
        with self.transaction():
            self.update(aid, "CLOSED")


class SimulatedAdapter:
    """Fault-injectable fake; never sends anything. Receipts are simulated."""
    def __init__(self):
        self.records, self.calls = {}, 0
        self.fail_after_effect = False
        self.crash_after_effect = False

    def execute(self, key, body):
        self.calls += 1
        self.records.setdefault(key, {"status": "executed", "record_id": "fake:" + key})
        if self.crash_after_effect:
            raise SystemExit("simulated process death")
        if self.fail_after_effect:
            raise TimeoutError("simulated lost response")
        return self.records[key]

    def reconcile(self, key):
        return self.records.get(key, {"status": "unknown"})
