import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { validatePolicy, assessSignerHost } from './preflight.mjs';

const clean = JSON.parse(readFileSync(new URL('./policy.json', import.meta.url), 'utf8'));
const mutate = callback => { const p = structuredClone(clean); callback(p); return p; };
test('original baseline explicitly gates all live actions', () => assert.deepEqual(validatePolicy(clean), []));
test('rejects missing repository identity', () => assert.match(validatePolicy(mutate(p => p.upstream.repository='other/reset')).join(' '), /identity/));
test('rejects abbreviated revision', () => assert.match(validatePolicy(mutate(p => p.upstream.commit='6132e86')).join(' '), /commit/));
test('rejects unreviewed license claimed green', () => assert.match(validatePolicy(mutate(p => p.upstream.licenseConfirmed=true)).join(' '), /license/));
test('rejects implicit read-only mode escalation', () => assert.match(validatePolicy(mutate(p => p.mode='mainnet')).join(' '), /mode/));
test('rejects wallet creation', () => assert.match(validatePolicy(mutate(p => p.permissions.createWallet=true)).join(' '), /createWallet/));
test('rejects Bitcoin header posting', () => assert.match(validatePolicy(mutate(p => p.permissions.miningMoves=true)).join(' '), /miningMoves/));
test('rejects outgoing transfers', () => assert.match(validatePolicy(mutate(p => p.permissions.transfers=true)).join(' '), /transfers/));
test('rejects background agent', () => assert.match(validatePolicy(mutate(p => p.permissions.backgroundAgent=true)).join(' '), /backgroundAgent/));
test('rejects active chat', () => assert.match(validatePolicy(mutate(p => p.permissions.chatMode='active')).join(' '), /chat/));
test('rejects invented MCP acceptance result', () => assert.match(validatePolicy(mutate(p => p.runtime.mcpLiveVerified=true)).join(' '), /mcpLiveVerified/));
test('rejects unsigned human release approval', () => assert.match(validatePolicy(mutate(p => p.approvals.separateHumanLiveGoAhead=true)).join(' '), /separateHumanLiveGoAhead/));
test('signer host refuses Node 22 and missing security prerequisites', () => {
  const r=assessSignerHost({nodeMajor:22,isolatedHost:false,reviewedSource:false,interactiveSecretEntry:false});
  assert.equal(r.readyForSeparateSignerSetup,false); assert.equal(r.problems.length,4);
});
test('host precheck is only a precheck, even with declared prerequisites', () => {
  const r=assessSignerHost({nodeMajor:24,isolatedHost:true,reviewedSource:true,interactiveSecretEntry:true});
  assert.equal(r.readyForSeparateSignerSetup,true);
  assert.deepEqual(validatePolicy(clean),[]); assert.equal(clean.runtime.mcpLiveVerified,false);
});
