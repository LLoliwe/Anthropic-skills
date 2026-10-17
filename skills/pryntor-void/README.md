# Pryntor × Void v1.1.11 isolated lab

This pilot adds a real Void route + browser fixture and a no-deploy CI smoke. It does **not** modify running Pryntor apps, provision Cloudflare, or install Void in persistent agents.

Sources: https://github.com/voidzero-dev/void ; https://void.cloud/guide/quickstart ; https://void.cloud/reference/api/plugin ; https://void.cloud/guide/platform/installation/prerequisites

## Local, if Node >=24.21.0 and npm is available

```bash
cd skills/pryntor-void/examples/hello
npm install --no-audit --no-fund
npm run build
npm run smoke
```

Use a throwaway shell/user; package install executes third-party scripts. CI runs in a disposable GitHub-hosted runner.

## Evidence gates

- **Repository**: pin upstream package, no production token, no deploy step.
- **CI**: package installation, real Void+Vite build, local dev-server HTTP checks (`/` and `/api/health`). Check workflow logs and run conclusion, not just the existence of a YAML.
- **Release**: production deployment remains HOLD pending independent security, cost/terms and credential review.
- **Venture fit**: LVL7 interactive prototypes first; Pryntor Mission Control internal demos next; BTWW experimental microsites optionally. Recover is currently Python/merchant-sensitive; Tirisano is WordPress, so neither should be migrated automatically.

## Costs and portability

`void@1.1.11` is MIT. A local build needs no Cloudflare account. Direct deployments may fit Cloudflare Workers Free quotas but still need account authentication. Self-hosted shared platform requires paid Workers for Platforms, a hosted PostgreSQL database and related services. Void supports standalone Node/Bun/Deno builds with limitations to Cloudflare binding APIs. These are architecture choices, not proof of cross-platform production compatibility.

## Security

No real customer, merchant, payment or travel details; no generated API keys. Inspect dependencies and run an independent audit before use with customer data. CI intentionally lacks `CLOUDFLARE_API_TOKEN` and any Void platform credentials.
