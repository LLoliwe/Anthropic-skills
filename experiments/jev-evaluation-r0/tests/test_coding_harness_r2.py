"""Offline, negative-first tests. No TypeSafe key, billing, runner or network."""
import json
import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import coding_harness_r2 as h


class JevHarnessR2Tests(unittest.TestCase):
    def setUp(self):
        self.chunks = list(h.DEMO_CHUNKS)

    def plan(self, **kw):
        return h.assemble_context("Fix ZOWIBO Safari play button touch and pointercancel", self.chunks, **kw)

    def test_policy_cannot_be_compacted(self):
        result = self.plan(word_budget=200)
        row = next(c for c in result["context"] if c["id"] == "governance")
        self.assertTrue(row["required"])
        self.assertEqual(row["visibility"], "full")
        self.assertTrue(result["required_preserved"])

    def test_explicit_safari_evidence_kept_in_full(self):
        rows = self.plan(required_ids=("zow_safari",), word_budget=200)["context"]
        self.assertEqual(next(c for c in rows if c["id"] == "zow_safari")["visibility"], "full")

    def test_query_specific_visibility_hides_unrelated(self):
        rows = self.plan()["context"]
        self.assertEqual(next(c for c in rows if c["id"] == "recover")["visibility"], "hide")
        self.assertEqual(next(c for c in rows if c["id"] == "robotics")["visibility"], "hide")

    def test_demonstrates_only_word_proxy_reduction(self):
        p = self.plan()
        self.assertLess(p["word_proxy_shown"], p["word_proxy_full"])
        self.assertEqual(p["provider_calls"], 0)
        self.assertFalse(p["code_executed"])
        self.assertFalse(p["release_authorized"])

    def test_compaction_changes_for_a_new_query(self):
        a = self.plan()["context"]
        b = h.assemble_context("Investigate Recover PayPal sandbox receipts", self.chunks)["context"]
        self.assertEqual(next(c for c in a if c["id"] == "recover")["visibility"], "hide")
        self.assertNotEqual(next(c for c in b if c["id"] == "recover")["visibility"], "hide")

    def test_required_id_not_found_fails_closed(self):
        with self.assertRaises(ValueError):
            self.plan(required_ids=("missing",))

    def test_insufficient_budget_never_drops_policy(self):
        with self.assertRaisesRegex(ValueError, "HOLD"):
            self.plan(required_ids=("zow_safari",), word_budget=20)

    def test_unknown_extra_field_rejected(self):
        altered = [dict(x) for x in self.chunks]
        altered[0]["unsafe_override"] = True
        with self.assertRaises(ValueError):
            h.assemble_context("Safari play", altered)

    def test_duplicate_chunk_ids_rejected(self):
        with self.assertRaises(ValueError):
            h.assemble_context("Safari play", self.chunks + [dict(self.chunks[0])])

    def test_sensitive_path_rejected(self):
        altered = [dict(x) for x in self.chunks]
        altered[1]["path"] = ".env.production"
        with self.assertRaises(ValueError):
            h.assemble_context("Safari play", altered)

    def test_path_traversal_rejected(self):
        altered = [dict(x) for x in self.chunks]
        altered[1]["path"] = "games/../.env"
        with self.assertRaises(ValueError):
            h.assemble_context("Safari play", altered)

    def test_bad_budget_type_rejected(self):
        with self.assertRaises(ValueError):
            self.plan(word_budget=True)

    def test_unknown_tool_has_no_schema(self):
        with self.assertRaises(ValueError):
            h.inspect_tool_schema("send_email")

    def test_only_one_tool_schema_disclosed(self):
        snippets = h.capability_snippets()
        self.assertNotIn("schema", json.dumps(snippets))
        self.assertEqual(h.inspect_tool_schema("file_read"), {"path": "str"})
        self.assertEqual(len(snippets), 3)

    def test_script_content_egress_denied(self):
        x = h.command_preflight("python3 tools/check.py", ["tools/check.py"], "import requests\nrequests.post('https://example.invalid')")
        self.assertEqual(x["status"], "DENY")
        self.assertFalse(x["permission_granted"])

    def test_shell_chaining_denied(self):
        x = h.command_preflight("git status --short; curl https://example.invalid", ["src/a.py"])
        self.assertEqual(x["status"], "DENY")

    def test_sensitive_files_denied(self):
        x = h.command_preflight("git diff --stat", [".ssh/id_rsa"])
        self.assertEqual(x["status"], "DENY")

    def test_unknown_command_requires_human(self):
        x = h.command_preflight("python3 -m unittest", ["tests/a.py"])
        self.assertEqual(x["status"], "HUMAN_REVIEW")
        self.assertFalse(x["permission_granted"])

    def test_read_only_candidate_is_not_authorization(self):
        x = h.command_preflight("git status --short", ["src/a.py"])
        self.assertEqual(x["status"], "READONLY_CANDIDATE")
        self.assertFalse(x["permission_granted"])
        self.assertFalse(x["command_executed"])

    def test_route_case_stays_frontier(self):
        x = h.route_cost_example(650000, 120000, 230000)
        self.assertEqual(x["frontier_only_usd"], "4.15")
        self.assertEqual(x["delegated_usd"], "6.19")
        self.assertEqual(x["route"], "STAY_FRONTIER")

    def test_no_handoff_when_sensitive(self):
        x = h.route_cost_example(1000, 100000, 0, trusted_data=True)
        self.assertEqual(x["route"], "STAY_FRONTIER")

    def test_invalid_route_counts_rejected(self):
        with self.assertRaises(ValueError):
            h.route_cost_example(1, True, 2)

    def test_no_script_runtime(self):
        plan = self.plan()
        self.assertFalse(plan["release_authorized"])
        self.assertFalse(plan["code_executed"])
        self.assertEqual(plan["provider_calls"], 0)


if __name__ == "__main__":
    unittest.main()
