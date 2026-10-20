"""Negative and positive tests for the offline assurance evidence gate."""
import copy
import datetime as dt
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PATH = Path(__file__).with_name("assurance_gate.py")
SPEC = importlib.util.spec_from_file_location("pryntor_assurance_gate", PATH)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

R = {"schema_version": 1, "project": "offline-synthetic-fixture",
     "required_controls": ["SEC-ACCESS", "PRIV-CONSENT"], "max_evidence_age_days": 90}
GOOD_CONTROL = {
    "id": "SEC-ACCESS",
    "status": "VERIFIED",
    "owner": "SYNTHETIC-CONTROL-OWNER",
    "reviewer": "SYNTHETIC-OTHER-REVIEWER",
    "independent_review": True,
    "evidence_url": "https://example.org/synthetic-evidence",
    "evidence_sha256": "a" * 64,
    "reviewed_at": "2026-10-19",
    "valid_until": "2026-12-01",
}
E = {"schema_version": 1, "project": R["project"],
     "controls": [GOOD_CONTROL, {**GOOD_CONTROL, "id": "PRIV-CONSENT"}]}
AS_OF = dt.date(2026, 10, 20)


class AssuranceGateTests(unittest.TestCase):
    def setUp(self):
        self.r = copy.deepcopy(R)
        self.e = copy.deepcopy(E)

    def check(self):
        return MODULE.evaluate(self.r, self.e, as_of=AS_OF)

    def test_valid_synthetic_complete_record_passes_structural_check(self):
        self.assertEqual(self.check(), (True, []))

    def test_missing_required_fails_closed(self):
        self.e["controls"].pop()
        self.assertIn("REQUIRED CONTROL MISSING", str(self.check()[1]))

    def test_open_status_fails(self):
        self.e["controls"][0]["status"] = "OPEN"
        self.assertFalse(self.check()[0])

    def test_prior_evidence_cannot_be_verification(self):
        self.e["controls"][0]["status"] = "PRIOR EVIDENCE"
        self.assertFalse(self.check()[0])

    def test_missing_independent_flag_fails(self):
        self.e["controls"][0]["independent_review"] = False
        self.assertFalse(self.check()[0])

    def test_self_review_fails(self):
        self.e["controls"][0]["reviewer"] = self.e["controls"][0]["owner"].lower()
        self.assertFalse(self.check()[0])

    def test_no_reviewer_fails(self):
        del self.e["controls"][0]["reviewer"]
        self.assertFalse(self.check()[0])

    def test_url_must_be_https(self):
        self.e["controls"][0]["evidence_url"] = "http://example.org"
        self.assertFalse(self.check()[0])

    def test_no_local_url(self):
        self.e["controls"][0]["evidence_url"] = "https://localhost"
        self.assertFalse(self.check()[0])

    def test_url_with_password_fails(self):
        self.e["controls"][0]["evidence_url"] = "https://user:pass@example.org"
        self.assertFalse(self.check()[0])

    def test_missing_hash_fails(self):
        self.e["controls"][0].pop("evidence_sha256")
        self.assertFalse(self.check()[0])

    def test_wrong_hash_fails(self):
        self.e["controls"][0]["evidence_sha256"] = "123"
        self.assertFalse(self.check()[0])

    def test_stale_evidence_fails(self):
        self.e["controls"][0]["reviewed_at"] = "2026-01-01"
        self.assertFalse(self.check()[0])

    def test_future_review_fails(self):
        self.e["controls"][0]["reviewed_at"] = "2027-01-01"
        self.assertFalse(self.check()[0])

    def test_expired_evidence_fails(self):
        self.e["controls"][0]["valid_until"] = "2026-10-19"
        self.assertFalse(self.check()[0])

    def test_duplicate_records_fail(self):
        self.e["controls"].append(copy.deepcopy(self.e["controls"][0]))
        self.assertFalse(self.check()[0])

    def test_no_required_controls_fails(self):
        self.r["required_controls"] = []
        self.assertFalse(self.check()[0])

    def test_wrong_project_fails(self):
        self.e["project"] = "another-client"
        self.assertFalse(self.check()[0])

    def test_malformed_json_cli_exit_2(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)
            (p / "rules.json").write_text(json.dumps(self.r))
            (p / "evidence.json").write_text("{invalid")
            run = subprocess.run([sys.executable, str(PATH), str(p/"rules.json"), str(p/"evidence.json")],
                                  capture_output=True, text=True)
            self.assertEqual(run.returncode, 2)
            self.assertEqual(json.loads(run.stdout)["gate"], "FAIL")

    def test_open_control_cli_exit_1(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)
            self.e["controls"][0]["status"] = "OPEN"
            (p/"rules.json").write_text(json.dumps(self.r))
            (p/"evidence.json").write_text(json.dumps(self.e))
            run = subprocess.run([sys.executable, str(PATH), str(p/"rules.json"), str(p/"evidence.json"),
                                  "--as-of", "2026-10-20"], capture_output=True, text=True)
            self.assertEqual(run.returncode, 1)
            self.assertEqual(json.loads(run.stdout)["gate"], "FAIL")


if __name__ == "__main__":
    unittest.main()
