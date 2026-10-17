import { defineHandler } from 'void';

export const GET = defineHandler((c) => {
  c.header('Cache-Control', 'no-store');
  c.header('X-Content-Type-Options', 'nosniff');
  return c.html(`<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Pryntor Void Pilot</title></head>
<body><main><h1>Pryntor Void Pilot</h1><p>Built Node.js runtime serving a real Void route.</p><p><a href="/api/health">View live health response</a></p></main></body></html>`);
});
