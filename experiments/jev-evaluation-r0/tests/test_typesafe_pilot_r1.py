"""Adversarial, stdlib-only tests for skill-guided synthetic Jev pilot R1."""
import inspect
import json
import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import typesafe_pilot_r1 as r1


class PartnershipsSkillPilotTests(unittest.TestCase):
    def setUp(self):
        self.valid = r1.mock_response("research", 0.98, 0.97)

    def test_official_choice_and_independent_nouls(self):
        req = r1.preview_request("partner-free-claims")
        self.assertEqual(req["model"], "jev-1.13.0")
        self.assertTrue(req["state"]["synthetic_only"])
        self.assertEqual(req["questions"]["next_queue"]["type"], "choice")
        self.assertEqual(req["questions"]["claims_no_card"]["type"], "noul")
        self.assertEqual(req["questions"]["claims_no_auto_conversion"]["type"], "noul")

    def test_request_only_contains_fictional_evidence(self):
        req = r1.preview_request("partner-unclear")
        self.assertIn("Fictional", req["state"]["evidence_excerpt"])
        self.assertNotIn("api_key", json.dumps(req).lower())

    def test_validated_research_stays_internal(self):
        result = r1.review_response("partner-free-claims", self.valid)
        self.assertEqual(result["queue"], "research")
        self.assertEqual(result["status"], "INTERNAL_REVIEW_ONLY")
        self.assertFalse(result["action_executed"])
        self.assertFalse(result["release_authorized"])
        self.assertFalse(result["terms_verified"])

    def test_claim_nouls_are_not_terms_verification(self):
        result = r1.review_response("partner-free-claims", self.valid)
        self.assertEqual(result["claims"]["no_card"], .98)
        self.assertFalse(result["terms_verified"])

    def test_high_confidence_pilot_does_not_grant_contract(self):
        response = r1.mock_response("pilot_review", 1, 1)
        result = r1.review_response("partner-free-claims", response)
        self.assertEqual(result["status"], "HOLD")
        self.assertEqual(result["reason"], "missing_independently_verified_contract")

    def test_fictional_written_approval_still_cannot_execute(self):
        result = r1.review_response("partner-written-approval", r1.mock_response("pilot_review", 1, 1))
        self.assertEqual(result["queue"], "pilot_review")
        self.assertFalse(result["action_executed"])
        self.assertFalse(result["release_authorized"])

    def test_fictional_approval_is_never_real_terms_verification(self):
        verdict = r1.review_response("partner-written-approval", r1.mock_response("pilot_review", .99, .99))
        self.assertTrue(verdict["fixture_policy_checks_passed"])
        self.assertFalse(verdict["terms_verified"])
        self.assertFalse(verdict["live_jev_invoked"])

    def test_no_mock_can_claim_live_model_invocation(self):
        for case in r1.CASES:
            verdict = r1.review_response(case, r1.mock_response("research", .99, .99))
            self.assertFalse(verdict["live_jev_invoked"])

    def test_payment_or_autobilling_skips_inference(self):
        self.assertFalse(r1.can_model_review("partner-freemium"))
        with self.assertRaises(ValueError):
            r1.preview_request("partner-freemium")

    def test_customer_data_flag_skips_inference(self):
        self.assertFalse(r1.can_model_review("partner-risk"))
        self.assertEqual(r1.review_response("partner-risk", self.valid)["status"], "HOLD")

    def test_unverified_identity_skips_inference(self):
        self.assertFalse(r1.can_model_review("partner-source-unknown"))

    def test_unknown_case_denied(self):
        with self.assertRaises(ValueError):
            r1.preview_request("real-customer-record")

    def test_unknown_provider_model_held(self):
        bad = r1.mock_response("research", 1, 1)
        bad["model"] = "jev-latest"
        self.assertEqual(r1.review_response("partner-free-claims", bad)["queue"], "human_review")

    def test_missing_one_noul_held(self):
        bad = r1.mock_response("research", 1, 1)
        del bad["answers"]["claims_no_card"]
        self.assertEqual(r1.review_response("partner-free-claims", bad)["reason"], "missing_or_unexpected_answers")

    def test_extra_provider_answer_held(self):
        bad = r1.mock_response("research", 1, 1)
        bad["answers"]["approve_payment"] = {"type": "noul", "noul": 1}
        self.assertEqual(r1.review_response("partner-free-claims", bad)["status"], "HOLD")

    def test_invalid_noul_values_held(self):
        for value in (float("nan"), math.inf, -0.001, 1.001, True, "1", None):
            with self.subTest(value=value):
                bad = r1.mock_response("research", .9, .9)
                bad["answers"]["claims_no_card"]["noul"] = value
                self.assertEqual(r1.review_response("partner-free-claims", bad)["reason"], "invalid_noul")

    def test_noul_with_confidence_field_held(self):
        bad = r1.mock_response("research", .95, .95)
        bad["answers"]["claims_no_card"]["confidence"] = .99
        self.assertEqual(r1.review_response("partner-free-claims", bad)["status"], "HOLD")

    def test_bad_choice_cannot_bypass_noul_checks(self):
        bad = r1.mock_response("research", 1, 1)
        bad["answers"]["next_queue"]["choice"] = "send_email"
        self.assertEqual(r1.review_response("partner-free-claims", bad)["status"], "HOLD")

    def test_not_a_network_enabled_client(self):
        source = inspect.getsource(r1)
        self.assertNotIn("urllib.request", source)
        self.assertNotIn("requests.post", source)
        self.assertNotIn("client.system_one(", source)
        self.assertNotIn("TYPESAFE_API_KEY", source)

    def test_every_mock_scenario_is_nonexecuting(self):
        for case_id in r1.CASES:
            for route in r1.policy.ROUTES["partnership"]:
                with self.subTest(case=case_id, route=route):
                    result = r1.review_response(case_id, r1.mock_response(route, .95, .95))
                    self.assertFalse(result["action_executed"])
                    self.assertFalse(result["release_authorized"])

    def test_missing_response_is_hold(self):
        self.assertEqual(r1.review_response("partner-free-claims", None)["status"], "HOLD")


if __name__ == "__main__":
    unittest.main()
