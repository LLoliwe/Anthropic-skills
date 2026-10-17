# Void Node production readiness gate — Pryntor (17 Oct 2026)

## Decision boundaries

| Gate | Evidence required | Current decision |
| --- | --- | --- |
| R0 pilot | Real framework dev server, route, static build | PASS (PR #10, Actions 39019052151) |
| R1 reproducibility | Commit package-lock; clean `npm ci`; pinned Node | PENDING until latest-head CI |
| R1 real runtime | `target:'node'` compiled SSR+client, HTTP API + JS asset tests | PENDING until latest-head CI |
| R1 dependency analysis | `npm audit` high/critical triage and licences | PENDING security reviewer |
| R2 operational staging | Named real app, hosting, resource quotas, TLS, logs, monitoring, rollback | NOT STARTED |
| R2 human QA | Independent reviewer with signed evidence/review | NOT STARTED |
| R3 production | Approved customer-data boundary, on-call owner, verified actual traffic | NOT AUTHORIZED |

## Rollback / promotion runbook

1. Record current deployed immutable artifact SHA and its exact hostname, routing, database compatibility and rollback owner.
2. Deploy the preapproved image/artifact to isolated staging. Smoke `/`, `/api/health`, browser JS assets, response headers and error paths over HTTPS; monitor startup and resource usage.
3. Compare baseline functionality, traffic, cost and failure metrics; get independent reviewer and owner approval. NEVER self-approve.
4. Promote a tested immutable artifact only through protected deployment approval; no on-the-fly npm install or remote content pull during cutover.
5. On any regression, route traffic to the recorded last-known-good artifact, verify all primary routes and monitor; never roll back code across incompatible schema migrations.
6. Revoke any unused tokens; document exact elapsed recovery and incident outcome in PRY-230.

## Current constraints

This fixture has no authentication or customer data, no datastore and no paid/production deployment. Health check is intentionally simple; it is NOT evidence that a real business app is secured. Node target trades away Cloudflare bindings. `npm audit` is automated inventory only, not supply-chain signoff. Do not represent the shared self-hosted Cloudflare Void platform as free, and do not report platform-wide installation without checking agents and target repos.

Links: https://github.com/LLoliwe/Anthropic-skills/pull/10 ; https://linear.app/pryntor/issue/PRY-230 ; https://void.cloud/integrations/nodejs-bun-deno .
