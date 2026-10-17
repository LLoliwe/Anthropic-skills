---
name: pryntor-void
description: Optional, evidence-gated VoidZero/Cloudflare Void SDK and CLI evaluation for isolated Pryntor Vite applications. Use only where it beats existing stacks on measured build and deployment outcomes.
---

# Pryntor Void — optional engineering capability

Upstream: https://github.com/voidzero-dev/void (MIT), https://void.cloud/guide/quickstart . Package pinned to `void@1.1.11` for the October 2026 pilot.

## Apply
- Prefer disposable, non-customer projects; first use the isolated fixture in `examples/hello`.
- Confirm Node >=24.21.0; read the matching installed `node_modules/void/docs/` before changing a client app.
- Choose Void only for compatible Vite/full-stack work. Do not replace existing Python, WordPress, React, Astro, Railway, or Cloudflare systems by default.
- Run `npm run build` and `npm run smoke` on the fixture; capture CI run URL, commit SHA, response and costs.
- Read only credentials and environment details from scoped CI secret manager; never paste tokens in agent prompts, logs, issues, Drive, or Slack.
- No auto-deploy, Cloudflare login, DNS changes, billed resources, account creation, public endpoint, migration, production customer data, or email without a separate approval and cost/permissions review.
- Direct Cloudflare Workers Free may work within quotas; the shared team platform requires paid Workers for Platforms and external database. Open source is not equivalent to free shared hosting.
- Preserve rights/attribution and avoid inventing QA results.

## Decision gate
1. **Local trial**: reproducible install, build, health-route HTTP smoke and static output; CI artifact.
2. **Engineering review**: inspect actual dependencies, license, token scopes and rollback; document alternatives (current Vite/Cloudflare, Railway, Render, Vercel).
3. **Production**: requires separate reviewed repo integration, real account permissions, budget authorization, secrets, rollback, independent human QA and security.

Status: pilot code only until latest-head CI evidence and independent review. This skill is opt-in, not a mandatory global agent installation.
