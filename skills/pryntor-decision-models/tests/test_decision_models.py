import io
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from decision_models import CASES, ENDPOINT, GuardrailError, make_request, prepare_case, send_live


class Response(io.BytesIO):
    status = 200
    def __enter__(self): return self
    def __exit__(self, *args): self.close()


class SafePilotTests(unittest.TestCase):
    def test_eight_synthetic_cases(self):
        self.assertEqual(len(CASES), 8)
        for label, state in CASES:
            self.assertTrue(state.startswith("SYNTHETIC:"))
            self.assertEqual(len(prepare_case(label, state)["questions"]), 1)

    def test_no_vision_in_r0(self):
        with self.assertRaises(GuardrailError):
            prepare_case("billing", "SYNTHETIC", "s1-vision")

    def test_live_opt_in_required(self):
        with self.assertRaises(GuardrailError):
            send_live(prepare_case(*CASES[0]), key="fake_test_key_123", live_flag=False)

    def test_no_network_without_env(self):
        called = []
        def should_never_call(*a, **k):
            called.append(True)
            raise AssertionError("Network reached")
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(GuardrailError):
                send_live(prepare_case(*CASES[0]), key="fake_test_key_123",
                          live_flag=True, opener=should_never_call)
        self.assertFalse(called)

    def test_no_key(self):
        with patch.dict(os.environ, {"PRYNTOR_DM_LIVE": "1"}):
            with self.assertRaises(GuardrailError):
                send_live(prepare_case(*CASES[0]), key=None, live_flag=True)

    def test_fixed_eu_header_and_endpoint(self):
        captured = []
        def stub(req, timeout):
            captured.append((req, timeout))
            return Response(b'{"answers":{"route":{"choice":"billing"}}}')
        with patch.dict(os.environ, {"PRYNTOR_DM_LIVE": "1"}):
            r = send_live(prepare_case(*CASES[0]), key="fake_test_key_123",
                          live_flag=True, opener=stub)
        self.assertEqual(r["answers"]["route"]["choice"], "billing")
        self.assertEqual(captured[0][0].get_header("S1-region"), "eu")
        self.assertEqual(captured[0][0].full_url, ENDPOINT)
        self.assertEqual(captured[0][1], 20)
        self.assertEqual(len(captured), 1)

    def test_reject_empty_state(self):
        with self.assertRaises(GuardrailError):
            prepare_case("billing", "")

    def test_reject_long_state(self):
        with self.assertRaises(GuardrailError):
            prepare_case("billing", "x" * 10001)

    def test_reject_multiple_fast_questions(self):
        one = prepare_case(*CASES[0])["questions"]["route"]
        with self.assertRaises(GuardrailError):
            make_request("s1-fast", "SYNTHETIC", {"one": one, "two": one})

    def test_reject_unapproved_ground_truth(self):
        with self.assertRaises(GuardrailError):
            prepare_case("approve_payment", "SYNTHETIC")


if __name__ == "__main__":
    unittest.main()
