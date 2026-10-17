import importlib.util
import pathlib
import tempfile
import unittest

spec=importlib.util.spec_from_file_location("vault", pathlib.Path(__file__).with_name("vault.py"))
vault=importlib.util.module_from_spec(spec);spec.loader.exec_module(vault)

class SourceVaultTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.db=vault.connect(pathlib.Path(self.tmp.name)/"vault.sqlite3")
        self.addCleanup(self.db.close)

    def test_tracking_removed_and_query_sorted(self):
        self.assertEqual(vault.canonical_url("https://Example.com/p?utm_source=x&b=2&a=1#frag"),"https://example.com/p?a=1&b=2")
    def test_credentials_rejected(self):
        with self.assertRaises(ValueError): vault.canonical_url("https://a:b@example.com")
    def test_local_urls_rejected(self):
        for u in ["http://localhost", "http://127.0.0.1/a", "http://10.0.0.1", "http://foo.internal"]:
            with self.subTest(u=u), self.assertRaises(ValueError): vault.canonical_url(u)
    def test_dedupe_and_update(self):
        x=vault.add(self.db,"https://example.org/article?utm_medium=social","First","Alpha research")
        y=vault.add(self.db,"https://example.org/article","Updated","Beta research")
        self.assertEqual(x,y);self.assertEqual(self.db.execute("SELECT COUNT(*) FROM documents").fetchone()[0],1)
        self.assertEqual(len(vault.search(self.db,"beta")),1)
        self.assertEqual(len(vault.search(self.db,"alpha")),0)
    def test_private_search_excluded_by_default(self):
        vault.add(self.db,"https://example.org/internal","Secret","Company confidential decision",visibility="internal")
        self.assertEqual(vault.search(self.db,"confidential"),[])
        self.assertEqual(len(vault.search(self.db,"confidential",True)),1)
    def test_exports_public_only(self):
        vault.add(self.db,"https://example.org/public","Public","Research")
        vault.add(self.db,"https://example.org/private","Private","Decision",visibility="internal")
        self.assertEqual(len(vault.export_public(self.db)),1)
        self.assertEqual(len(vault.export_public(self.db,True)),2)
    def test_sql_injection_search_safe(self):
        vault.add(self.db,"https://example.org/a","Record","hello word")
        self.assertEqual(vault.search(self.db,"' OR 1=1 --"),[])
    def test_delete_removes_fts(self):
        i=vault.add(self.db,"https://example.org/c","To remove","specialenough word")
        with self.db:self.db.execute("DELETE FROM documents WHERE id=?",(i,))
        self.assertEqual(vault.search(self.db,"specialenough"),[])
    def test_content_limit(self):
        with self.assertRaises(ValueError): vault.add(self.db,"https://example.org/a","Huge","x"*(vault.MAX_TEXT_BYTES+1))
    def test_digest(self):
        vault.add(self.db,"https://example.org/a","Title","hello")
        h=self.db.execute("SELECT sha256 FROM documents").fetchone()[0]
        self.assertEqual(len(h),64)
    def test_unicode_search(self):
        vault.add(self.db,"https://example.org/z","Science","ukuhlola scientific")
        self.assertEqual(len(vault.search(self.db,"ukuhlola")),1)
    def test_invalid_scheme_rejected(self):
        with self.assertRaises(ValueError): vault.canonical_url("file:///etc/passwd")

if __name__=="__main__": unittest.main(verbosity=2)
