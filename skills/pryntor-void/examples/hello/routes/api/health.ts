import { defineHandler } from 'void';

export const GET = defineHandler((c) => {
  c.header('Cache-Control', 'no-store');
  c.header('X-Content-Type-Options', 'nosniff');
  return c.json({
    ok: true,
    service: 'pryntor-launch-desk',
    runtime: 'node',
    release: 'beta',
  });
});
