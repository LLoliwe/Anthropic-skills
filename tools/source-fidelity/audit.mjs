#!/usr/bin/env node
// Pryntor original R0 source-fidelity audit. No external dependencies or network.
import { createHash } from 'node:crypto';
import { readFileSync, statSync } from 'node:fs';
import { pathToFileURL } from 'node:url';

export function sha256(value) {
  return createHash('sha256').update(value, 'utf8').digest('hex');
}

const isSpan = (s, text) => Array.isArray(s) && s.length === 2 &&
  s.every(Number.isSafeInteger) && s[0] >= 0 && s[1] > s[0] && s[1] <= text.length;
const isText = (v, max) => typeof v === 'string' && v.length > 0 && v.length <= max;

export function audit(manifest) {
  const errors = [];
  const reject = (id, code) => errors.push({ id, code });
  if (!manifest || typeof manifest !== 'object' || Array.isArray(manifest) || manifest.version !== 1) {
    reject('manifest', 'invalid_version');
    return { ok: false, checked: 0, errors };
  }
  const source = manifest.source;
  if (!source || typeof source !== 'object' || !isText(source.ref, 2048) ||
    !isText(source.text, 200000) || !/^[a-f0-9]{64}$/.test(source.sha256 ?? '')) {
    reject('source', 'invalid_source');
    return { ok: false, checked: 0, errors };
  }
  if (sha256(source.text) !== source.sha256) reject('source', 'sha256_mismatch');
  if (typeof manifest.answer !== 'string' || manifest.answer.length > 100000) {
    reject('answer', 'invalid_answer');
    return { ok: false, checked: 0, errors };
  }
  if (!Array.isArray(manifest.claims) || manifest.claims.length < 1 || manifest.claims.length > 500) {
    reject('claims', 'invalid_claims');
    return { ok: false, checked: 0, errors };
  }
  const seen = new Set();
  for (const claim of manifest.claims) {
    if (!claim || typeof claim !== 'object' || !isText(claim.id, 128)) {
      reject('claim', 'invalid_claim_id');
      continue;
    }
    const id = claim.id;
    if (seen.has(id)) { reject(id, 'duplicate_claim_id'); continue; }
    seen.add(id);
    if (claim.type === 'copy') {
      if (!isText(claim.value, 100000) ||
          !isSpan(claim.sourceSpan, source.text) || !isSpan(claim.answerSpan, manifest.answer)) {
        reject(id, 'invalid_copy_claim');
        continue;
      }
      if (source.text.slice(...claim.sourceSpan) !== claim.value) reject(id, 'source_span_mismatch');
      if (manifest.answer.slice(...claim.answerSpan) !== claim.value) reject(id, 'answer_span_mismatch');
    } else if (claim.type === 'absent') {
      if (!isText(claim.needle, 100000)) { reject(id, 'invalid_absence_claim'); continue; }
      if (source.text.includes(claim.needle)) reject(id, 'needle_present');
    } else {
      reject(id, 'unknown_claim_type');
    }
  }
  return { ok: errors.length === 0, checked: manifest.claims.length, errors };
}

// Only run the CLI when explicitly invoked (never on module import).
if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  let result;
  try {
    if (process.argv.length !== 3) throw new Error('usage: node audit.mjs manifest.json');
    const path = process.argv[2];
    if (statSync(path).size > 1024 * 1024) throw new Error('manifest_too_large');
    result = audit(JSON.parse(readFileSync(path, 'utf8')));
  } catch (error) {
    result = { ok: false, checked: 0, errors: [{ id: 'cli', code: 'invalid_input' }] };
  }
  process.stdout.write(JSON.stringify(result) + '\n');
  process.exitCode = result.ok ? 0 : 1;
}
