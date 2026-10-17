import io
import json
import unittest
from urllib.error import HTTPError
from unittest.mock import patch
import github_oss_radar as m


class FakeResponse:
    def __init__(self, data, url): self.data, self.url = data, url
    def __enter__(self): return self
    def __exit__(self, *_): return False
    def geturl(self): return self.url
    def read(self, amount): return self.data[:amount]


class PublicRepoTests(unittest.TestCase):
    def setUp(self):
        self.repo = "PyLabRobot/pylabrobot"
        self.url = m.API + self.repo
        self.obj = {"full_name": self.repo, "description":"A lab robot library", "default_branch":"main", "pushed_at":"2026-10-16T00:00:00Z", "updated_at":"2026-10-17T00:00:00Z", "archived":False, "license":{"spdx_id":"MIT"}}
    def fake_open(self, req, timeout):
        self.assertEqual(req.full_url, self.url)
        self.assertEqual(req.get_method(), "GET")
        self.assertEqual(timeout, 12)
        self.assertNotIn("Authorization", req.headers)
        return FakeResponse(json.dumps(self.obj).encode(), self.url)
    def test_verified_metadata(self):
        result=m.fetch_one(self.repo, opener=self.fake_open)
        self.assertEqual(result["github_license_spdx"],"MIT")
        self.assertFalse(result["license_certified"])
        self.assertEqual(result["url"], "https://github.com/"+self.repo)
    def test_allowlist_blocks_arbitrary_host_and_repo(self):
        for repo in ("other/repo", "../secret", "https://evil.example.org/x", "user/repo?x=1"):
            with self.assertRaises(ValueError): m.fetch_one(repo)
    def test_redirect_rejected(self):
        with self.assertRaises(m.RepoFetchError):
            m.fetch_one(self.repo, opener=lambda *a, **k: FakeResponse(json.dumps(self.obj).encode(), "https://evil.example.org"))
    def test_identity_mismatch_rejected(self):
        obj=dict(self.obj,full_name="Other/Else")
        with self.assertRaises(m.RepoFetchError):
            m.fetch_one(self.repo, opener=lambda *a,**k:FakeResponse(json.dumps(obj).encode(),self.url))
    def test_failure_safe_on_bad_json(self):
        with self.assertRaises(m.RepoFetchError): m.fetch_one(self.repo, opener=lambda *a,**k:FakeResponse(b"oops",self.url))
    def test_rate_limit_error_safe(self):
        def deny(*a,**k): raise HTTPError(self.url,403,"limit",{},None)
        with self.assertRaises(m.RepoFetchError): m.fetch_one(self.repo, opener=deny)
    def test_allows_token_only_when_supplied(self):
        def token_test(req,timeout):
            self.assertTrue(req.headers["Authorization"].startswith("Bearer "))
            return FakeResponse(json.dumps(self.obj).encode(),self.url)
        result=m.fetch_one(self.repo,opener=token_test,token="placeholder-token")
        self.assertEqual(result["repository"],self.repo)
    def test_collect_reports_errors_without_leaking_request_data(self):
        def opener(req,timeout):
            if req.full_url == self.url: return FakeResponse(json.dumps(self.obj).encode(),self.url)
            raise HTTPError(req.full_url,404,"Not found",{},None)
        report=m.collect(opener=opener,max_repos=2)
        self.assertEqual((report["count"], report["failed"]),(1,1))
        self.assertNotIn("Token",json.dumps(report))
    def test_bad_max_repos(self):
        with self.assertRaises(ValueError): m.collect(max_repos=99)
    def test_no_forum_domain(self):
        self.assertNotIn("labautomation.io",str(m.REPOS))

if __name__ == "__main__": unittest.main()
