"""Documentation-shape regression tests; synthetic values, no TypeSafe calls.

Official raw response contract: https://docs.typesafe.ai/introduction/quickstart
The examples below are representative, NOT captured TypeSafe results.
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import decision_pilot as p


class OfficialDocumentationShapeTests(unittest.TestCase):
    def official_shaped_response(self, workflow="diagnostic"):
        choices = p.ROUTES[workflow]
        best = next(iter(choices))
        return {
            "model": "jev-1.13.0",
            "answers": {
                "route": {
                    "type": "choice",
                    "choice": best,
                    "confidence": 0.98,
                    "probabilities": {
                        key: 1.0 if key == best else 0.0 for key in choices
                    },
                }
            },
        }

    def test_raw_model_answers_shape(self):
        answer = self.official_shaped_response()
        self.assertIn("model", answer)
        self.assertIn("answers", answer)
        self.assertEqual(set(answer["answers"]["route"]), {"type", "choice", "confidence", "probabilities"})

    def test_advisory_from_official_shape(self):
        answer = self.official_shaped_response()
        self.assertEqual(p.guarded_route("diagnostic", {"missing_requirement": True}, answer)["route"], "inspect_contract")

    def test_unknown_provider_model_holds(self):
        answer = self.official_shaped_response()
        answer["model"] = "unapproved-preview"
        self.assertEqual(p.guarded_route("diagnostic", {}, answer)["route"], "human_review")

    def test_missing_answer_payload_holds(self):
        answer = self.official_shaped_response()
        answer["answers"].pop("route")
        self.assertEqual(p.guarded_route("diagnostic", {}, answer)["route"], "human_review")

    def test_unknown_provider_answer_key_ignored_not_executed(self):
        answer = self.official_shaped_response()
        answer["answers"]["publish"] = {"type": "noul", "noul": 1}
        verdict = p.guarded_route("diagnostic", {}, answer)
        self.assertFalse(verdict["action_executed"])
        self.assertFalse(verdict["release_authorized"])

    def test_non_automatic_external_communication_even_if_confident(self):
        answer = self.official_shaped_response("partnership")
        verdict = p.guarded_route("partnership", {"policy_flags": ["external_send"]}, answer)
        self.assertEqual(verdict["route"], "human_review")
        self.assertFalse(verdict["action_executed"])

    def test_raw_request_preview_uses_official_typed_choice(self):
        req = p.build_request("diagnostic", {"contract_mismatch": True})
        self.assertEqual(req["questions"]["route"]["type"], "choice")
        self.assertIn("criteria", req["questions"]["route"])
        self.assertEqual(req["model"], "jev-1.13.0")


if __name__ == "__main__":
    unittest.main()
