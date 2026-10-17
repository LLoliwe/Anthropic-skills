import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import { test } from 'node:test';

test('real BUILT Void Node server serves API and static assets without secrets', { timeout: 70000 }, async () => {
  const port = 43000 + (process.pid % 10000);
  const base = `http://127.0.0.1:${port}`;
  const marker = 'PRYNTOR_NOT_A_REAL_SECRET_DO_NOT_EXPOSE';
  const child = spawn(process.execPath, ['dist/ssr/index.js'], {
    cwd: process.cwd(),
    stdio: ['ignore', 'pipe', 'pipe'],
    env: {
      ...process.env,
      PORT: String(port),
      PRYNTOR_TEST_SECRET: marker,
      CLOUDFLARE_API_TOKEN: '',
      VOID_TOKEN: '',
      NODE_ENV: 'production',
    },
    detached: process.platform !== 'win32',
  });
  let logs = '';
  for (const stream of [child.stdout, child.stderr]) {
    stream.on('data', (chunk) => { logs = (logs + String(chunk)).slice(-8000); });
  }
  const get = async (path) => fetch(base + path, { signal: AbortSignal.timeout(2000) });
  try {
    const deadline = Date.now() + 60000;
    let html, api;
    while (Date.now() < deadline) {
      if (child.exitCode !== null) throw new Error('Built Node server exited: ' + logs);
      try {
        const [home, health] = await Promise.all([get('/'), get('/api/health')]);
        if (home.ok && health.ok) { html = await home.text(); api = await health.json(); break; }
      } catch {}
      await new Promise((resolve) => setTimeout(resolve, 1000));
    }
    assert.ok(html, 'Built Node server did not start. Logs: ' + logs);
    assert.match(html, /Pryntor Void Pilot/);
    assert.deepEqual(api, { ok: true, service: 'pryntor-void-pilot', deployment: 'local-only' });
    assert.doesNotMatch(html + JSON.stringify(api), new RegExp(marker));
    for (let i = 0; i < 5; i++) {
      const resp = await get('/api/health');
      assert.equal(resp.status, 200);
      assert.match(resp.headers.get('content-type') || '', /application\/json/);
      assert.equal(resp.headers.get('cache-control'), 'no-store');
      assert.equal(resp.headers.get('x-content-type-options'), 'nosniff');
      assert.deepEqual(await resp.json(), api);
    }
    const script = html.match(/src="([^"]+\.js)"/);
    assert.ok(script, 'Built HTML must refer to hashed JavaScript');
    const asset = await get(script[1]);
    assert.equal(asset.status, 200, 'Built asset should serve from dist/client');
    assert.match(asset.headers.get('content-type') || '', /javascript/);
    assert.doesNotMatch(await asset.text(), new RegExp(marker));
  } finally {
    if (child.pid && process.platform !== 'win32') {
      try { process.kill(-child.pid, 'SIGTERM'); } catch {}
    } else child.kill();
  }
});
