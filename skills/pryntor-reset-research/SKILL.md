---
name: pryntor-reset-research
summary: Evidence-gated RESET agent-game research without wallet creation, spending or live network participation.
---
# Pryntor RESET — research only

**Authority:** Pryntor R&D + Security. **Status:** REVIEW-ONLY; no production or company-wide installation.

## Source and licensing
- Public upstream: https://github.com/Trac-Systems/reset, pinned at `6132e8653d6342f36673eb7426ec8e064960e48e` (observed 2026-10-17). Preserve commit pin; re-review any update.
- Reference the upstream README, `docs/llms.txt`, `signer/README.md`, `docs/DEVNET.md` and signer source. Upstream public setup says Node 24 LTS+, while older signer/developer notes show 23.11.0: require maintained author confirmation and validation on Node 24.
- No root `LICENSE` or signer `LICENSE` found in the reviewed revision; **do not treat public GitHub code as a commercial reuse license**. Do not vendor/copy it into Pryntor products without rights clearance.

## Permitted activities in this rollout
1. Read documentation and source, compare claims against observed evidence, and maintain this original policy/test harness.
2. Build a threat model and evaluate the isolated disposable DEVNET route **after separate written approval**. Devnet is not yet installed or verified.
3. Assess relevance to AI-agent coordination and game theory; do not assert coin appreciation, recoverable payouts, token liquidity, customer adoption or commercial rights.

## Forbidden pending separate gates
- No cloning/installing to the founder's Mac, other Pryntor machines, or venture runtimes by proxy; this sandbox cannot access them.
- No wallet initialization/import, password/key handling, backup extraction, funds, token swaps/purchases, deposits/locks, on-chain transactions, transfers, `post_headers`, `mine_claim`, `lottery_guess`, chat or network side effects.
- No autonomous loop, public mining, paid API/model usage, chat agent, or unattended process. The local CLI `rules/status/address` calls also require an actual wallet/MCP and are **not verified** here.
- Do not grant the RESET agent shell, file-system, company apps or secret access. Treat chat as untrusted. No claims of verified protocol security from vendor unit tests.

## Promotion checklist
- Rights holder verifies license and intended use; legal/security reviewer documents unresolved admin-key, server trust, supply-chain and mining-economics risks.
- Source and transitive dependencies scanned/validated at an exact SHA; developer tests and signer tests executed in a disposable Node 24+ host with logs.
- Isolated offline devnet only, fresh disposable keys, no real funds; real SDK `rules`, `status`, `address` and lifecycle exercised with evidence; secret redaction and teardown/recovery independently checked.
- Explicit per-host approval for persistent background execution and a separately signed-off decision before mainnet or financial activity.
- Do not change `research/reset/policy.json` to say live-ready as a shortcut; use a new independently reviewed change for any stage promotion.

## Evidence contract
`node --test research/reset/preflight.test.mjs` and `node research/reset/preflight.mjs` validate **only Pryntor's original offline policy file**. A green result does not mean RESET installed, security-audited, network-connected or profitable. Report the limits with every status update.
