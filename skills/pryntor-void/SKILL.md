---
name: pryntor-void
description: Optional, tested Void 1.1.11 framework skill for isolated Pryntor Vite apps. Evaluate compiled Node/Cloudflare build and hosting tradeoffs without new vendor spend.
---

# Pryntor Void — gated opt-in capability

Official upstream: https://github.com/voidzero-dev/void (MIT). Source is vendored only as pinned npm dependency `void@1.1.11`; optional engineering pilot, **not** global fleet-installation.

## Procedure
1. Determine target (Node / Bun / Deno / Cloudflare) before generating code; never pretend Cloudflare bindings run on Node.
2. Use `examples/hello` as isolated Node sample. Install Node >=24.21, run `npm ci`, static policy check, `npm run build`, `npm run smoke`, `npm run smoke:prod` and audit.
3. Require matching committed lockfile, exact dependency pins, latest-head hosted CI run and saved build artifact; do not trust stale passing builds.
4. Never copy credentials or real customer data into generated code, files, logs or CI. No paid resources, login, live deployment, DNS, migration, persistent agent installation or public release without scoped authorization.
5. Read full `PRODUCTION_GATE.md` and `README.md`. A green build is **not** production certification. Have an independent reviewer verify data boundaries, dependencies, auth, performance, rollback, legal/rights, observability and spend, then sign off separately.
6. Treat LVL7 and Mission Control as first evaluation candidates; avoid automatic migration of Python Recover or WordPress Tirisano.

Keep R1 (technical build/HTTP) independent from R2 (real staging and human-reviewed production).
