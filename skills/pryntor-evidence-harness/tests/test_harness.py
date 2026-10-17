import tempfile
import unittest
from pathlib import Path
from harness import evaluate, execute, load_contract, route_diagnostic, snapshot

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = load_contract(ROOT / 'contract.json')


class PolicyTests(unittest.TestCase):
    def test_deliberate_description_gap_holds(self):
        project = ROOT / 'fixture'
        report = evaluate(CONTRACT, execute(project, CONTRACT, 'ALL DONE'), snapshot(project))
        self.assertEqual(report['decision'], 'hold')
        self.assertEqual(report['requirements']['R1_title_search']['status'], 'passed')
        self.assertEqual(report['requirements']['R2_description_search']['status'], 'failed')
        self.assertFalse(report['release_authorized'])

    def test_missing_check_holds(self):
        project = ROOT / 'fixture'
        proof = execute(project, CONTRACT)
        proof['checks'].pop('C2_description')
        self.assertEqual(evaluate(CONTRACT, proof, snapshot(project))['decision'], 'hold')

    def test_stale_check_holds(self):
        project = ROOT / 'fixture'
        proof = execute(project, CONTRACT)
        for c in proof['checks'].values():
            c['snapshot_before'] = 'outdated'
        self.assertEqual(evaluate(CONTRACT, proof, snapshot(project))['decision'], 'hold')

    def test_runner_error_is_not_success(self):
        project = ROOT / 'fixture'
        proof = execute(project, CONTRACT)
        proof['checks']['C2_description']['exit_code'] = None
        proof['checks']['C2_description']['runner_state'] = 'runner_error'
        self.assertEqual(evaluate(CONTRACT, proof, snapshot(project))['requirements']['R2_description_search']['status'], 'unverified')

    def test_changed_command_is_unverified(self):
        project = ROOT / 'fixture'
        proof = execute(project, CONTRACT)
        proof['checks']['C1_title']['command'] = ['true']
        self.assertEqual(evaluate(CONTRACT, proof, snapshot(project))['requirements']['R1_title_search']['status'], 'unverified')

    def test_valid_fixed_project_completes_contract_not_release(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            for f in (ROOT / 'fixture').iterdir():
                if f.is_file():
                    (project / f.name).write_bytes(f.read_bytes())
            source = project / 'search.py'
            source.write_text(source.read_text().replace("fields = ['title']", "fields = ['title', 'description']"))
            proof = execute(project, CONTRACT, 'DONE')
            verdict = evaluate(CONTRACT, proof, snapshot(project))
            self.assertEqual(verdict['decision'], 'contract_satisfied')
            self.assertFalse(verdict['release_authorized'])

    def test_valid_choice_only_suggests_never_executes(self):
        response = {'type': 'choice', 'choice': 'D2', 'confidence': .8,
                    'probabilities': {'D1': .1, 'D2': .9}}
        self.assertEqual(route_diagnostic(response, {'D1', 'D2'})['action'], 'suggest_registered_check')

    def test_missing_judge_stops(self):
        self.assertEqual(route_diagnostic(None, {'D1'})['action'], 'stop_for_review')

    def test_low_confidence_stops(self):
        response = {'type': 'choice', 'choice': 'D2', 'confidence': .52,
                    'probabilities': {'D2': .68, 'D1': .32}}
        self.assertEqual(route_diagnostic(response, {'D1', 'D2'})['reason'], 'low_confidence')

    def test_unregistered_check_stops(self):
        response = {'type': 'choice', 'choice': 'DROP_TABLES', 'confidence': 1,
                    'probabilities': {'DROP_TABLES': 1}}
        self.assertEqual(route_diagnostic(response, {'D1', 'D2'})['reason'], 'unregistered_diagnostic')

    def test_invalid_probability_stops(self):
        response = {'type': 'choice', 'choice': 'D1', 'confidence': .9,
                    'probabilities': {'D1': .9, 'D2': .9}}
        self.assertEqual(route_diagnostic(response, {'D1', 'D2'})['reason'], 'judge_invalid_distribution')

    def test_empty_project_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                snapshot(Path(tmp))

    def test_unknown_check_contract_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'c.json'
            path.write_text('{"schema":"pryntor-evidence-v1","checks":{"C1":{"command":["true"]}},"requirements":{"R1":["bogus"]}}')
            with self.assertRaises(ValueError):
                load_contract(path)


if __name__ == '__main__':
    unittest.main()