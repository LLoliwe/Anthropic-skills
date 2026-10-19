"""Pin the official TypeSafe agent skill to reviewed upstream Git blobs.

This verifies project-local installation, not a live Jev account.
"""
import hashlib
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
SKILL_DIR = REPO_ROOT / ".agents" / "skills" / "typesafe-ai"
EXPECTED_BLOBS = {
    "SKILL.md": "0109513f9656917dc93cbc5ecddfca465a53ce66",
    "LICENSE": "8c73b41b89d9a76ddf0fdb0edfaafdda800d36e8",
}


def git_blob_sha(path):
    content = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(content)).encode("ascii") + b"\0" + content).hexdigest()


class OfficialSkillTests(unittest.TestCase):
    def test_files_exist(self):
        for name in EXPECTED_BLOBS:
            with self.subTest(name=name):
                self.assertTrue((SKILL_DIR / name).is_file())

    def test_upstream_blob_identity(self):
        for name, blob in EXPECTED_BLOBS.items():
            with self.subTest(name=name):
                self.assertEqual(git_blob_sha(SKILL_DIR / name), blob)

    def test_metadata(self):
        source = (SKILL_DIR / "SKILL.md").read_text()
        self.assertTrue(source.startswith("---\nname: typesafe-ai\n"))
        self.assertIn("license: MIT", source)
        self.assertIn("https://docs.typesafe.ai/llms.txt", source)

    def test_skill_contains_no_inline_api_secret(self):
        source = (SKILL_DIR / "SKILL.md").read_text()
        self.assertNotIn("TYPESAFE_API_KEY=", source)
        self.assertIn("Keep API credentials server-side", source)


if __name__ == "__main__":
    unittest.main()
