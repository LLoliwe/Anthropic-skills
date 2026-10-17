import test from 'node:test';
import assert from 'node:assert/strict';
import { audit, sha256 } from './audit.mjs';

function fixture(sourceText, answer, value) {
  const start = sourceText.indexOf(value);
  const outStart = answer.indexOf(value);
  assert.ok(start >= 0 && outStart >= 0, 'test fixture must contain copied value');
  return {
    version: 1,
    source: { ref: 'synthetic:1', text: sourceText, sha256: sha256(sourceText) },
    answer,
    claims: [{ id: 'claim-1', type: 'copy', value, sourceSpan: [start, start + value.length], answerSpan: [outStart, outStart + value.length] }]
  };
}
function hasCode(manifest, code) { assert.ok(audit(manifest).errors.some(e => e.code === code)); }

test('accepts exact source and answer spans', () => {
  const x = fixture('Campaign ID: MT-123', 'Campaign ID is MT-123', 'MT-123');
  assert.equal(audit(x).ok, true);
});
test('rejects altered answer without auto-correction', () => {
  const x = fixture('Spend R1,200', 'Spend R1,200', 'R1,200');
  x.answer = 'Spend R1,300';
  hasCode(x, 'answer_span_mismatch');
});
test('rejects source range shift even if answer is right', () => {
  const x = fixture('ABC ABC', 'ABC', 'ABC');
  x.claims[0].sourceSpan = [1, 4];
  hasCode(x, 'source_span_mismatch');
});
test('rejects forged stale hash', () => {
  const x = fixture('amount=-12.05', '-12.05', '-12.05');
  x.source.text = 'amount=+12.05';
  hasCode(x, 'sha256_mismatch');
});
test('rejects duplicates and unknown claim modes', () => {
  const x = fixture('ID X1', 'X1', 'X1');
  x.claims.push({ ...x.claims[0] });
  hasCode(x, 'duplicate_claim_id');
  x.claims[1].id = 'claim-2'; x.claims[1].type = 'rewrite';
  hasCode(x, 'unknown_claim_type');
});
test('rejects empty/zero-length or out-of-bounds spans', () => {
  const x = fixture('K=abc', 'abc', 'abc');
  x.claims[0].answerSpan = [0, 0];
  hasCode(x, 'invalid_copy_claim');
  x.claims[0].answerSpan = [0, 999];
  hasCode(x, 'invalid_copy_claim');
});
test('absence checks are exact and cannot prove a refusal', () => {
  const x = fixture('BLUE', 'BLUE', 'BLUE');
  x.claims = [{ id: 'absent-1', type: 'absent', needle: 'RED' }];
  assert.equal(audit(x).ok, true);
  x.claims[0].needle = 'BLUE';
  hasCode(x, 'needle_present');
});
test('rejects missing or malformed source and manifests', () => {
  assert.equal(audit(null).ok, false);
  const x = fixture('ID X1', 'X1', 'X1');
  x.source.sha256 = 'bad';
  hasCode(x, 'invalid_source');
  x.source.sha256 = sha256(x.source.text); x.claims = [];
  hasCode(x, 'invalid_claims');
});
test('UTF-16 spans support unicode when offsets are measured correctly', () => {
  const x = fixture('🎵 track=AA7', 'Song 🎵 AA7', 'AA7');
  assert.equal(audit(x).ok, true);
});
test('100 deterministic synthetic fixtures pass, then reject corrupt answer spans', () => {
  const groups = ['identifiers', 'money-dates', 'math', 'code-utm', 'long-context'];
  for (let i = 0; i < 100; i++) {
    const part = groups[i % groups.length];
    const values = {
      'identifiers': 'PRY-' + String(1000 + i),
      'money-dates': 'R' + (i + 1) + ',' + String(100 + i),
      'math': 'x^2-' + (i + 1) + '=0',
      'code-utm': 'utm_campaign=sample_' + i,
      'long-context': 'case:' + String(i).padStart(4, '0') + ':EXACT'
    };
    const value = values[part];
    const source = 'DUMMY ' + 'distractor false-id '.repeat(part === 'long-context' ? 250 : 2) + ' ' + part + '=' + value + ' END';
    const x = fixture(source, 'Reporting ' + value, value);
    assert.equal(audit(x).ok, true, part + ' ' + i);
    x.claims[0].answerSpan[0]++;
    assert.equal(audit(x).ok, false, 'tampered ' + part + ' ' + i);
  }
});
