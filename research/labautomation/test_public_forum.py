"""Offline unit tests. No external web access or credentials required."""
import io
import json
import unittest
from unittest.mock import patch

import public_forum as m

CATEGORIES = {"category_list": {"categories": [
    {"id": 12, "name": "Open-Source", "slug": "open-source"},
    {"id": 23, "name": "Robotic Arms", "slug": "robotic-arms"},
]}}
TOPICS = {"topic_list": {"topics": [
    {"id": 1, "title": "An older open-source simulator", "category_id": 12, "last_posted_at": "2025-01-01T00:00:00Z", "posts_count": 1},
    {"id": 2, "title": "Open-source robot workflow", "category_id": 23, "last_posted_at": "2026-10-17T12:00:00Z", "posts_count": 2},
    {"id": "bad", "title": "Invalid", "category_id": 12},
    {"id": 3, "title": "Community meetup", "category_id": 99, "last_posted_at": "2026-10-16T00:00:00Z"},
]}}


class FakeResponse:
    def __init__(self, data, uri):
        self.data = data
        self.uri = uri
    def __enter__(self): return self
    def __exit__(self, *_): return False
    def geturl(self): return self.uri
    def read(self, amount): return self.data[:amount]


class AdapterTests(unittest.TestCase):
    def test_resolve_categories_by_slug_or_name(self):
        self.assertEqual(m.category_path(CATEGORIES, "open-source"), "/c/open-source/12.json")
        self.assertEqual(m.category_path(CATEGORIES, "Robotic Arms"), "/c/robotic-arms/23.json")
    def test_unknown_category_fails_closed(self):
        with self.assertRaises(m.PublicForumError): m.category_path(CATEGORIES, "hidden")
    def test_category_injection_rejected(self):
        cats = {"category_list": {"categories": [{"id": 1, "name": "x", "slug": "../../evil"}]}}
        with self.assertRaises(m.PublicForumError): m.category_path(cats, "x")
    def test_sort_recency_and_exclude_invalid_id(self):
        topics = m.clean_topics(TOPICS, CATEGORIES)
        self.assertEqual([x["id"] for x in topics], [2, 3, 1])
        self.assertEqual(topics[0]["url"], "https://labautomation.io/t/2")
    def test_filter_and_limit(self):
        topics = m.clean_topics(TOPICS, CATEGORIES, 1, ("open-source",))
        self.assertEqual([x["id"] for x in topics], [2])
    def test_limit_validation(self):
        with self.assertRaises(ValueError): m.clean_topics(TOPICS, CATEGORIES, 100)
    def test_public_json_never_sends_credentials(self):
        def fake_open(req, timeout):
            self.assertEqual(req.full_url, "https://labautomation.io/latest.json")
            self.assertEqual(req.get_method(), "GET")
            self.assertNotIn("api-key", {x.lower() for x in req.headers})
            self.assertEqual(timeout, 15)
            return FakeResponse(json.dumps(TOPICS).encode(), req.full_url)
        with patch.object(m, "urlopen", side_effect=fake_open):
            self.assertEqual(m.public_json("/latest.json"), TOPICS)
    def test_reject_other_host_and_unlisted_paths(self):
        for path in ["https://evil.com", "/users/me.json", "//evil.com/data", "/t/123.json", "/c/../1.json"]:
            with self.assertRaises(ValueError): m.public_json(path)
    def test_reject_external_redirect(self):
        with patch.object(m, "urlopen", return_value=FakeResponse(b'{}', "https://evil.com")):
            with self.assertRaises(m.PublicForumError): m.public_json("/latest.json")
    def test_reject_garbled_json(self):
        with patch.object(m, "urlopen", return_value=FakeResponse(b'<html>', "https://labautomation.io/latest.json")):
            with self.assertRaises(m.PublicForumError): m.public_json("/latest.json")
    def test_end_to_end_offline_category(self):
        def fake(path):
            return CATEGORIES if path == "/categories.json" else TOPICS
        with patch.object(m, "public_json", side_effect=fake):
            result = m.collect("open-source", 3)
        self.assertEqual(result["count"], 3)
        self.assertEqual(result["scope"], "public-read-only")
        self.assertEqual(result["feed"], "https://labautomation.io/c/open-source/12.json")
    def test_main_json_no_network(self):
        report = {"provider":"Lab Automation Forums","scope":"public-read-only","feed": "x","count":0,"topics":[]}
        with patch.object(m,"collect",return_value=report),patch("sys.stdout",new_callable=io.StringIO) as stdout:
            self.assertEqual(m.main(["--format","json"]),0)
        self.assertEqual(json.loads(stdout.getvalue())["scope"],"public-read-only")


if __name__ == "__main__":
    unittest.main()
