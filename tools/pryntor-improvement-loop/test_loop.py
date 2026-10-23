"""Offline tests, including adversarial verifier tampering."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

CONTROLLER = Path(__file__).with_name('loop.py')


class TestLoop(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.root = self.base / 'source'
        self.root.mkdir()
        (self.root / 'value.txt').write_text('bad')
        (self.root / 'verify.py').write_text("from pathlib import Path\nimport sys\nsys.exit(0 if Path('value.txt').read_text() == 'good' else 1)\n")

    def call(self, candidate, execute=True, count=3):
        spec = self.base / 'spec.json'
        spec.write_text(json.dumps({'goal': 'Fix acceptance fixture', 'candidate_argv':
                                    [sys.executable, '-c', candidate], 'verify_argv':
                                    [sys.executable, 'verify.py'], 'protected_files': ['verify.py'],
                                    'max_attempts': count, 'timeout_seconds': 3}))
        args = [sys.executable, str(CONTROLLER), '--spec', str(spec), '--root', str(self.root),
                '--out', str(self.base / 'result')]
        if execute:
            args.append('--execute')
        return subprocess.run(args, capture_output=True, text=True)

    def test_succeeds_with_patch_and_unmodified_original(self):
        r = self.call("from pathlib import Path; Path('value.txt').write_text('good')")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(json.loads(r.stdout)['status'], 'CANDIDATE_VERIFIED_REVIEW_REQUIRED')
        self.assertEqual((self.root / 'value.txt').read_text(), 'bad')
        self.assertIn('+good', (self.base / 'result' / 'candidate.patch').read_text())

    def test_protects_verifier(self):
        r = self.call("from pathlib import Path; Path('verify.py').write_text('pass')")
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertEqual(json.loads(r.stdout)['status'], 'BLOCKED_VERIFIER_MODIFIED')
        self.assertFalse((self.base / 'result' / 'candidate.patch').exists())

    def test_stops_on_no_progress(self):
        r = self.call('pass', count=5)
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertEqual(json.loads(r.stdout)['status'], 'STOPPED_NO_PROGRESS')
        self.assertEqual(sum(1 for line in (self.base / 'result' / 'events.jsonl').read_text().splitlines()
                             if json.loads(line)['event'] == 'attempt'), 2)

    def test_dry_run_is_default(self):
        r = self.call('pass', execute=False)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(json.loads(r.stdout)['status'], 'DRY_RUN')
        self.assertFalse((self.base / 'result').exists())

    def test_already_passing(self):
        (self.root / 'value.txt').write_text('good')
        r = self.call("raise RuntimeError('must not run')")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(json.loads(r.stdout)['status'], 'ALREADY_PASSING')

    def test_disallows_untrusted_shell_form(self):
        spec = self.base / 'bad.json'
        spec.write_text(json.dumps({'goal': 'bad', 'candidate_argv': 'echo wrong',
                                    'verify_argv': ['python3', 'verify.py'], 'protected_files': ['verify.py']}))
        r = subprocess.run([sys.executable, str(CONTROLLER), '--spec', str(spec),
                            '--root', str(self.root), '--out', str(self.base / 'result'), '--execute'],
                           capture_output=True)
        self.assertNotEqual(r.returncode, 0)

    def test_forbids_symlink_in_staged_workspace(self):
        (self.root / 'escape').symlink_to(self.base / 'spec.json')
        r = self.call('pass')
        self.assertNotEqual(r.returncode, 0)


    def test_verifier_side_effect_cannot_fake_success(self):
        # Baseline verifier intentionally rewrites data. Its changes must never reach candidate.
        (self.root / 'verify.py').write_text(
            "from pathlib import Path\nimport sys\n"
            "value = Path('value.txt')\n"
            "if value.read_text() != 'good':\n"
            "    value.write_text('good')\n"
            "    sys.exit(1)\n"
            "sys.exit(0)\n"
        )
        r = self.call('pass')
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertEqual(json.loads(r.stdout)['status'], 'STOPPED_NO_PROGRESS')
        self.assertEqual((self.root / 'value.txt').read_text(), 'bad')
        self.assertFalse((self.base / 'result' / 'candidate.patch').exists())

    def test_verifier_tampering_on_passing_attempt_blocks(self):
        (self.root / 'verify.py').write_text(
            "from pathlib import Path\nimport sys\n"
            "if Path('value.txt').read_text() == 'good':\n"
            "    Path('verify.py').write_text('pass')\n"
            "    sys.exit(0)\n"
            "sys.exit(1)\n"
        )
        r = self.call("from pathlib import Path; Path('value.txt').write_text('good')")
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertEqual(json.loads(r.stdout)['status'], 'BLOCKED_VERIFIER_MODIFIED')
        self.assertFalse((self.base / 'result' / 'candidate.patch').exists())

    def test_unavailable_baseline_does_not_run_candidate(self):
        (self.root / 'verify.py').write_text("import time\ntime.sleep(10)\n")
        r = self.call("from pathlib import Path; Path('value.txt').write_text('good')")
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertEqual(json.loads(r.stdout)['status'], 'BLOCKED_BASELINE_UNAVAILABLE')
        self.assertEqual((self.root / 'value.txt').read_text(), 'bad')
        self.assertFalse((self.base / 'result' / 'candidate.patch').exists())



if __name__ == '__main__':
    unittest.main()