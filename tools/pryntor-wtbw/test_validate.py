"""These are SYNTHETIC structural tests, not real model/product evaluations."""
import copy
import importlib.util
from pathlib import Path
import unittest

sp=importlib.util.spec_from_file_location("validator", Path(__file__).with_name("validate.py"))
v=importlib.util.module_from_spec(sp)
sp.loader.exec_module(v)
def packet():
    f="a"*64
    def row(role,name,s):
        return {"role":role,"name":name,"scores":{"correctness":s,"experience":s},
          "source":{"url":"https://example.org/"+name,"checked_at":"2026-10-20","mechanism":"synthetic comparator only","rights_note":"fabricated synthetic test"},
          "receipt":{"artifact_sha256":"b"*64,"fixture_sha256":f,"run_id":"synthetic-fixture-only","evidence_url":"https://example.org/test/"+name}}
    return {"schema":"WTBW-1.0","issue":"PRY-309","owner":"Example owner","user_job":"Original complete working flow","failure":"Synthetic baseline failure",
      "advantage":"Increase original utility","do_not_copy":"No licensed third-party expression",
      "artifact":{"repository":"fiction/repo","base_sha":"c"*40},
      "protocol":{"fixture_sha256":f,"preregistered_at":"2026-10-20","method":"synthetic test","blinded":True,"kind":"objective","sample_count":30,"judges":1,"minimum_margin":2,"weights":{"correctness":60,"experience":40}},
      "gates":dict.fromkeys(("rights","privacy","safety","originality","source_fidelity","zero_new_spend"),"pass") | {"human_release_approval":"pending","production_deployed":False},
      "review":{"builder":"B","verifier":"V","evidence_url":"https://example.org/review"},
      "rollback":"Restore prior head","next_experiment":"Real independent review, currently NOT RUN",
      "entries":[row("baseline","baseline",40),row("direct","directA",71),row("direct","directB",74),row("lateral","lateral",80),row("candidate","candidate",84)]}
class TestWTBW(unittest.TestCase):
    def test_review_is_not_release(self):
        r=v.evaluate(packet());self.assertEqual(r["status"],"REVIEW_REQUIRED");self.assertFalse(r["release_authorized"])
    def test_inferior_candidate_iterates(self):
        p=packet();p["entries"][-1]["scores"]={"correctness":79,"experience":79};self.assertEqual(v.evaluate(p)["status"],"ITERATE")
    def test_changed_fixture_blocks(self):
        p=packet();p["entries"][-1]["receipt"]["fixture_sha256"]="x"*64;self.assertEqual(v.evaluate(p)["status"],"HOLD")
    def test_self_review_blocks(self):
        p=packet();p["review"]["verifier"]="B";self.assertEqual(v.evaluate(p)["status"],"HOLD")
    def test_missing_direct_blocks(self):
        p=packet();p["entries"]=p["entries"][1:];self.assertEqual(v.evaluate(p)["status"],"HOLD")
    def test_missing_lateral_blocks(self):
        p=packet();p["entries"]=p["entries"][:3]+p["entries"][4:];self.assertEqual(v.evaluate(p)["status"],"HOLD")
    def test_invalid_rights_blocks(self):
        p=packet();p["gates"]["rights"]="unknown";self.assertEqual(v.evaluate(p)["status"],"HOLD")
    def test_cost_blocks(self):
        p=packet();p["gates"]["zero_new_spend"]="pending";self.assertEqual(v.evaluate(p)["status"],"HOLD")
    def test_score_tamper_blocks(self):
        p=packet();p["protocol"]["weights"]["correctness"]=99;self.assertEqual(v.evaluate(p)["status"],"HOLD")
    def test_no_receipt_blocks(self):
        p=packet();del p["entries"][1]["receipt"]["evidence_url"];self.assertEqual(v.evaluate(p)["status"],"HOLD")
    def test_http_reference_blocks(self):
        p=packet();p["entries"][0]["source"]["url"]="http://example.org";self.assertEqual(v.evaluate(p)["status"],"HOLD")
    def test_invalid_score_blocks(self):
        p=packet();p["entries"][0]["scores"]["experience"]=101;self.assertEqual(v.evaluate(p)["status"],"HOLD")
    def test_unblinded_blocks(self):
        p=packet();p["protocol"]["blinded"]=False;self.assertEqual(v.evaluate(p)["status"],"HOLD")
    def test_editorial_panel_blocks(self):
        p=packet();p["protocol"].update(kind="editorial",sample_count=5,judges=2);self.assertEqual(v.evaluate(p)["status"],"HOLD")
    def test_editorial_panel_three(self):
        p=packet();p["protocol"].update(kind="editorial",sample_count=5,judges=3);self.assertEqual(v.evaluate(p)["status"],"REVIEW_REQUIRED")
    def test_no_deployment_claim(self):
        p=packet();p["gates"]["production_deployed"]=True;self.assertEqual(v.evaluate(p)["status"],"HOLD")
    def test_bad_packet(self):
        self.assertEqual(v.evaluate([])["status"],"HOLD")
    def test_duplicate(self):
        p=packet();p["entries"][1]["name"]="candidate";self.assertEqual(v.evaluate(p)["status"],"HOLD")
if __name__=="__main__":unittest.main()
