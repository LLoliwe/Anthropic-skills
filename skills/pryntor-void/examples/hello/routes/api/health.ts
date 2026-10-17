import { defineHandler } from 'void';

export const GET = defineHandler((c) =>
  c.json({
    ok: true,
    service: 'pryntor-void-pilot',
    deployment: 'local-only',
  }),
);
