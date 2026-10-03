import json
import tempfile
from pathlib import Path
from engine import Engine, SimulatedAdapter, digest
from tests.test_acceptance import action, contract, fixture_policy

with tempfile.TemporaryDirectory() as folder:
    adapter = SimulatedAdapter()
    gateway = Engine(str(Path(folder) / "gateway.sqlite"), adapter, lambda: 100, fixture_policy)
    gateway.principal("worker", {"outreach:sandbox"})
    cid = gateway.contract(contract())
    aid = gateway.plan(cid, "worker", action())
    nonce = gateway.approve(aid, 200)
    adapter.fail_after_effect = True
    print("Lost response:", gateway.dispatch(aid, nonce))
    print("Reconciliation:", gateway.reconcile(aid))
    gateway.verify(aid)
    gateway.evaluate(aid, {"measurement_plan_hash": digest(contract()["measurement_plan"]),
                          "impact": "unresolved"})
    gateway.finish(aid)
    print(json.dumps({"state": gateway.state(aid), "execution": "confirmed (SIMULATED)",
                      "impact": "unresolved", "external_calls": adapter.calls}, indent=2))
    gateway.close()
