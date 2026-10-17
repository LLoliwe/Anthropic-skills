import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import { test } from 'node:test';

test('real BUILT Void Node server serves HTML/API without credentials or dummy secret exposure', { timeout: 70000 }, async () => {
  const port = 43000 + (process.pid % 10000);
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
  const hosts = ['localhost', '127.0.0.1', '[::1]'];
  const request = async (host, path) => fetch(`http://${host}:${port}${path}`, { signal: AbortSignal.timeout(1200) });
  try {
    const deadline = Date.now() + 52000;
    let html, api, activeHost;
    while (Date.now() < deadline) {
      if (child.exitCode !== null) throw new Error('Built Node server exited: ' + logs);
      for (const host of hosts) {
        try {
          const [home, health] = await Promise.all([request(host,'/'), request(host,'/api/health')]);
          if (home.ok && health.ok) {
            html = await home.text(); api = await health.json(); activeHost = host; break;
          }
        } catch { /* another loopback family may be used on this host */ }
      }
      if (activeHost) break;
      await new Promise((resolve) => setTimeout(resolve, 500));
    }
    assert.ok(html, 'Built Node server failed real HTTP routes. Logs: ' + logs);
    assert.match(html, /Launch Desk — Pryntor/);
    assert.match(html, /fetch\("\/api\/health"/);
    assert.deepEqual(api, { ok: true, service: 'pryntor-launch-desk', runtime: 'node', release: 'beta' });
    assert.doesNotMatch(html + JSON.stringify(api), new RegExp(marker));
    for (let i = 0; i < 5; i++) {
      const resp = await request(activeHost, '/api/health');
      assert.equal(resp.status, 200);
      assert.match(resp.headers.get('content-type') || '', /application\/json/);
      assert.equal(resp.headers.get('cache-control'), 'no-store');
      assert.equal(resp.headers.get('x-content-type-options'), 'nosniff');
      assert.deepEqual(await resp.json(), api);
    }
    const missing = await request(activeHost, '/api/not-a-real-route');
    assert.equal(missing.status, 404);
  } finally {
    if (child.pid && process.platform !== 'win32') {
      try { process.kill(-child.pid, 'SIGTERM'); } catch {}
    } else child.kill();
  }
});
