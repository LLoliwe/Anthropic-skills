"""Adversarial offline tests for the founder-priority router. No external calls."""
from copy import deepcopy
from datetime import datetime, timezone
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).with_name("founder_dispatch.py")
loader = importlib.util.spec_from_file_location("founder_dispatch", SCRIPT)
fd = importlib.util.module_from_spec(loader)
loader.loader.exec_module(fd)
NOW = datetime(2026, 10, 19, 2, 0, tzinfo=timezone.utc)
A = "a" * 40
B = "b" * 40
H = "c" * 64


def task(issue="PRY-342", lane="zowibo", **changes):
    t = {
        "issue": issue, "repo": "LLoliwe/pryntor-motion", "source_sha": A,
        "source_url": "https://github.com/LLoliwe/pryntor-motion/pull/10",
        "lane": lane, "urgency": "P0",
        "impact": "broken_user_journey", "effort": "small",
        "updated_at": "2026-10-19T01:50:00+00:00",
        "failure_state": "reproduced_failing",
        "repro": "Open real Play and assert it enters active gameplay.",
        "acceptance": "Play starts the actual level and movement responds.",
        "negative_case": "Wrong pointer must not steal active player controls.",
        "action": "internal_patch", "risks": [],
        "claimed_by_other": False, "spend_required": 0,
        "review_required": True,
    }
    t.update(changes)
    return t


def evidence(lane="zowibo", **changes):
    e = {
        "issue": "PRY-342", "repo": "LLoliwe/pryntor-motion",
        "lane": lane, "base_sha": A, "result_sha": B,
        "artifact_sha256": H, "source_changed": True,
        "tests": [{"type": kind, "command": ["python3", "-m", "unittest"],
                   "exit_code": 0, "log_sha256": H}
                  for kind in ["functional", "negative", "browser"]],
        "independent_review": "PASSED",
    }
    e.update(changes)
    return e


class SelectTests(unittest.TestCase):
    def test_select_prioritizes_verified_product_breakage(self):
        lower = task("PRY-191", "studios", urgency="P1", impact="quality_gap")
        result = fd.select({"schema_version": 1, "tasks": [lower, task()]}, NOW)
        self.assertEqual(result["status"], "READY_FOR_SCOPED_OPERATOR")
        self.assertEqual(result["selected"]["issue"], "PRY-342")
        self.assertFalse(result["execution_started"])
        self.assertFalse(result["release_authorized"])

    def test_security_p0_takes_precedence_at_same_urgency(self):
        sec = task("PRY-19", "security")
        result = fd.select({"schema_version": 1, "tasks": [task(), sec]}, NOW)
        self.assertEqual(result["selected"]["issue"], "PRY-19")

    def test_paid_model_task_is_rejected_even_when_high_priority(self):
        bad = task("PRY-19", "security", action="paid_api", spend_required=1)
        result = fd.select({"schema_version": 1, "tasks": [bad, task()]}, NOW)
        self.assertEqual(result["selected"]["issue"], "PRY-342")
        self.assertIn("NONZERO_OR_UNVERIFIED_SPEND", result["rejected"][0]["reasons"])
        self.assertIn("UNAPPROVED_ACTION", result["rejected"][0]["reasons"])

    def test_outbound_merge_deployment_and_data_are_blocked(self):
        for action in ("send", "deploy", "merge", "publish", "purchase", "iam_change"):
            with self.subTest(action=action):
                item = task(action=action)
                self.assertIn("UNAPPROVED_ACTION", fd.screen(item, NOW))
        item = task(risks=["customer_data"])
        self.assertIn("UNREVIEWED_RISK", fd.screen(item, NOW))

    def test_stale_or_future_snapshot_not_admissible(self):
        past = task(updated_at="2026-10-17T20:00:00Z")
        future = task(updated_at="2026-10-19T02:06:00Z")
        self.assertIn("STALE_OR_FUTURE_SNAPSHOT", fd.screen(past, NOW))
        self.assertIn("STALE_OR_FUTURE_SNAPSHOT", fd.screen(future, NOW))

    def test_claimed_other_worker_cannot_be_raced(self):
        claimed = task(claimed_by_other=True)
        self.assertIn("OWNERSHIP_NOT_CLEAR", fd.screen(claimed, NOW))

    def test_unverified_or_already_passing_is_not_a_task(self):
        for state in ("already_passing", "not_run", "agent_claim_only"):
            with self.subTest(state=state):
                self.assertIn("NO_REPRODUCED_FAILURE",
                              fd.screen(task(failure_state=state), NOW))

    def test_missing_negative_and_review_gate_rejected(self):
        x = task(negative_case="none", review_required=False)
        problems = fd.screen(x, NOW)
        self.assertIn("MISSING_NEGATIVE_CASE", problems)
        self.assertIn("MISSING_REVIEW_GATE", problems)

    def test_unowned_repo_rejected(self):
        x = task(repo="external/clone", source_url="https://github.com/external/clone")
        self.assertIn("UNAPPROVED_SOURCE", fd.screen(x, NOW))

    def test_empty_queue_does_not_invent_work(self):
        result = fd.select({"schema_version": 1, "tasks": []}, NOW)
        self.assertEqual(result["status"], "HOLD_NO_ELIGIBLE_WORK")
        self.assertIsNone(result["selected"])

    def test_duplicate_issue_fails_closed(self):
        with self.assertRaises(ValueError):
            fd.select({"schema_version": 1, "tasks": [task(), task()]}, NOW)

    def test_unexpected_fields_fails_closed(self):
        with self.assertRaises(ValueError):
            fd.select({"schema_version": 1, "tasks": [task(paid_approval=True)]}, NOW)

    def test_snapshot_with_no_timezone_is_invalid(self):
        self.assertIn("INVALID_SNAPSHOT_TIME",
                      fd.screen(task(updated_at="2026-10-19T01:50:00"), NOW))

    def test_tiebreak_is_stable_by_canonical_issue(self):
        first, second = task("PRY-343"), task("PRY-342")
        result = fd.select({"schema_version": 1, "tasks": [first, second]}, NOW)
        self.assertEqual(result["selected"]["issue"], "PRY-342")

    def test_bool_spend_not_accepted_as_zero_dollar_approval(self):
        self.assertIn("NONZERO_OR_UNVERIFIED_SPEND",
                      fd.screen(task(spend_required=False), NOW))

    def test_malformed_nested_fields_reject_without_type_error(self):
        for field in ("repo", "lane", "urgency", "impact", "effort", "action"):
            with self.subTest(field=field):
                wrong = task(**{field: ["untrusted"]})
                problems = fd.screen(wrong, NOW)
                self.assertTrue(problems)

    def test_mismatched_repo_url_is_not_provenance(self):
        wrong = task(source_url="https://github.com/LLoliwe/Leseli/pull/12")
        self.assertIn("UNAPPROVED_SOURCE", fd.screen(wrong, NOW))

    def test_boolean_schema_version_rejected(self):
        with self.assertRaises(ValueError):
            fd.select({"schema_version": True, "tasks": [task()]}, NOW)


