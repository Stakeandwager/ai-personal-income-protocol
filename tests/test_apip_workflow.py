import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.apip_workflow import approval_scope, approve_action, build_workflow, execute_local_action


class APIPWorkflowTests(unittest.TestCase):
    def test_external_action_is_blocked_before_approval_when_no_adapter_exists(self):
        workflow = build_workflow(
            "Apply for paid work and earn income",
            [{"type": "submit_proposal", "description": "Apply to a specific listing", "data": {"url": "https://example.com/job"}}],
        )
        action = workflow["actions"][0]
        self.assertEqual(action["status"], "CAPABILITY_MISSING")
        self.assertTrue(action["approval_required"])
        self.assertFalse(action.get("approval_granted", False))
        self.assertEqual(workflow["verified_income"], 0)

    def test_safe_local_draft_is_ready_and_truthful_without_profile_facts(self):
        workflow = build_workflow("Prepare a proposal", [{
            "type": "prepare_proposal_draft",
            "data": {"title": "Spreadsheet cleanup", "buyer_request": "Clean duplicates"},
        }])
        action = workflow["actions"][0]
        self.assertEqual(action["status"], "READY")
        with tempfile.TemporaryDirectory() as tmp:
            event = execute_local_action(workflow, action["action_id"], Path(tmp))
            output = Path(event["evidence"]["path"]).read_text(encoding="utf-8")
        self.assertEqual(workflow["status"], "COMPLETED")
        self.assertIn("[Add only relevant experience you can truthfully confirm", output)
        self.assertIn("DRAFT ONLY. Not submitted.", output)
        self.assertFalse(event["external_action"])
        self.assertFalse(event["payment_verified"])
        self.assertEqual(len(event["evidence"]["sha256"]), 64)

    def test_financial_and_legal_actions_are_not_locally_executable(self):
        workflow = build_workflow("Complete paid task", [
            {"type": "spend_money", "data": {"amount": 1000, "currency": "NGN"}},
            {"type": "accept_contract"},
            {"type": "move_money"},
        ])
        self.assertEqual([item["status"] for item in workflow["actions"]], [
            "BLOCKED_BUDGET_LEDGER_UNVERIFIED", "OWNER_HANDOFF", "OWNER_HANDOFF",
        ])
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(PermissionError):
                execute_local_action(workflow, workflow["actions"][0]["action_id"], Path(tmp))

    def test_reconciled_spend_still_needs_explicit_limit_and_capability(self):
        workflow = build_workflow(
            "Apply to one role",
            [{"type": "spend_money", "data": {"amount": 400, "currency": "NGN"}}],
            {"spending_balance_verified": True, "spending_limit": 300},
        )
        self.assertEqual(workflow["actions"][0]["status"], "BLOCKED_SPENDING_LIMIT")

    def test_approval_scope_must_match_and_no_unavailable_action_can_be_approved(self):
        workflow = build_workflow(
            "Submit an application",
            [{"type": "submit_proposal", "data": {"url": "https://example.com/job"}}],
        )
        action = workflow["actions"][0]
        with self.assertRaises(PermissionError):
            approve_action(workflow, action["action_id"], approval_scope(action))

    def test_live_research_is_capability_blocked_not_falsely_completed(self):
        workflow = build_workflow("Find available jobs", [{"type": "research_public_listing"}])
        self.assertEqual(workflow["actions"][0]["status"], "CAPABILITY_MISSING")
        self.assertEqual(workflow["status"], "BLOCKED")

    def test_unsupported_action_fails_closed(self):
        workflow = build_workflow("Make income", [{"type": "arbitrary_shell", "data": {"command": "echo unsafe"}}])
        self.assertEqual(workflow["actions"][0]["status"], "UNSUPPORTED")

    def test_requires_nonempty_objective(self):
        with self.assertRaises(ValueError):
            build_workflow(" ", [])


if __name__ == "__main__":
    unittest.main()
