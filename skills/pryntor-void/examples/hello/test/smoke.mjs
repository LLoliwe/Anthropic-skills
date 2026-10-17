import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import { test } from 'node:test';

test('Void serves the static page and real API route without Cloudflare credentials', { timeout: 70000 }, async () => {
  const port = 5397;
  const base = 'http://127.0.0.1:' + port;
  const child = spawn('npm', ['run', 'dev', '--', '--host', '127.0.0.1', '--port', String(port), '--strictPort'], {
    cwd: process.cwd(),
    stdio: ['ignore', 'pipe', 'pipe'],
    env: { ...process.env, CLOUDFLARE_API_TOKEN: '', VOID_TOKEN: '' },
    detached: process.platform !== 'win32',
  });
  let logs = '';
  for (const pipe of [child.stdout, child.stderr]) pipe.on('data', (data) => { logs += String(data).slice(-3000); });
  try {
    const deadline = Date.now() + 60000;
    let page, api;
    while (Date.now() < deadline) {
      if (child.exitCode !== null) throw new Error('Dev server exited: ' + logs);
      try {
        const [p, a] = await Promise.all([
          fetch(base + '/', { signal: AbortSignal.timeout(2000) }),
          fetch(base + '/api/health', { signal: AbortSignal.timeout(2000) }),
        ]);
        if (p.ok && a.ok) { page = await p.text(); api = await a.json(); break; }
      } catch {}
      await new Promise((resolve) => setTimeout(resolve, 1000));
    }
    assert.ok(page, 'Local HTML not served. Logs: ' + logs);
    assert.match(page, /Launch Desk — Pryntor/);
    assert.deepEqual(api, { ok: true, service: 'pryntor-void-pilot', deployment: 'local-only' });
  } finally {
    if (process.platform !== 'win32') { try { process.kill(-child.pid, 'SIGTERM'); } catch {} }
    else child.kill();
  }
});
