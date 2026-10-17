# Pryntor × Void 1.1.11 — built Node runtime hardening (R1)

**Status:** CI hardening candidate, not production-authorized. No live Cloudflare, Railway or Vercel deployment. Production release requires a named owner and independent human security review.

## What's different from the R0 disposable pilot?

- Void config uses `target:'node'` to demonstrate cloud-independent built server; no Cloudflare bindings.
- Node production runtime starts via `node dist/ssr/index.js` and exposes GET /api/health.
- Tests check the **built Node server** (not just Vite dev), client JavaScript asset, five repeated responses, cache/type headers and no dummy secret leakage.
- Node >=24.21.0, pinned dependencies, and committed npm lockfile + `npm ci` gate before release.
- CI never authenticates or deploys to any platform. Build artifact and dependency vulnerability report are retained for seven days.

## On a compatible developer machine

```sh
cd skills/pryntor-void/examples/hello
npm ci --no-audit --no-fund
npm run policy
npm run build
npm run smoke
npm run smoke:prod
npm audit --audit-level=high
```

Local build is R0; no Cloudflare account is required. CI executes an initial lockfile-bootstrap install *only once*, and the final release gate requires committed `package-lock.json` plus `npm ci`.

## Deployment compatibility and release gates

Void's Node target can deploy `dist/ssr` and `dist/client` to a compatible Node host but **does not support** `void/db`, `void/kv`, `void/ai`, `void/auth`, `void/env`, `void/storage`, managed WebSockets or other Cloudflare-specific bindings. Those cannot be silently ported.

Before production: review dependency audit (including high/critical), verify no secrets, real data privacy, auth/abuse protection if routes expand, observability, backup/restore if data is added, health checks, resource budgets, deploy target access, CI branch protection, rollback and independent human approval. For any real app, test its own code and dependencies, not just this fixture.

Production deploy for a standalone Node host is not `void deploy`: publish the *same tested artifact* with the Node runtime and start `node dist/ssr/index.js`. Smoke the resulting HTTPS URL, verify security, rollback capability and no-spend budget. Do not promote this reference fixture as a commercial app.

See `PRODUCTION_GATE.md` for the recorded release decision.
