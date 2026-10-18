import json
import math
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import decision_pilot as p


class AdversarialDecisionTests(unittest.TestCase):
    def setUp(self):
        self.sample = {"source_failure": True}
        self.options = p.ROUTES["diagnostic"]

    def response(self, chosen="inspect_source", prob=.96, conf=.96, model="jev-1.13.0"):
        other = (1-prob)/(len(self.options)-1)
        return {"model": model, "answers": {"route": {"type": "choice", "choice": chosen,
            "confidence": conf, "probabilities": {k: prob if k == chosen else other for k in self.options}}}}

    def test_valid_advisory(self):
        self.assertEqual(p.guarded_route("diagnostic", self.sample, self.response())["route"], "inspect_source")

    def test_never_authorizes_release(self):
        self.assertFalse(p.guarded_route("diagnostic", self.sample, self.response())["release_authorized"])

    def test_never_executes_action(self):
        self.assertFalse(p.guarded_route("diagnostic", self.sample, self.response())["action_executed"])

    def test_invalid_route(self):
        r = self.response()
        r["answers"]["route"]["choice"] = "deploy_prod"
        self.assertEqual(p.guarded_route("diagnostic", self.sample, r)["route"], "human_review")

    def test_wrong_model(self):
        self.assertEqual(p.guarded_route("diagnostic", self.sample, self.response(model="jev-latest"))["route"], "human_review")

    def test_wrong_type(self):
        r = self.response()
        r["answers"]["route"]["type"] = "score"
        self.assertEqual(p.guarded_route("diagnostic", self.sample, r)["route"], "human_review")

    def test_missing_question(self):
        self.assertEqual(p.guarded_route("diagnostic", self.sample, {"model": "jev-1.13.0", "answers": {}})["route"], "human_review")

    def test_missing_probabilities(self):
        r = self.response()
        r["answers"]["route"].pop("probabilities")
        self.assertEqual(p.guarded_route("diagnostic", self.sample, r)["route"], "human_review")

    def test_nonfinite_probability(self):
        r = self.response()
        r["answers"]["route"]["probabilities"]["inspect_source"] = float("nan")
        self.assertEqual(p.guarded_route("diagnostic", self.sample, r)["route"], "human_review")

    def test_inf_confidence(self):
        self.assertEqual(p.guarded_route("diagnostic", self.sample, self.response(conf=math.inf))["route"], "human_review")

    def test_booleans_not_confidences(self):
        self.assertEqual(p.guarded_route("diagnostic", self.sample, self.response(conf=True))["route"], "human_review")

    def test_oversummed_probability(self):
        r = self.response()
        r["answers"]["route"]["probabilities"]["inspect_runner"] = 0.3
        self.assertEqual(p.guarded_route("diagnostic", self.sample, r)["route"], "human_review")

    def test_low_confidence(self):
        self.assertEqual(p.guarded_route("diagnostic", self.sample, self.response(conf=.3))["route"], "human_review")

    def test_low_winner(self):
        self.assertEqual(p.guarded_route("diagnostic", self.sample, self.response(prob=.75))["route"], "human_review")

    def test_mismatched_winner(self):
        r = self.response()
        r["answers"]["route"]["choice"] = "inspect_contract"
        self.assertEqual(p.guarded_route("diagnostic", self.sample, r)["route"], "human_review")

    def test_payment_override_ignored(self):
        s = {"source_failure": True, "policy_flags": ["payment"]}
        self.assertEqual(p.guarded_route("diagnostic", s, self.response())["route"], "human_review")

    def test_external_send_override_ignored(self):
        s = {"source_failure": True, "policy_flags": ["external_send"]}
        self.assertEqual(p.guarded_route("diagnostic", s, self.response())["route"], "human_review")

    def test_release_override_ignored(self):
        s = {"source_failure": True, "policy_flags": ["production_release"]}
        self.assertEqual(p.guarded_route("diagnostic", s, self.response())["route"], "human_review")

    def test_customer_data_override_ignored(self):
        s = {"source_failure": True, "policy_flags": ["unreviewed_customer_data"]}
        self.assertEqual(p.guarded_route("diagnostic", s, self.response())["route"], "human_review")

    def test_password_rejected(self):
        with self.assertRaises(ValueError):
            p.build_request("diagnostic", {"password": "secret"})

    def test_api_key_rejected(self):
        with self.assertRaises(ValueError):
            p.build_request("diagnostic", {"api_key": "test"})

    def test_default_latest_model_rejected(self):
        with self.assertRaises(ValueError):
            p.build_request("diagnostic", self.sample, "jev-latest")

    def test_hard_held_request_never_exported(self):
        with self.assertRaises(ValueError):
            p.build_request("diagnostic", {"policy_flags": ["secret_access"]})

    def test_invalid_flags_hold(self):
        self.assertEqual(p.guarded_route("diagnostic", {"policy_flags": "bad"}, self.response())["route"], "human_review")

    def test_unknown_approval_hold(self):
        self.assertEqual(p.baseline("diagnostic", {"approval_required": True})["route"], "human_review")

    def test_empty_response_holds(self):
        self.assertEqual(p.guarded_route("diagnostic", self.sample, {})["route"], "human_review")

    def test_works_in_both_pinned_versions(self):
        self.assertEqual(p.guarded_route("diagnostic", self.sample, self.response(model="jev-1.14.0"))["route"], "inspect_source")

    def test_vendor_payload_has_only_allowed_questions(self):
        q = p.build_request("diagnostic", self.sample)
        self.assertEqual(set(q["questions"]), {"route"})
        self.assertNotIn("Authorization", json.dumps(q))

    def test_report_zero_jev_calls(self):
        rows = p.cases(Path(__file__).resolve().parents[1] / "fixtures.json")
        report = p.offline_report(rows)
        self.assertEqual(report["paid_jev_calls"], 0)
        self.assertFalse(report["jev_accuracy_measured"])

    def test_all_hard_flags_hold(self):
        for flag in p.BLOCK_FLAGS:
            with self.subTest(flag=flag):
                self.assertEqual(p.baseline("partnership", {"policy_flags": [flag]})["route"], "human_review")

    def test_all_cases_match_curated_baseline(self):
        rows = p.cases(Path(__file__).resolve().parents[1] / "fixtures.json")
        self.assertEqual(len(rows), 60)
        for r in rows:
            with self.subTest(id=r["id"]):
                self.assertEqual(p.baseline(r["workflow"], r["state"])["route"], r["gold"])

    def test_no_provider_response_can_authorize(self):
        for wf in p.ROUTES:
            chosen = next(iter(p.ROUTES[wf]))
            opts = p.ROUTES[wf]
            probs = {k: 1.0 if k == chosen else 0.0 for k in opts}
            r = {"model": "jev-1.13.0", "answers": {"route": {"type": "choice", "choice": chosen,
                 "confidence": 1.0, "probabilities": probs}}}
            verdict = p.guarded_route(wf, {}, r)
            self.assertFalse(verdict["release_authorized"])

    def test_dataset_duplicate_rejected(self):
        rows = p.cases(Path(__file__).resolve().parents[1] / "fixtures.json")
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "x.json"
            path.write_text(json.dumps(rows + [rows[0]]))
            with self.assertRaises(ValueError):
                p.cases(path)


if __name__ == "__main__":
    unittest.main()
