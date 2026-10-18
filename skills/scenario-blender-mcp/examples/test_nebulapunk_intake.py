"""Unit tests for R0 cost, licence, hash and ownership gates. No Blender."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from nebulapunk_intake import validate_vendor_asset, OFFICIAL_URL


class TestIntake(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        root = Path(temp.name)
        self.asset = root / "trial.blend"
        self.asset.write_bytes(b"BLENDER-test-not-real")
        self.digest = hashlib.sha256(self.asset.read_bytes()).hexdigest()
        self.receipt = root / "approval.json"
        self.record = {
            "product": "Nebulapunk Free", "source": OFFICIAL_URL,
            "cost_usd": 0, "approved_for_internal_test": True,
            "commercial_use_review": "internal-only",
            "owner_reviewer": "Independent operator",
            "sha256": self.digest
        }
        self.save()

    def save(self):
        self.receipt.write_text(json.dumps(self.record))

    def check(self):
        return validate_vendor_asset(self.asset, self.receipt,
                                     self.digest, "Light Nebula")

    def test_valid_local_review(self):
        self.assertEqual(self.check()["sha256"], self.digest)

    def test_mismatched_sha(self):
        with self.assertRaises(ValueError):
            validate_vendor_asset(self.asset, self.receipt, "a" * 64, "Light Nebula")

    def test_nonzero_spend_forbidden(self):
        self.record["cost_usd"] = 5
        self.save()
        with self.assertRaises(ValueError):
            self.check()

    def test_not_approved_for_test(self):
        self.record["approved_for_internal_test"] = False
        self.save()
        with self.assertRaises(ValueError):
            self.check()

    def test_unknown_rights_forbidden(self):
        self.record["commercial_use_review"] = "unknown"
        self.save()
        with self.assertRaises(ValueError):
            self.check()

    def test_missing_reviewer_forbidden(self):
        self.record["owner_reviewer"] = ""
        self.save()
        with self.assertRaises(ValueError):
            self.check()

    def test_wrong_edition_forbidden(self):
        self.record["product"] = "Nebulapunk+"
        self.save()
        with self.assertRaises(ValueError):
            self.check()

    def test_symlink_forbidden(self):
        shortcut = self.asset.parent / "shortcut.blend"
        shortcut.symlink_to(self.asset)
        with self.assertRaises(ValueError):
            validate_vendor_asset(shortcut, self.receipt,
                                  self.digest, "Light Nebula")

    def test_missing_collection_forbidden(self):
        with self.assertRaises(ValueError):
            validate_vendor_asset(self.asset, self.receipt, self.digest, "")


if __name__ == "__main__":
    unittest.main()
