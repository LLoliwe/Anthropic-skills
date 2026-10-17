import json
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from vault import Vault, VaultError


class VaultTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.vault = Vault(Path(self.tmp.name) / 'owner')

    def propose(self, key='sample', **kw):
        return self.vault.propose(key=key, kind=kw.get('kind', 'Memory'),
                                  scope=kw.get('scope', 'Company'),
                                  sensitivity=kw.get('sensitivity', 'Internal'),
                                  content=kw.get('content', 'Synthetic fact'),
                                  source='local:unit-test', owner='example-owner',
                                  expected_revision=kw.get('expected_revision'))

    def export(self, scope='Company'):
        dest = Path(self.tmp.name) / f'{scope}.json'
        res = self.vault.export_agent(scope, dest)
        return res, json.loads(dest.read_text())

    def test_proposal_private_by_default(self):
        self.propose()
        self.assertEqual(self.export()[0]['records'], 0)

    def test_approved_not_shared_without_agent_read(self):
        self.propose()
        self.vault.approve('sample', 1, 'reviewer')
        self.assertEqual(self.export()[0]['records'], 0)

    def test_export_allowlist(self):
        self.propose()
        self.vault.approve('sample', 1, 'reviewer', agent_read=True)
        result, data = self.export()
        self.assertEqual(result['records'], 1)
        self.assertEqual(data['records'][0]['key'], 'sample')
        self.assertEqual(data['checksum'], __import__('vault').digest(data['records']))

    def test_scope_isolation(self):
        self.propose(scope='Personal')
        self.vault.approve('sample', 1, 'reviewer', agent_read=True)
        self.assertEqual(self.export('Company')[0]['records'], 0)
        self.assertEqual(self.export('Personal')[0]['records'], 1)

    def test_restricted_never_shared(self):
        self.propose(sensitivity='Restricted')
        with self.assertRaises(VaultError):
            self.vault.approve('sample', 1, 'reviewer', agent_read=True)

    def test_conflicting_update_fails(self):
        self.propose()
        with self.assertRaises(VaultError):
            self.propose(content='different')
        with self.assertRaises(VaultError):
            self.propose(content='different', expected_revision=0)
        self.assertEqual(self.propose(content='different', expected_revision=1)['revision'], 2)

    def test_verify_detects_edit(self):
        self.propose()
        state = self.vault._load()
        state['entries']['sample']['content'] = 'Tampered'
        self.vault.path.write_text(json.dumps(state))
        with self.assertRaises(VaultError):
            self.vault.verify()

    def test_verify_detects_event_edit(self):
        self.propose()
        state = self.vault._load()
        state['events'][0]['action'] = 'forged'
        self.vault.path.write_text(json.dumps(state))
        with self.assertRaises(VaultError):
            self.vault.verify()

    def test_prevent_obvious_secrets(self):
        with self.assertRaises(VaultError):
            self.propose(content='password=THIS_SHOULD_NOT_BE_STORED')

    def test_invalid_source(self):
        with self.assertRaises(VaultError):
            self.vault.propose(key='sample', kind='Memory', scope='Company',
              sensitivity='Internal', content='Example', source='http://not-secure', owner='X')

    def test_handoff_is_quarantined_proposal(self):
        self.propose()
        self.vault.approve('sample', 1, 'reviewer', agent_read=True)
        result, _ = self.export()
        second = Vault(Path(self.tmp.name) / 'second')
        self.assertEqual(second.import_handoff(result['path'], 'receiver')['imported_proposals'], 1)
        self.assertEqual(second.export_agent('Company', Path(self.tmp.name) / 'receiver.json')['records'], 0)
        self.assertEqual(second.verify()['verified_records'], 1)

    def test_handoff_corruption_rejected(self):
        self.propose()
        self.vault.approve('sample', 1, 'reviewer', agent_read=True)
        result, _ = self.export()
        p = Path(result['path'])
        state = json.loads(p.read_text())
        state['records'][0]['content'] = 'Modified'
        p.write_text(json.dumps(state))
        with self.assertRaises(VaultError):
            Vault(Path(self.tmp.name) / 'new').import_handoff(p, 'receiver')

    def test_empty_vault_valid(self):
        self.assertEqual(self.vault.verify()['verified_records'], 0)

    def test_export_cannot_overwrite_vault(self):
        self.propose()
        with self.assertRaises(VaultError):
            self.vault.export_agent('Company', self.vault.path)

if __name__ == '__main__':
    unittest.main()
