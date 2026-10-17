"""V2 regression and adversarial tests. Synthetic only, no keys or network."""
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

from harness import (CONTRACT_SCHEMA, RECORD_SCHEMA, contract_digest, evaluate, execute,
                     exclusive_write, load_contract, record_digest, render_html,
                     route_diagnostic, snapshot)

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = load_contract(ROOT / 'contract.json')


def single(command, seconds=2):
    return {'schema': CONTRACT_SCHEMA,
            'checks': {'C1': {'command': command, 'timeout_seconds': seconds}},
            'requirements': {'R1': ['C1']}}


class SentinelV2Tests(unittest.TestCase):
    def test_provenance_checksum_present_and_replay_verifies(self):
        proof = execute(ROOT / 'fixture', CONTRACT, 'DONE')
        self.assertEqual(proof['schema'], RECORD_SCHEMA)
        self.assertEqual(proof['record_digest'], record_digest(proof))
        proof['worker_claim_untrusted'] = 'CHANGED'
        verdict = evaluate(CONTRACT, proof, snapshot(ROOT / 'fixture'))
        self.assertEqual(verdict['reason'], 'record_corrupt_or_modified')

    def test_recomputed_digest_is_not_release_authorization(self):
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp)
            (project / 'source.txt').write_text('safe')
            contract = single(['python3', '-c', 'pass'])
            proof = execute(project, contract)
            proof['worker_claim_untrusted'] = 'edited'
            proof['record_digest'] = record_digest(proof)
            result = evaluate(contract, proof, snapshot(project))
            self.assertEqual(result['decision'], 'contract_satisfied')
            self.assertFalse(result['release_authorized'])
            # Shows why a plain digest is NOT a signature or genuine provenance attestation.

    def test_recomputed_missing_check_still_holds(self):
        proof = execute(ROOT / 'fixture', CONTRACT)
        del proof['checks']['C2_description']
        proof['record_digest'] = record_digest(proof)
        self.assertEqual(evaluate(CONTRACT, proof, snapshot(ROOT / 'fixture'))['reason'], 'missing_or_extra_checks')

    def test_symlinked_directory_refused_instead_of_skipped(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / 'source.txt').write_text('code')
            (root / 'node_modules').symlink_to('/tmp', target_is_directory=True)
            with self.assertRaisesRegex(ValueError, 'Symlink directory'):
                snapshot(root)

    def test_mutated_project_detected_in_same_run(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / 'source.txt').write_text('original')
            c = single(['python3', '-c', "open('source.txt','w').write('changed')"])
            proof = execute(root, c)
            self.assertEqual(evaluate(c, proof, snapshot(root))['decision'], 'hold')

    def test_stdout_default_omits_secrets_and_records_hash(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / 'source.txt').write_text('safe')
            c = single(['python3', '-c', 'print("Authorization: secretvalue987654321")'])
            proof = execute(root, c)
            check = proof['checks']['C1']
            self.assertEqual(check['stdout_tail'], '')
            self.assertEqual(check['stdout_bytes'], len('Authorization: secretvalue987654321\n'))
            self.assertEqual(len(check['stdout_sha256']), 64)
            self.assertEqual(evaluate(c, proof, snapshot(root))['decision'], 'contract_satisfied')

    def test_opt_in_log_redaction(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / 'source.txt').write_text('safe')
            c = single(['python3', '-c', 'print("Authorization: secretvalue987654321")'])
            proof = execute(root, c, include_output=True)
            self.assertIn('[REDACTED]', proof['checks']['C1']['stdout_tail'])
            self.assertNotIn('secretvalue987654321', proof['checks']['C1']['stdout_tail'])

    def test_exposed_api_keys_removed_in_check_env(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / 'source.txt').write_text('safe')
            c = single(['python3', '-c',
                        "import os,sys;sys.exit(0 if 'TYPESAFE_API_KEY' not in os.environ else 1)"])
            with patch.dict(os.environ, {'TYPESAFE_API_KEY': 'private'}):
                proof = execute(root, c)
            self.assertEqual(evaluate(c, proof, snapshot(root))['decision'], 'contract_satisfied')

    def test_child_process_terminated_after_parent_timeout(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / 'source.txt').write_text('safe')
            child = "import time;time.sleep(1);open('late.txt','w').write('escaped')"
            worker = 'import subprocess,time;subprocess.Popen(["python3","-c",' + repr(child) + ']);time.sleep(5)'
            c = single(['python3', '-c', worker], seconds=.25)
            proof = execute(root, c)
            self.assertEqual(proof['checks']['C1']['runner_state'], 'timeout')
            time.sleep(1.1)
            self.assertFalse((root / 'late.txt').exists(), 'orphaned child mutated project')
            self.assertEqual(evaluate(c, proof, snapshot(root))['decision'], 'hold')

    def test_low_pmax_blocks_overconfident_judge(self):
        x = {'type':'choice','choice':'D1','confidence':.99,
             'probabilities':{'D1':.51,'D2':.49}}
        self.assertEqual(route_diagnostic(x, {'D1','D2'})['reason'], 'low_confidence_or_weak_winner')

    def test_disallow_unknown_probability_options(self):
        x = {'type':'choice','choice':'D1','confidence':.99,
             'probabilities':{'D1':.92,'SHELL_CMD':.08}}
        self.assertEqual(route_diagnostic(x, {'D1'})['reason'], 'judge_invalid_distribution')

    def test_html_is_static_and_escapes_untrusted_text(self):
        proof = execute(ROOT / 'fixture', CONTRACT, '<img src=x onerror=alert(1)>')
        html = render_html(proof, evaluate(CONTRACT, proof, snapshot(ROOT / 'fixture')))
        self.assertNotIn('<img src=x', html)
        self.assertIn('&lt;img src=x', html)
        self.assertIn("default-src 'none'", html)
        self.assertIn('RELEASE AUTHORIZED: NO', html)

    def test_exclusive_evidence_permissions_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as temp:
            p = Path(temp) / 'record.json'
            exclusive_write(p, '{}')
            self.assertEqual(stat.S_IMODE(p.stat().st_mode), 0o600)
            with self.assertRaises(FileExistsError):
                exclusive_write(p, '{"fake": true}')

    def test_contract_rejects_nan_timeout(self):
        with tempfile.TemporaryDirectory() as temp:
            p = Path(temp) / 'contract.json'
            c = single(['true'], seconds=float('nan'))
            p.write_text(json.dumps(c, allow_nan=True))
            with self.assertRaisesRegex(ValueError, 'timeout'):
                load_contract(p)

    def test_cli_deny_without_pinned_contract_digest(self):
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp) / 'record.json'
            result = subprocess.run([sys.executable, str(ROOT/'harness.py'), 'run',
                                     '--project', str(ROOT/'fixture'), '--contract', str(ROOT/'contract.json'),
                                     '--evidence', str(out)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            self.assertFalse(out.exists())
            self.assertIn('not reviewed', result.stderr)

    def test_cli_generates_replayable_record_and_html(self):
        with tempfile.TemporaryDirectory() as temp:
            out, page = Path(temp)/'record.json', Path(temp)/'audit.html'
            args=[sys.executable, str(ROOT/'harness.py'), 'run', '--project', str(ROOT/'fixture'),
                  '--contract', str(ROOT/'contract.json'), '--evidence', str(out), '--html', str(page),
                  '--approved-contract-sha256', contract_digest(CONTRACT), '--claim','WORKER CLAIMS DONE']
            r = subprocess.run(args, capture_output=True, text=True)
            self.assertEqual(r.returncode, 2)  # deliberate R2 failure
            self.assertTrue(out.exists())
            self.assertTrue(page.exists())
            self.assertIn('HOLD: UNVERIFIED', page.read_text())
            replay = subprocess.run([sys.executable, str(ROOT/'harness.py'), 'replay',
                '--project', str(ROOT/'fixture'), '--contract', str(ROOT/'contract.json'),
                '--evidence', str(out), '--approved-contract-sha256', contract_digest(CONTRACT)],
                capture_output=True, text=True)
            self.assertEqual(replay.returncode, 2)
            self.assertIn('R2_description_search', replay.stdout)


if __name__ == '__main__':
    unittest.main()