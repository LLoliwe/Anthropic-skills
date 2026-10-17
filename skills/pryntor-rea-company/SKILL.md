---
name: pryntor-rea-company
description: Route lawful, authorised shipped-artifact and runtime investigations across Pryntor to its installed REA skill; require evidence, permissions, independent QA and zero-new-spend approval.
---

# Pryntor REA — group operating overlay

**Status:** company routing and acceptance policy, **not** a substitute for the official `reverse-engineer-anything` skill or proof of live REA MCP connection.

## Source and existing installation

- Official upstream: https://github.com/morluto/rea (MIT for REA-authored code; providers and targets have separate terms).
- Company record PRY-15: official REA skill and six references were installed to a separate persistent Skills workspace on 16 October 2026 at commit `977c306`; npm `rea-agents@6.5.0` CLI startup verified. Existing Codex MCP registration was **missing** at the last recorded doctor check.
- Pinned initial server package for this rollout: `rea-agents@6.5.0`. Before upgrading inspect package/release differences; do not silently mix development-main skill metadata with older server tools.
- Real MCP readiness gate: a successful JSON-RPC `initialize` response, `notifications/initialized`, nonempty `tools/list` from the actual REA process, and **a target-appropriate analysis** with verifiable Evidence. The accompanying probe tests only the first two substantive checks.
- Node.js requirement: 22.19+, 24.11+, or 26+ (not arbitrary Node 22/24).

## Route ONLY eligible problems

Use REA when source is missing or insufficient and a legitimate task requires shipped binaries, JavaScript/Electron bundles, .NET assemblies, authorised browser/runtime behaviour, firmware or saved device/protocol traces. Prefer direct source inspection for full open-source repos.

- Core / Mission Control / Web / Mobile / Games: authorised package-debugging, Electron/JS IPC mapping, interoperability, regression comparison.
- Robotics / device lab: *owned test hardware* and consented firmware or previously captured IR/RF traces; start offline and isolated. Never infer that a hardware controller is operational from a demo UI.
- Studios / BTWW / AFTERLIGHT: troubleshooting legitimately licensed production tools and artifact packaging; no protected-asset cloning.
- LVL7 / Show Your Working: authorised static education-software diagnostics, respecting child data and educational-review gates.
- Tirisano: explicitly approved internal travel-client diagnostics using redacted artifacts; no traveller PII in public repos or transcripts.
- Pryntor Recover / Finance / Security: investigation only against owned code or consented test instances; never production payment controls, credentials or client systems by default.

## Fail-closed execution contract

1. Open an existing product Linear issue, identify asset OWNER, rights/permission, exact target and read-only versus runtime scope, and sign-off for any device or account state changes.
2. Log SHA-256 of input, origin/provenance, relevant OS/CPU architecture, exact REA npm version and provider version, isolated execution environment, expected cost (R0).
3. Prefer offline static triage. Runtime instrumentation, capturing real network traffic, firmware extraction, third-party software and real hardware require separate explicit authorisation and safeguards.
4. Run `python3 scripts/rea_mcp_probe.py --self-test` for the synthetic probe test; for a **real** local host with supported Node and package acquisition access, run `python3 scripts/rea_mcp_probe.py -- npx -y rea-agents@6.5.0 mcp`. Neither is a target-analysis result.
5. If client registration is missing: inspect `npx -y rea-agents@6.5.0 doctor --client codex --json`, then `setup --client codex --dry-run --json`, review file paths/backups and approve scope before `setup --client codex --yes`. Restart and enumerate active tools. Never overwrite an unrelated MCP server.
6. For a first real case, use an **original, non-sensitive, disposable JavaScript/Electron fixture** with `npx -y rea-agents@6.5.0 analyze-javascript-application /absolute/path/to/fixture --json`. Verify tool output fields and limitations independently; the CLI run does **not** prove MCP registration.
7. Keep observation vs inference vs unknown separate. Compare a reconstructed original implementation to a held-out oracle/test and independent reviewer evidence before any claim of parity.
8. No DRM, anti-cheat or licence bypass; no unauthorised access, protected IP copying, surveillance or release of private firmware. Respect POPIA, client contracts, target licenses and upstream responsible-use policy.
9. Do not pay for Hopper, Ghidra hosting, cloud compute, third-party access or devices without documented price and founder approval. Ghidra is independently available software; REA setup does not install it.
10. Ship only after human QA, security/safety checks, source-to-test traceability and real CI evidence pass. The branch/PR is a pilot until these checks pass.

## Evidence ledger

For EACH venture target append: date | venture | issue | exact target digest | rights | REA/version/provider | observed command | redacted Evidence | tests/holdouts | reviewer | spend | status (QUEUED / PROBE-ONLY / ANALYZED / ACCEPTED / REJECTED).

**Current baseline 17 Oct 2026:** official skill saved separately, REA CLI previously started, live MCP and authentic target analysis **unverified**. This repo's probe is independent plumbing, not proof of commercial functionality.
