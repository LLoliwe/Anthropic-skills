# Pryntor Inspect — Local-first public preview

An original, premium editorial interface inspired by the clarity and restraint of modern software design. No Apple logos, assets or copyrighted visual elements were copied.

**What it does:** Read-only browser analysis of up to 20 user-selected JS/TS/HTML/CSS/JSON files; source inventory, import relationships, file details, heuristic review notes and a local JSON export. Includes original Pryntor test fixture. All input stays in browser memory; no network APIs, uploads, account or telemetry. Source text is never echoed to HTML or the exported report. No external fonts or dependencies. CSP blocks outgoing connections.

**What it does not do:** This is NOT the full REA MCP reverse engineering engine, a formal security audit, arbitrary binary analyzer, execution sandbox, customer data processor, or proof of independent human security approval. The separate REA cloud MCP host only analyzes a pinned owned fixture.

Preview launch is an early customer-facing **local-only beta**, not a released commercial managed reverse-engineering service. Do not invite customers to upload confidential third-party assets without rights/consent. User data remains local.

Run tests: `node --test apps/pryntor-inspect/test.mjs`. Serve `apps/pryntor-inspect` as static files, no backend. Test via keyboard and mobile viewport; verify sample and real own-code file upload, JSON export, and reset.

For human acceptance, recruit consenting known testers; record anonymised usability/bug feedback without collecting their source files. Before promoting to managed paid product, require independently recorded human security approval, legal/IP review, customer consent, threat model and isolated server-side processing. Physical AC control N/A.

This repo's global REA skill and free host remain separate from this intentionally restricted customer preview.


## V0 frozen / V1 global benchmark and original implementation

V0 frozen branch release/pryntor-inspect-v0-20261017 at commit 5fab3445d13c955a2a863ca41c79f9b342ae5a85; V0 Render URL must remain intact. Develop V1 on separate feature/pryntor-inspect-v1-code-intelligence-20261017 and separate preview. Inspired by publicly documented interaction patterns; does not copy vendor code, screens, marks or unlicensed assets.

- Apple Human Interface Guidelines — user agency, clear purpose, accessible interaction, simplicity: https://developer.apple.com/design/human-interface-guidelines/design-principles/
- Raycast Action Panel — Ctrl/Command+K, search, accessible keyboard commands: https://manual.raycast.com/action-panel
- Sourcegraph — inspect dependencies and connected files, but sourcegraph compiler-accurate SCIP navigation is NOT present here: https://sourcegraph.com/docs/code-navigation
- Semgrep — severity-grouped traceable issues, whereas our local notes remain author-built regex heuristics, NOT full SAST: https://semgrep.dev/products/semgrep-appsec-platform/
- GitHub code scanning — line-specific source-linked review rather than claiming security certification: https://docs.github.com/en/code-security/concepts/code-scanning/code-scanning-alerts
- Vercel responsive dashboard navigation — readable mobile hierarchy: https://vercel.com/changelog/dashboard-navigation-redesign-rollout
- Linear intelligent triage — focused human-understandable suggestions and feedback loop: https://linear.app/now/how-we-built-triage-intelligence

V1 features: entirely offline searchable command palette, heuristic interactive SVG import relationship map and selectable file list, transitive-dependents *suggestions*, severity and text filters, direct finding-to-file links, more accurate local path-aware resolution, responsive original CSS, no external fonts or scripts, no raw source in reports. Source snippets are not sent to remote servers. No full AST parser, runtime execution, managed customer REA tool, or independent security approval.

QA: run node --test apps/pryntor-inspect/test.mjs apps/pryntor-inspect/v1-test.mjs and test Chromium on desktop/mobile with samples, uploads, keyboard commands, SVG navigation, export, reset and actual browser network. Scope human test reports as opt-in, no customer code collection. Full managed REA release and human expert signoff remain separate gates.
