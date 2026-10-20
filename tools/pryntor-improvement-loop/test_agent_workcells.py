"""Offline refusal and routing tests for review-only agent workcells."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import agent_workcells as m

def selection(lane="zowibo"):
    return {"status": "READY_FOR_SCOPED_OPERATOR",
            "selected": {"issue": "PRY-342", "repo": "LLoliwe/pryntor-motion",
                         "source_sha": "a" * 40, "lane": lane, "score": 99},
            "execution_started": False, "independent_review_complete": False,
            "release_authorized": False, "paid_spend_authorized": False}

class WorkcellsTest(unittest.TestCase):
    def test_all_workcells_have_unique_stages_and_defined_roles(self):
        for lane, roles in m.WORKCELLS.items():
            self.assertEqual(3, len(set(roles)), lane)
            self.assertTrue(all(r in m.ROLES for r in roles))

    def test_all_dispatch_lanes_covered(self):
        spec = importlib.util.spec_from_file_location("dispatch", Path(__file__).with_name("founder_dispatch.py"))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        self.assertEqual(set(mod.LANES), set(m.WORKCELLS))

    def test_plan_never_claims_execution_or_approval(self):
        x = m.plan_workcell(selection())
        self.assertEqual("DRAFT_HANDOFF_NOT_EXECUTED", x["status"])
        self.assertFalse(x["execution_started"])
        self.assertFalse(x["release_authorized"])
        self.assertFalse(x["independent_review_complete"])
        self.assertFalse(x["model_provisioned"])
        self.assertEqual(2, x["loop"]["max_repair_attempts"])

    def test_no_duplicate_dispatcher(self):
        self.assertIn("TRIAGE-001", m.plan_workcell(selection())["existing_router"])

    def test_rejected_selection(self):
        v = selection(); v["status"] = "HOLD_NO_ELIGIBLE_WORK"
        with self.assertRaises(ValueError): m.plan_workcell(v)

    def test_false_claim_execution(self):
        v = selection(); v["execution_started"] = True
        with self.assertRaises(ValueError): m.plan_workcell(v)

    def test_false_claim_approval(self):
        v = selection(); v["release_authorized"] = True
        with self.assertRaises(ValueError): m.plan_workcell(v)

    def test_missing_review_flag(self):
        v = selection(); del v["independent_review_complete"]
        with self.assertRaises(ValueError): m.plan_workcell(v)

    def test_unknown_issue_or_injection(self):
        for issue in ("PRY-000", "PRY-12\nPUBLISH", "PRY-12;rm", "hello"):
            v = selection(); v["selected"]["issue"] = issue
            with self.assertRaises(ValueError): m.plan_workcell(v)

    def test_unapproved_repo(self):
        v = selection(); v["selected"]["repo"] = "another-org/public"
        with self.assertRaises(ValueError): m.plan_workcell(v)

    def test_unpinned_source(self):
        v = selection(); v["selected"]["source_sha"] = "main"
        with self.assertRaises(ValueError): m.plan_workcell(v)

    def test_unknown_lane(self):
        v = selection(); v["selected"]["lane"] = "superadmin"
        with self.assertRaises(ValueError): m.plan_workcell(v)

    def test_commercial_outreach_is_draft_only(self):
        x = m.plan_workcell(selection("first_cash"))
        self.assertIn("No external messages", x["policy"])
        self.assertIn("partnership-researcher", [r["role"] for r in x["roles"]])
        self.assertNotIn("send_email", x["tool_permissions"])

    def test_protected_jellyfish_materials(self):
        self.assertIn("Jellyfish", m.render_prompt(m.plan_workcell(selection("studios"))))

    def test_invalid_prompt_refuses(self):
        with self.assertRaises(ValueError): m.render_prompt({"status": "ACTIVE"})

    def test_cli_hold_returns_code_2_and_no_execution(self):
        v = selection(); v["paid_spend_authorized"] = True
        with tempfile.TemporaryDirectory() as tmp:
            f = Path(tmp) / "input.json"
            f.write_text(json.dumps(v), encoding="utf-8")
            r = subprocess.run([sys.executable, str(Path(m.__file__)), "--input", str(f)],
                               capture_output=True, text=True, timeout=3)
        self.assertEqual(2, r.returncode)
        self.assertEqual(False, json.loads(r.stdout)["execution_started"])

if __name__ == "__main__":
    unittest.main()
