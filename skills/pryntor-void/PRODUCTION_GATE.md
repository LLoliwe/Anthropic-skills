# Void Node readiness gate — Pryntor — 17 Oct 2026

## Public beta deployment — verified

A live **public beta** is hosted at https://pryntor-launch-desk.onrender.com on **Render Free**, region Frankfurt, source commit `efaf21c03890144d6972dd642329cf79d9b42d2c`. Render deployment `dep-db9mgb6q1p3s738qa530` reported LIVE; independent HTML and health HTTPS fetches returned status 200. Service has `autoDeploy=no` and uses Node 24.21.0. The six-gate application stores user input **only in browser localStorage** and exports JSON locally; it does not accept server-side customer content. Costs are $0 plan selection, subject to Render bandwidth/build usage limits and suspension. Free instances spin down after 15 idle minutes and are explicitly unsuitable for reliable commercial production; third-party browser-interaction QA was attempted but timed out. **Commercial release and independent security approval remain HOLD.**


## Verified release matrix

| Gate | Evidence | Status |
| --- | --- | --- |
| R0 original framework pilot | PR #10, Actions [39019052151](https://github.com/LLoliwe/Anthropic-skills/actions/runs/39019052151) | PASS |
| R1 reproducible supply chain | Committed npm package-lock v3, pinned Node >=24.21, `npm ci`, static CI policy checks | PASS |
| R1 actual Node runtime | `target:'node'`; built SSR; real `GET /`, `GET /api/health`, five repeated HTTP responses, headers, nonexistent route 404, dummy-secret nonexposure | PASS |
| R1 npm security floor | Full `npm audit`: 0 high, 0 critical; `npm audit --omit=dev --audit-level=high` PASS | PASS with review exceptions |
| Moderate advisories and licences | **5 moderate npm advisories** involving `void`, `esbuild`, `drizzle-kit`, `@esbuild-kit/core-utils`, `@esbuild-kit/esm-loader`. Proposed npm fix is a breaking downgrade `void@0.1.6`; do NOT apply blindly. Human advisory and licence review remains missing. | HOLD FOR HUMAN REVIEW |
| R2 live staging | Approved real target/account, public HTTPS, telemetry, auth/abuse review, quotas/costs, deploy and tested rollback | NOT VERIFIED |
| R2 independent human review | Separate human reviewer approves code, dependencies, threat model and release | NOT VERIFIED |
| R3 commercial production | Named customer app, privacy boundary, budget and on-call owner, actual smoke & customer traffic | NOT AUTHORIZED |

**Latest green CI:** [Actions 39028612034](https://github.com/LLoliwe/Anthropic-skills/actions/runs/39028612034), sourced from PR [#13](https://github.com/LLoliwe/Anthropic-skills/pull/13), merged at `64018942dd653f34e0f202a8da68f874adeae72e`. Local dev smoke 1/1, compiled Node runtime smoke 1/1. No production environment was changed. Release artifact evidence expires after 7 days.

## Rollback and promotion runbook

1. Capture last-known-good immutable deployment artifact, commit, live domain, compatible schema, account and on-call owner.
2. Select explicit target and zero-new-spend allowance. Node runtime requires `dist/ssr` plus any `dist/client` output for the actual app; this fixture serves UI as a Void Node route and does not generate client bundles.
3. Deploy the exact CI-tested artifact to isolated staging over HTTPS. Verify health, index, negative routes, headers, auth where applicable, TLS, error logging and constraints.
4. Require a distinct human reviewer to sign off dependencies, data, auth, rights, budget, performance, monitoring and rollback. Never self-certify.
5. Promote only with protected deployment approval. At regression, restore recorded known-good deployment, smoke critical routes and record restore duration; do not downgrade code over incompatible database migrations.
6. Disable/revoke unneeded tokens; record deployment and review receipts in [PRY-230](https://linear.app/pryntor/issue/PRY-230).

## Hard safety boundary

This sample is a tiny no-database, no-auth internal reference app—not a commercially useful or customer-ready product. Node target is Cloudflare-independent but cannot import Void-managed `void/db`, `void/kv`, `void/ai`, `void/auth`, `void/storage` or Cloudflare platform bindings. Do not deploy the paid shared Void platform, spend money, migrate customer data, or call this global agent installation. The code is only opt-in in the Pryntor shared skills repository.
