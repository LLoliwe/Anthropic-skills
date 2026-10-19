"""Evidence regressions: reject incomplete, erroneous, or mismatched upstream results."""
import importlib.util
import json
from pathlib import Path
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'earshot_live_acceptance.py'
spec = importlib.util.spec_from_file_location('earshot_acceptance', SCRIPT)
acceptance = importlib.util.module_from_spec(spec)
spec.loader.exec_module(acceptance)


class EarshotEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.measure = {'duration': 1.0, 'lufs': -21.2, 'true_peak_dbtp': -7.4, 'clipped_samples': 0}
        self.doctor = {'problems': [], 'clap_load_s': 10.6, 'ast_load_s': 3.0,
                       'clap_one_window_s': 0.91, 'ast_one_window_s': 1.11}
        self.review = {'metrics': [{'metric': 'lufs_i', 'status': 'low'}],
                       'partial': [], 'score': 0.345, 'verdict': 'not launch-grade'}

    def measurement(self, data):
        return acceptance.validate_measurement('Exact meter readings\n\nJSON (compact): ' + json.dumps(data))

    def test_known_fixture_has_real_meter_values(self):
        self.assertEqual(self.measurement(self.measure)['duration'], 1.0)

    def test_textual_tool_error_cannot_pass(self):
        with self.assertRaises(AssertionError):
            acceptance.validate_measurement('Error executing tool measure: path required')

    def test_missing_nonfinite_and_boolean_metrics_rejected(self):
        for value in (None, float('nan'), float('inf'), True, '-21.2'):
            with self.subTest(value=value), self.assertRaises(AssertionError):
                self.measurement({**self.measure, 'lufs': value})

    def test_wrong_fixture_duration_and_clipping_rejected(self):
        for change in ({'duration': 4.0}, {'clipped_samples': 1}):
            with self.subTest(change=change), self.assertRaises(AssertionError):
                self.measurement({**self.measure, **change})

    def test_real_bad_quality_verdict_is_valid_evidence_not_release_approval(self):
        acceptance.validate_critique(self.doctor, self.review)
        self.assertEqual(self.review['verdict'], 'not launch-grade')

    def test_missing_or_failed_model_inference_rejected(self):
        for change in ({'problems': ['AST unavailable']}, {'ast_one_window_s': None},
                       {'clap_load_s': 0}, {'ast_load_s': float('inf')}):
            with self.subTest(change=change), self.assertRaises(AssertionError):
                acceptance.validate_critique({**self.doctor, **change}, self.review)

    def test_partial_empty_and_invalid_critique_rejected(self):
        for change in ({'partial': ['realness']}, {'metrics': []}, {'verdict': 'success'},
                       {'score': float('nan')}, {'score': True}):
            with self.subTest(change=change), self.assertRaises(AssertionError):
                acceptance.validate_critique(self.doctor, {**self.review, **change})


if __name__ == '__main__':
    unittest.main()
