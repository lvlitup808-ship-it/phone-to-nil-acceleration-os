"""Opt-in adapter contract against a dedicated sandbox. Never falls back to fake."""
import importlib
import os
import unittest
from engine import Engine, Rejected
from test_acceptance import action, contract


@unittest.skipUnless(os.environ.get("AGENT_SANDBOX_ADAPTER") and
                     os.environ.get("AGENT_INTEGRATION_MODE") == "sandbox",
                     "UNPROVEN: real sandbox adapter not configured")
class RealIntegration(unittest.TestCase):
    def test_real_execution_reconciliation_and_replay(self):
        # Operator-authored module owns trusted credentials and sandbox isolation.
        # fixture: adapter, db_path, clock, action, contract, cleanup.
        fixture = importlib.import_module(os.environ["AGENT_SANDBOX_ADAPTER"]).make_fixture()
        self.addCleanup(fixture["cleanup"])
        gateway = Engine(fixture["db_path"], fixture["adapter"], fixture["clock"], fixture["policy_service"])
        self.addCleanup(gateway.close)
        body = fixture["action"]
        gateway.principal("sandbox-worker", {body["permission"]})
        cid = gateway.contract(fixture["contract"])
        aid = gateway.plan(cid, "sandbox-worker", body)
        nonce = gateway.approve(aid, fixture["clock"]() + 60)
        state = gateway.dispatch(aid, nonce)
        if state == "UNKNOWN":
            state = gateway.reconcile(aid)
        self.assertEqual(state, "CONFIRMED", "real external execution evidence required")
        with self.assertRaises(Rejected):
            gateway.dispatch(aid, nonce)
        fixture["adapter"].assert_effect_count(aid, 1)
