# Pryntor Mission Control — actual OpenUI pilot

Isolated, synthetic-only evaluation for PRY-160. Implements the real MIT `@openuidev/react-lang` 1.0.1 component library, parser and React renderer; no model key or inference is needed. The runtime re-exports its parser from its real `@openuidev/lang-core` dependency. A built-in custom component library is used rather than the optional pre-styled react-ui package.

`npm ci && npm test && npm run build`

`node browser-check.mjs` uses Playwright Chromium against the compiled production build. Install with `npx playwright install --with-deps chromium`. The optional `BROWSER_EXECUTABLE_PATH` selects a preinstalled browser for restricted local environments. `npm run dev` binds only to loopback.

Venture and state filters change the OpenUI Lang payload; a schema validation pass rejects unknown components, unsupported props and unresolved references before rendering. Oversized payloads are rejected. The UI demonstrates an empty state and a deliberate invalid-input/recovery flow. No mutation/query/tool provider exists. Do not add arbitrary tools or untrusted component registries.

All five work cards are fictional. Historical 15 Oct runtime counts are labelled as historical, never live telemetry. This app has no backend, persistence, analytics, secrets, external asset loads, runtime control or customer data. Rendering a stored deterministic payload does not demonstrate LLM generation, agent commissioning, current production integrations or production approval.

Local verification on 17 Oct 2026: five Node test groups pass, actual renderer server markup verified, production build succeeds, full npm audit zero known advisories. Browser results are recorded by browser-check in evidence/ and uploaded by CI. Human design, assistive technology and independent security review remain pending. Do not promote the pilot to commercial production on these checks alone.

Upstream API guidance: https://www.npmjs.com/package/@openuidev/react-lang ; https://github.com/thesysdev/openui . Lockfile records exact dependency resolution. Original UI/code in this directory follows the repository license; third-party dependencies retain their respective licenses.
