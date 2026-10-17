import assert from 'node:assert/strict';
import { existsSync, readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';

const root = fileURLToPath(new URL('../', import.meta.url));
const app = root + 'examples/hello/';
const pkg = JSON.parse(readFileSync(app + 'package.json', 'utf8'));
assert.equal(pkg.private, true);
assert.equal(pkg.devDependencies.void, '1.1.11');
assert.equal(pkg.devDependencies.vite, '8.1.2');
assert.equal(pkg.dependencies['@hono/node-server'], '2.1.4');
assert.equal(pkg.scripts.build, 'vite build');
assert.equal(pkg.scripts.start, 'node dist/ssr/index.js');
assert.equal(pkg.scripts['smoke:prod'], 'node --test test/production-smoke.mjs');

const config = readFileSync(app + 'void.config.ts', 'utf8');
assert.match(config, /target: 'node'/);
assert.doesNotMatch(config, /account_id|apiToken|CLOUDFLARE_API_TOKEN/);

const workflow = readFileSync(fileURLToPath(new URL('../../../.github/workflows/pryntor-void-lab.yml', import.meta.url)), 'utf8');
assert.doesNotMatch(workflow, /\bvoid deploy\b|CLOUDFLARE_API_TOKEN:|VOID_TOKEN:|id-token:\s*write/);
assert.match(workflow, /npm run build/);
assert.match(workflow, /npm run smoke:prod/);
assert.match(workflow, /npm ci/);

const lockFile = app + 'package-lock.json';
if (existsSync(lockFile)) {
  const lock = JSON.parse(readFileSync(lockFile, 'utf8'));
  assert.equal(lock.lockfileVersion, 3);
  assert.equal(lock.packages[''].devDependencies.void, '1.1.11');
  assert.equal(lock.packages[''].dependencies['@hono/node-server'], '2.1.4');
} else {
  // Only for the one-time CI bootstrap; not acceptable for any release.
  assert.equal(process.env.PRYNTOR_BOOTSTRAP_LOCK, '1', 'Committed package-lock.json is required');
}
console.log('policy: node target, pinned packages, no deploy credentials, CI and reproducible install constraints checked');
