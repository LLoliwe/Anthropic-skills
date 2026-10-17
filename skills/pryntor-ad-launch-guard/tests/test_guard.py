import copy
import pathlib
import sys
import unittest
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/"scripts"))
from validate_manifest import validate

BASE={
 "mode":"dry_run","approval_status":"test_only","live":False,"spend_enabled":False,
 "budget":0,"tenant":"pryntor-studios","account_id":"test_PRYNTOR01",
 "objective":"traffic","campaign_name":"Synthetic ad test","adset_name":"Mock adset",
 "ads":[{"name":"Synthetic hero","publish":False,"enhancements_enabled":False,
         "approved_rights":True,"cta":"LEARN_MORE","placements":["feed","reels"],
         "media":["assets/hero.png"],
         "url":"https://example.com/?utm_source=meta&utm_medium=paid_social&utm_campaign=synthetic"}]
}

class TestGuard(unittest.TestCase):
 def base(self): return copy.deepcopy(BASE)
 def assert_reject(self, key, value, ad=False):
    d=self.base()
    if ad: d["ads"][0][key]=value
    else: d[key]=value
    self.assertTrue(validate(d),(key,value))
 def test_good_synthetic(self): self.assertEqual(validate(self.base()),[])
 def test_non_dict(self): self.assertTrue(validate([]))
 def test_no_ads(self): self.assert_reject("ads",[])
 def test_empty_ad(self): d=self.base(); d["ads"]=[{}]; self.assertTrue(validate(d))
 def test_duplicate(self): d=self.base(); d["ads"].append(copy.deepcopy(d["ads"][0])); self.assertTrue(validate(d))
 def test_51(self): d=self.base(); d["ads"]=[copy.deepcopy(d["ads"][0]) for _ in range(51)]; self.assertTrue(validate(d))
 def test_bad_account(self): self.assert_reject("account_id","act_123456")
 def test_missing_account(self): self.assert_reject("account_id",None)
 def test_bad_objective_type(self): self.assert_reject("objective",["sales"])
 def test_bad_placements_type(self): self.assert_reject("placements",[["feed"]],True)
 def test_non_string_media(self): self.assert_reject("media",[3],True)
 def test_unsafe_media(self): self.assert_reject("media",[r"assets\..\secret.png"],True)
 def test_encoded_media(self): self.assert_reject("media",["assets/%2e%2e/secret.jpg"],True)
 def test_bad_media_type(self): self.assert_reject("media",["assets/file.exe"],True)
 def test_bad_url(self): self.assert_reject("url","http://localhost",True)
 def test_url_private_ip(self): self.assert_reject("url","https://127.0.0.1/?utm_source=meta&utm_medium=p&utm_campaign=c",True)
 def test_url_credentials(self): self.assert_reject("url","https://x:y@example.com/?utm_source=meta&utm_medium=p&utm_campaign=c",True)
 def test_utm_missing(self): self.assert_reject("url","https://example.com/",True)
 def test_utm_repeat(self): self.assert_reject("url","https://example.com/?utm_source=x&utm_source=y&utm_medium=p&utm_campaign=c",True)
 def test_utm_injection(self): self.assert_reject("url","https://example.com/?utm_source=%0Asecret&utm_medium=p&utm_campaign=c",True)
 def test_unknown_budget_field(self): self.assert_reject("daily_budget",100)
 def test_unknown_active_field(self): self.assert_reject("status","ACTIVE",True)
 def test_private_payload(self): self.assert_reject("private_data",{"name":"client"})
 def test_bool_budget(self): self.assert_reject("budget",False)
 def test_nonzero_budget(self): self.assert_reject("budget",1)
 def test_live(self): self.assert_reject("live",True)
 def test_publish(self): self.assert_reject("publish",True,True)
 def test_enhancements(self): self.assert_reject("enhancements_enabled",True,True)
 def test_missing_rights(self): self.assert_reject("approved_rights",False,True)
 def test_missing_tenant(self): self.assert_reject("tenant","")
 def test_invalid_approval(self): self.assert_reject("approval_status","active")
 def test_invalid_cta(self): self.assert_reject("cta","DONATE",True)
