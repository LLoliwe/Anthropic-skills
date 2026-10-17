# Pryntor Interface Lab R0 — actual FREE HeroUI package pilot

A deliberately **synthetic, original** and isolated React app exercising the HeroUI v3 **free** Button package, its style import, responsive layout, filtering, search, disclosure selection, local-only saved state and reduced-motion. No production logins, customer data, real agent connection, analytics or travel bookings.

## Local launch

Requires Node 22+, npm and **network access to the public npm registry**. Do not use paid Pro content.

```sh
cd examples/heroui-free-pilot
npm install --no-audit --no-fund
npm run check
npm run build
npx playwright install chromium
npm run test:e2e
npm run dev
```

- Source package manifests pinned: `@heroui/react@3.2.6`, `@heroui/styles@3.2.6`, React 19.2.0 and Tailwind 4.3.3.
- **Actual package installs are not claimed until CI completes.** Local runtime in initial authoring environment has no npm registry DNS. CI will prove or reject the actual install and test.
- Host release not authorized. Preview only locally unless reviewed and approved.
- After CI: inspect `qa/screenshots/`, `qa/playwright-report/`, bundle size and actual install lockfile. `npm ci` requires a committed lockfile; npm install is used only during initial bootstrap to generate the first lock. Commit reviewed lock before production adoption.
- Verified package manifests declare MIT; upstream repo root Apache 2.0: https://github.com/heroui-inc/heroui . Check redistributed assets, transitive terms and NOTICE. Paid Pro: **excluded**.
- This example is only a shared method reference. No other venture gains an installed package or public deployment by having this directory.

See `skills/pryntor-heroui-free/SKILL.md`, `research/heroui/COMPANY-ROLLOUT.md` and Linear https://linear.app/pryntor/issue/PRY-273 .