class EvidenceTests(unittest.TestCase):
    def test_complete_manifest_is_still_not_independent_release_proof(self):
        result = fd.evidence_gate(evidence())
        self.assertEqual(result["status"], "READY_FOR_EXTERNAL_RECEIPT_CHECK")
        self.assertFalse(result["external_test_logs_authenticated"])
        self.assertFalse(result["human_review_authenticated"])
        self.assertFalse(result["release_authorized"])

    def test_ui_product_cannot_pass_on_unit_tests_alone(self):
        e = evidence(tests=evidence()["tests"][:2])
        result = fd.evidence_gate(e)
        self.assertIn("MISSING_BROWSER_PROOF", result["gaps"])

    def test_backend_does_not_require_browser(self):
        e = evidence(lane="robotics_sim", tests=evidence()["tests"][:2])
        self.assertEqual(fd.evidence_gate(e)["status"], "READY_FOR_EXTERNAL_RECEIPT_CHECK")

    def test_intentionally_failing_negative_test_cannot_pass(self):
        e = evidence()
        e["tests"][1]["exit_code"] = 1
        result = fd.evidence_gate(e)
        self.assertIn("INVALID_OR_FAILED_TEST", result["gaps"])
        self.assertIn("MISSING_NEGATIVE_PROOF", result["gaps"])

    def test_bool_or_fabricated_test_exit_code_rejected(self):
        e = evidence()
        e["tests"][0]["exit_code"] = True
        self.assertIn("INVALID_OR_FAILED_TEST", fd.evidence_gate(e)["gaps"])

    def test_no_actual_change_no_technical_success(self):
        e = evidence(result_sha=A, source_changed=False)
        result = fd.evidence_gate(e)
        self.assertIn("NO_NEW_COMMIT", result["gaps"])
        self.assertIn("NO_WORK_PRODUCT", result["gaps"])

    def test_missing_human_qa_keeps_the_gate_closed(self):
        self.assertIn("INDEPENDENT_REVIEW_PENDING",
                      fd.evidence_gate(evidence(independent_review="PENDING"))["gaps"])

    def test_new_fields_cannot_override_the_release_gate(self):
        with self.assertRaises(ValueError):
            fd.evidence_gate(evidence(release_authorized=True))

    def test_malformed_test_type_does_not_crash(self):
        e = evidence()
        e["tests"][0]["type"] = ["functional"]
        self.assertIn("INVALID_OR_FAILED_TEST", fd.evidence_gate(e)["gaps"])

    def test_unknown_owner_type_does_not_crash(self):
        e = evidence(repo=["LLoliwe/pryntor-motion"])
        self.assertIn("UNKNOWN_OWNER_OR_LANE", fd.evidence_gate(e)["gaps"])

    def test_unknown_lane_type_does_not_crash(self):
        e = evidence(lane=["zowibo"])
        self.assertIn("UNKNOWN_OWNER_OR_LANE", fd.evidence_gate(e)["gaps"])


class CLITests(unittest.TestCase):
    def test_cli_deterministic_replay_and_exit_code(self):
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / "tasks.json"
            source.write_text(json.dumps({"schema_version": 1, "tasks": [task()]}))
            proc = subprocess.run([sys.executable, str(SCRIPT), "--mode", "select",
                                   "--input", str(source), "--now", "2026-10-19T02:00:00Z"],
                                  capture_output=True, text=True)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            result = json.loads(proc.stdout)
            self.assertEqual(result["selected"]["issue"], "PRY-342")

    def test_cli_denies_invalid_json_without_executing(self):
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / "bad.json"
            source.write_text("{bad json")
            proc = subprocess.run([sys.executable, str(SCRIPT), "--mode", "select",
                                   "--input", str(source)], capture_output=True, text=True)
            self.assertEqual(proc.returncode, 2)
            self.assertEqual(json.loads(proc.stdout)["status"], "BLOCKED_INVALID_INPUT")


if __name__ == "__main__":
    unittest.main()
