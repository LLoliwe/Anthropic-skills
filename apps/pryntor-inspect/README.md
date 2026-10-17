# Pryntor Inspect — Local-first public preview

An original, premium editorial interface inspired by the clarity and restraint of modern software design. No Apple logos, assets or copyrighted visual elements were copied.

**What it does:** Read-only browser analysis of up to 20 user-selected JS/TS/HTML/CSS/JSON files; source inventory, import relationships, file details, heuristic review notes and a local JSON export. Includes original Pryntor test fixture. All input stays in browser memory; no network APIs, uploads, account or telemetry. Source text is never echoed to HTML or the exported report. No external fonts or dependencies. CSP blocks outgoing connections.

**What it does not do:** This is NOT the full REA MCP reverse engineering engine, a formal security audit, arbitrary binary analyzer, execution sandbox, customer data processor, or proof of independent human security approval. The separate REA cloud MCP host only analyzes a pinned owned fixture.

Preview launch is an early customer-facing **local-only beta**, not a released commercial managed reverse-engineering service. Do not invite customers to upload confidential third-party assets without rights/consent. User data remains local.

Run tests: `node --test apps/pryntor-inspect/test.mjs`. Serve `apps/pryntor-inspect` as static files, no backend. Test via keyboard and mobile viewport; verify sample and real own-code file upload, JSON export, and reset.

For human acceptance, recruit consenting known testers; record anonymised usability/bug feedback without collecting their source files. Before promoting to managed paid product, require independently recorded human security approval, legal/IP review, customer consent, threat model and isolated server-side processing. Physical AC control N/A.

This repo's global REA skill and free host remain separate from this intentionally restricted customer preview.
