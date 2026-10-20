"""Real and negative controls for the bounded PRY-309 QA runner."""
from pathlib import Path
import hashlib
import subprocess
import tempfile
import unittest

import workcell_execute as worker


class TestQAWorkcell(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        folder = self.root / worker.ROOT_PATH
        folder.mkdir(parents=True)
        for name in worker.SOURCE + worker.TESTS:
            (folder / name).write_text("pass\n", encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    @staticmethod
    def ok(*args, **kwargs):
        return subprocess.CompletedProcess(args[0], 0, "", "Ran 8 tests in 0.01s\n\nOK\n")

    def test_executes_real_fixed_test_argv_and_no_secrets(self):
        observed = []
        def runner(*args, **kwargs):
            observed.append((args, kwargs))
            return self.ok(*args, **kwargs)
        receipt, log = worker.run_workcell(self.root, execute=runner)
        self.assertEqual(receipt["status"], "QA_EXECUTED_REVIEW_REQUIRED")
        self.assertEqual(receipt["test_count"], 8)
        self.assertEqual(observed[0][0][0], list(worker.CMD))
        self.assertNotIn("GITHUB_TOKEN", observed[0][1]["env"])
        self.assertFalse(receipt["release_authorized"])
        self.assertEqual(0, receipt["model_workers_provisioned"])
        self.assertEqual(hashlib.sha256(log.encode()).hexdigest(), receipt["test_log_sha256"])

    def test_failed_tests_stay_on_hold(self):
        def fail(*args, **kwargs):
            return subprocess.CompletedProcess(args[0], 1, "", "Ran 8 tests in 0.01s\nFAILED\n")
        self.assertEqual(worker.run_workcell(self.root, execute=fail)[0]["status"], "HOLD_QA_FAILED")

    def test_zero_tests_do_not_pass(self):
        def fake(*args, **kwargs):
            return subprocess.CompletedProcess(args[0], 0, "", "Ran 0 tests in 0.01s\nOK\n")
        self.assertEqual(worker.run_workcell(self.root, execute=fake)[0]["status"], "HOLD_QA_FAILED")

    def test_implicit_ok_without_test_report_does_not_pass(self):
        def fake(*args, **kwargs):
            return subprocess.CompletedProcess(args[0], 0, "", "OK\n")
        self.assertEqual(worker.run_workcell(self.root, execute=fake)[0]["status"], "HOLD_QA_FAILED")

    def test_timeout_holds(self):
        def bad(*args, **kwargs):
            raise subprocess.TimeoutExpired(args[0], 75)
        receipt, _ = worker.run_workcell(self.root, execute=bad)
        self.assertEqual(receipt["status"], "HOLD_QA_FAILED")
        self.assertTrue(receipt["timed_out"])

    def test_source_mutation_stops_acceptance(self):
        def tamper(*args, **kwargs):
            (self.root / worker.ROOT_PATH / worker.SOURCE[0]).write_text("changed\n")
            return self.ok(*args, **kwargs)
        receipt, _ = worker.run_workcell(self.root, execute=tamper)
        self.assertEqual(receipt["status"], "HOLD_QA_FAILED")
        self.assertFalse(receipt["source_immutable"])

    def test_symlinked_source_is_refused(self):
        original = self.root / worker.ROOT_PATH / worker.SOURCE[0]
        original.unlink()
        original.symlink_to(self.root / worker.ROOT_PATH / worker.SOURCE[1])
        with self.assertRaises(ValueError):
            worker.run_workcell(self.root, execute=self.ok)

    def test_missing_test_is_refused(self):
        (self.root / worker.ROOT_PATH / worker.TESTS[1]).unlink()
        with self.assertRaises(ValueError):
            worker.run_workcell(self.root, execute=self.ok)


if __name__ == "__main__":
    unittest.main()
