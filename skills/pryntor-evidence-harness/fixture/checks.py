import unittest
from search import search


class SearchRequirements(unittest.TestCase):
    def test_title(self):
        self.assertEqual([x['id'] for x in search('milk')], [1])

    def test_description(self):
        self.assertEqual([x['id'] for x in search('carton')], [1])