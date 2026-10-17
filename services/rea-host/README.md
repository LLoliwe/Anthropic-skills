# Pryntor REA free cloud host pilot

Read-only development sandbox: real rea-agents@6.5.0 stdio MCP on an original JavaScript fixture. HTTP GET /, /healthz and /readyz only; no external tool execution, uploads, secrets, customer data or physical appliance commands. Not an always-on guarantee: free Render services can sleep.

Run with Node 24.21: cd services/rea-host && npm ci && npm test && npm start. Render build: cd services/rea-host && npm ci --omit=dev --no-audit --no-fund && npm test. Render start: cd services/rea-host && node server.mjs. NODE_VERSION=24.21.0. Independent review, persistent Mac installations and physical device proof are separate release gates.

Render free 512 MiB plan: set NODE_OPTIONS=--max-old-space-size=384 for the parent and child; otherwise REA can return a memory resource_constraint on even the original fixture. This is a verified free-tier-specific configuration, not a universal REA default. Service can sleep; on cold start /readyz may be 503 until actual MCP verification completes. No arbitrary tool endpoint is exposed.
