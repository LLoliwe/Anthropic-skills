"""Offline negative and positive coverage for the Pryntor MLX-LoRA gate."""

from __future__ import annotations

import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("mlx_lora_gate", HERE / "mlx_lora_gate.py")
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)
FIXTURE = HERE / "fixtures" / "mlx-lm-lora"


class GateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for n in ("train.jsonl", "test.jsonl", "plan.json"):
            (self.root / n).write_bytes((FIXTURE / n).read_bytes())
        self.plan = gate._read_json(self.root / "plan.json")

    def assess(self, obj=None, host=("Linux", "x86_64")):
        return gate.assess(self.plan if obj is None else obj, self.root, host)

    def test_review_only_and_hardware_block(self):
        r = self.assess()
        self.assertEqual(r["status"], "REVIEW_ONLY_VALIDATED")
        self.assertEqual(r["failures"], [])
        self.assertFalse(r["training_started"])
        self.assertFalse(r["mcp_connected"])
        self.assertFalse(r["release_authorized"])
        self.assertTrue(any("Mac Apple Silicon" in s for s in r["pending_for_training"]))
        self.assertTrue(any("model revision" in s for s in r["pending_for_training"]))

    def test_fake_mac_does_not_authorize_training(self):
        r = self.assess(host=("Darwin", "arm64"))
        self.assertFalse(r["training_started"])
        self.assertFalse(r["release_authorized"])
        self.assertTrue(any("validate_model_support" in s for s in r["pending_for_training"]))

    def test_wrong_upstream_commit_rejected(self):
        p = copy.deepcopy(self.plan)
        p["upstream"]["commit"] = "f" * 40
        self.assertEqual(self.assess(p)["status"], "BLOCKED_POLICY")

    def test_wrong_upstream_tag_rejected(self):
        p = copy.deepcopy(self.plan)
        p["upstream"]["tag"] = "main"
        self.assertEqual(self.assess(p)["status"], "BLOCKED_POLICY")

    def test_spend_rejected(self):
        p = copy.deepcopy(self.plan)
        p["controls"]["new_spend_zar"] = 1
        self.assertEqual(self.assess(p)["status"], "BLOCKED_POLICY")

    def test_boolean_cost_bypass_rejected(self):
        p = copy.deepcopy(self.plan)
        p["controls"]["new_spend_zar"] = False
        self.assertEqual(self.assess(p)["status"], "BLOCKED_POLICY")

    def test_confidential_data_rejected(self):
        p = copy.deepcopy(self.plan)
        p["controls"]["contains_personal_or_client_data"] = True
        self.assertEqual(self.assess(p)["status"], "BLOCKED_POLICY")

    def test_child_data_rejected(self):
        p = copy.deepcopy(self.plan)
        p["controls"]["contains_child_data"] = True
        self.assertEqual(self.assess(p)["status"], "BLOCKED_POLICY")

    def test_auto_start_or_promotion_rejected(self):
        for field in ("training_enabled", "automatic_promotion", "external_upload_approved"):
            p = copy.deepcopy(self.plan)
            p["controls"][field] = True
            with self.subTest(field=field):
                self.assertEqual(self.assess(p)["status"], "BLOCKED_POLICY")

    def test_http_transport_rejected(self):
        p = copy.deepcopy(self.plan)
        p["controls"]["mcp_transport"] = "http"
        self.assertEqual(self.assess(p)["status"], "BLOCKED_POLICY")

    def test_checksum_tampering_rejected(self):
        (self.root / "train.jsonl").write_text('{"messages":[]}', encoding="utf-8")
        self.assertEqual(self.assess()["status"], "BLOCKED_POLICY")

    def test_dataset_overlap_rejected(self):
        import hashlib
        same = (self.root / "train.jsonl").read_bytes()
        (self.root / "test.jsonl").write_bytes(same)
        p = copy.deepcopy(self.plan)
        p["data"]["test"]["sha256"] = hashlib.sha256(same).hexdigest()
        r = self.assess(p)
        self.assertEqual(r["status"], "BLOCKED_POLICY")
        self.assertTrue(any("overlap" in s or "independent" in s for s in r["failures"]))

    def test_path_traversal_rejected(self):
        p = copy.deepcopy(self.plan)
        p["data"]["train"]["path"] = "../not-allowed.jsonl"
        self.assertEqual(self.assess(p)["status"], "BLOCKED_POLICY")

    def test_absolute_path_rejected(self):
        p = copy.deepcopy(self.plan)
        p["data"]["train"]["path"] = str(self.root / "train.jsonl")
        self.assertEqual(self.assess(p)["status"], "BLOCKED_POLICY")

    def test_symlink_rejected(self):
        (self.root / "link.jsonl").symlink_to(self.root / "train.jsonl")
        p = copy.deepcopy(self.plan)
        p["data"]["train"]["path"] = "link.jsonl"
        self.assertEqual(self.assess(p)["status"], "BLOCKED_POLICY")

    def test_duplicate_json_keys_rejected(self):
        (self.root / "x.json").write_text('{"controls":{},"controls":{}}', encoding="utf-8")
        with self.assertRaises(gate.DuplicateKeyError):
            gate._read_json(self.root / "x.json")

    def test_invalid_sft_schema_rejected(self):
        import hashlib
        content = b'{"prompt":"hello","completion":"world"}\n{"messages": []}\n'
        (self.root / "train.jsonl").write_bytes(content)
        p = copy.deepcopy(self.plan)
        p["data"]["train"]["sha256"] = hashlib.sha256(content).hexdigest()
        self.assertEqual(self.assess(p)["status"], "BLOCKED_POLICY")

    def test_unverified_model_license_rejected(self):
        p = copy.deepcopy(self.plan)
        p["model"]["license"] = "unknown"
        self.assertEqual(self.assess(p)["status"], "BLOCKED_POLICY")

    def test_unknown_issue_cannot_sneak_into_same_gate(self):
        p = copy.deepcopy(self.plan)
        p["tracking_issue"] = "PRY-ANYTHING"
        self.assertEqual(self.assess(p)["status"], "BLOCKED_POLICY")

    def test_invalid_manifest_rejected(self):
        self.assertEqual(self.assess([])["status"], "BLOCKED_POLICY")


if __name__ == "__main__":
    unittest.main()
