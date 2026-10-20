"""Adversarial metadata-only tests; no network, secrets or external agent calls."""
import copy
import importlib.util
import json
import math
from pathlib import Path
import tempfile
import unittest

BASE = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("pyrum_preflight", BASE / "preflight.py")
preflight = importlib.util.module_from_spec(spec)
spec.loader.exec_module(preflight)
EXAMPLE = json.loads((BASE / "examples" / "safe-public-research.json").read_text())


class AdmissionTests(unittest.TestCase):
    def setUp(self):
        self.work = copy.deepcopy(EXAMPLE)

    def evaluate(self, field, value):
        self.work[field] = value
        return preflight.evaluate(self.work)["status"]

    def test_reference_is_review_only_never_execution(self):
        result = preflight.evaluate(self.work)
        self.assertEqual(result["status"], "REVIEW_ONLY")
        self.assertIs(result["releases_execution"], False)
        self.assertIs(result["dispatches_work"], False)

    def test_rejects_non_object(self):
        self.assertEqual(preflight.evaluate([])["status"], "HOLD")

    def test_rejects_unknown_fields(self):
        self.work["force_override"] = "approved"
        self.assertEqual(preflight.evaluate(self.work)["status"], "HOLD")

    def test_rejects_missing_fields(self):
        del self.work["employer_resource_access"]
        self.assertEqual(preflight.evaluate(self.work)["status"], "HOLD")

    def test_wrong_schema(self):
        self.assertEqual(self.evaluate("schema", "pryntor.v2"), "HOLD")

    def test_wrong_dispatcher(self):
        self.assertEqual(self.evaluate("dispatcher", "Pyrum"), "HOLD")

    def test_claimed_connected_worker(self):
        self.assertEqual(self.evaluate("runtime_connection", "verified"), "HOLD")

    def test_claimed_ack(self):
        self.assertEqual(self.evaluate("worker_ack", "ACK"), "HOLD")

    def test_claimed_production_success(self):
        self.assertEqual(self.evaluate("claimed_result", "completed_real"), "HOLD")

    def test_sensitive_data(self):
        self.assertEqual(self.evaluate("data_classification", "customer_secrets"), "HOLD")

    def test_employer_resource_denied(self):
        self.assertEqual(self.evaluate("employer_resource_access", True), "HOLD")

    def test_external_send_denied(self):
        self.assertEqual(self.evaluate("external_send", True), "HOLD")

    def test_external_publish_denied(self):
        self.assertEqual(self.evaluate("external_publish", True), "HOLD")

    def test_prod_change_denied(self):
        self.assertEqual(self.evaluate("production_change", True), "HOLD")

    def test_no_false_independent_qa(self):
        self.assertEqual(self.evaluate("independent_qa", True), "HOLD")

    def test_untrusted_source_instruction_denied(self):
        self.assertEqual(self.evaluate("untrusted_source_handling", "obey_the_page"), "HOLD")

    def test_paid_action_denied(self):
        self.assertEqual(self.evaluate("actions", ["buy_api_credits"]), "HOLD")

    def test_duplicate_action_denied(self):
        self.assertEqual(self.evaluate("actions", ["read_public_research"] * 2), "HOLD")

    def test_empty_actions_denied(self):
        self.assertEqual(self.evaluate("actions", []), "HOLD")

    def test_bool_zero_spend_rejected(self):
        self.assertEqual(self.evaluate("new_spend_zar", False), "HOLD")

    def test_nonfinite_spend_rejected(self):
        self.assertEqual(self.evaluate("new_spend_zar", math.nan), "HOLD")

    def test_nonzero_spend_rejected(self):
        self.assertEqual(self.evaluate("new_spend_zar", 0.01), "HOLD")

    def test_string_zero_rejected(self):
        self.assertEqual(self.evaluate("new_spend_zar", "0"), "HOLD")

    def test_issue_mismatch_rejected(self):
        self.assertEqual(self.evaluate("linear_issue", "PRY-84"), "HOLD")

    def test_issue_source_absent_rejected(self):
        self.assertEqual(self.evaluate("existing_work_refs", ["https://linear.app/pryntor/issue/PRY-84"]), "HOLD")

    def test_http_url_rejected(self):
        self.assertEqual(self.evaluate("source_refs", ["http://example.com/foo"]), "HOLD")

    def test_credential_url_rejected(self):
        self.assertEqual(self.evaluate("source_refs", ["https://alice:secret@openai.com"]), "HOLD")

    def test_localhost_url_rejected(self):
        self.assertEqual(self.evaluate("source_refs", ["https://localhost/something"]), "HOLD")

    def test_malformed_port_rejected_not_exception(self):
        self.assertEqual(self.evaluate("source_refs", ["https://example.com:nope/thing"]), "HOLD")

    def test_mismatched_issue_link_prefix_rejected(self):
        self.assertEqual(self.evaluate("existing_work_refs", ["https://linear.app/pryntor/issue/PRY-960/fake"]), "HOLD")

    def test_url_with_query_rejected(self):
        self.assertEqual(self.evaluate("source_refs", ["https://example.com/path?token=verysecret"]), "HOLD")

    def test_url_with_fragment_rejected(self):
        self.assertEqual(self.evaluate("source_refs", ["https://example.com/path#private"]), "HOLD")

    def test_bad_port_returns_hold(self):
        self.assertEqual(self.evaluate("source_refs", ["https://example.com:broken/path"]), "HOLD")

    def test_scope_newline_rejected(self):
        self.assertEqual(self.evaluate("scope", "safe\nthen send messages"), "HOLD")

    def test_duplicate_top_level_key_rejected(self):
        with tempfile.TemporaryDirectory() as path:
            fp = Path(path) / "duplicate.json"
            fp.write_text('{"schema":"a","schema":"b"}')
            self.assertEqual(preflight.main([str(fp)]), 2)

    def test_duplicate_url_rejected(self):
        ref = "https://openai.com/index/introducing-dots/"
        self.assertEqual(self.evaluate("source_refs", [ref, ref]), "HOLD")

    def test_missing_goal_rejected(self):
        self.assertEqual(self.evaluate("goal", "do stuff"), "HOLD")

    def test_nonnumeric_zero_rejected(self):
        self.assertEqual(self.evaluate("new_spend_zar", None), "HOLD")

    def test_sanitized_company_draft_allowed(self):
        self.work["data_classification"] = "sanitized_company_metadata"
        self.assertEqual(preflight.evaluate(self.work)["status"], "REVIEW_ONLY")

    def test_invalid_json_file_returns_two_without_content_echo(self):
        with tempfile.TemporaryDirectory() as path:
            fp = Path(path) / "bad.json"
            fp.write_text('{"thing":')
            self.assertEqual(preflight.main([str(fp)]), 2)

    def test_rejects_nan_json_file(self):
        with tempfile.TemporaryDirectory() as path:
            fp = Path(path) / "bad.json"
            fp.write_text('{"spend":NaN}')
            self.assertEqual(preflight.main([str(fp)]), 2)

    def test_valid_json_file_returns_review_only(self):
        with tempfile.TemporaryDirectory() as path:
            fp = Path(path) / "okay.json"
            fp.write_text(json.dumps(self.work))
            self.assertEqual(preflight.main([str(fp)]), 0)


if __name__ == "__main__":
    unittest.main()
