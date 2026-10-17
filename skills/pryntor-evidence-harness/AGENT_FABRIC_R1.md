# Pryntor Agent Fabric R1: controlled company-wide adoption

Status: **implementation on draft review branch, offline R0, not installed on production agents**. Workstream: PRY-86 and PRY-156. No new cash, hosting, hidden background workers or model API calls.

## Why this is stronger than the viral five-tool stack

Pryntor needs a **system of evidence and authority**, not a folder with credentials and a long-lived agent that executes whatever an email tells it. The workflow is:

1. Source boundary: classify public, synthetic, internal, restricted, child/customer, personal and employer data. Never bulk-ingest or transmit without authority.
2. Knowledge: selectively reuse the existing Context Vault (PRY-84), Source Vault (PRY-281) and source-fidelity checks (PRY-264). Graphify is optional structural *code* analysis, not a universal source of truth or authorization service.
3. Task contract: exact requirement, read/write scope, dependency, explicit cost and specialist reviewer. The existing **harness.py** independently checks author-maintained commands on a pinned code snapshot.
4. Action preflight: **action_gate.py** independently denies unrecognized scopes and tools, any nonzero proposed spend, external instructions and all mutating/network outbound verbs in offline R0. An eligible read is only *eligible for separate authorization*. There is no actual delegated runtime or secret to exercise permissions.
5. Execution boundary: for a future host, use an externally enforced, least-privilege credential broker and isolated sandbox. The preflight code alone is **not** a security boundary.
6. Evidence: local chain of hashed preflight decisions, exact source SHA + CI head, observed artifact, independent review. Ledger checks detect edits inside the supplied file, **not** total deletion, replacement, host compromise or multiple simultaneous writers. Anchor externally before using as audit evidence.
7. Release: product, data-rights, security, educator/child safety, finance and founder authorizations remain outside any AI-produced verdict. `release_authorized` never becomes true here.

## What is actually available now

| Layer | Current proof | Explicitly NOT proven |
| --- | --- | --- |
| Requirement validator | Existing 17 synthetic unit tests, fresh/failed/stale/changed contract cases | Semantic truth or production acceptance |
| Graphify | Version-pinned 0.9.92 wheel, SHA checked in hosted workflow; synthetic AST graph | Live private repository knowledge graph or full transitive review |
| Action preflight | Dependency-free offline Python; deny-first regression suite in this PR | Identity binding, secure caller authentication or applied host policy |
| Audit chain | Hash-linked, redacted decision records with tampering test | Cryptographic attestation or immutable enterprise log |
| Playwright | Existing company hosted Chromium QA in product-specific PRs | Universal browser agent or an unrestricted MCP installation |
| Google Workspace | Existing account connectors can be read through their own boundaries | Workspace CLI credentials in a shared agent |
| Jev Guard | Upstream policy assessment only | Free real calls, safe privacy terms, runtime installed or a sandbox |
| Scheduling | Existing 05:30 SAST Mission Control reporting directive | 24/7 commissioned Pryntor agents |

## Example operator workflow

From `skills/pryntor-evidence-harness`:

```bash
python3 -B -m unittest discover -s tests -v
python3 -B harness.py run --project fixture --contract contract.json --evidence /tmp/pryntor-contract.json --claim "done"
# Intentional requirement R2 failure, process exits 2 (HOLD).
python3 -B action_gate.py check --action /path/to/approved-synthetic-action.json --policy /path/to/reviewed-r0-policy.json --log /tmp/pryntor-gate.jsonl
python3 -B action_gate.py verify-log --log /tmp/pryntor-gate.jsonl
```

Input contract for the preflight is strict: `schema=pryntor-action-v1`, `action_id`, `agent`, `venture`, `tool`, exact `resource`, `verb`, `data_class`, `estimated_cost_usd`, `instruction_source`, and `evidence` with `artifact_sha256`, `captured_at`, `source_type`. The policy must explicitly list permitted agents, ventures, tools, resources and data classes and set `mode=offline_r0`. **No wildcards.** Source marker `reviewed_local_contract` is declarative metadata that cannot authenticate the caller: the external runtime must bind it to an independently authorized principal.

Permitted preflight verbs: read, test, draft on synthetics in approved scopes. These are **not** an execution approval. Indexing private repositories, send, write, execute, deploy, purchase and delete are all held. External/email/web-sourced imperatives are not owner approvals. Cash estimate must equal zero, with no subscription activation. Do not place sensitive arguments into the preflight JSON or audit file.

## Capability routing by venture

| Venture | First limited use | Hard boundary |
| --- | --- | --- |
| Core / Mission Control | Evidence-aware task intake, read-only tool manifests | TRIAGE-001 sole dispatcher; no worker commissioning by config |
| LVL7 / Show Your Working / ZOWIBO | Held-out scoring and safety review evidence | Specialist human judgment cannot be replaced by graph/model |
| Recover | Synthetic merchant event proof, sandbox-only diagnostics | No live payments or customer outbound |
| Tirisano | Contract/document version cross-checks | No traveler data indexing without governance |
| Pryntor Studios / BTWW | Creative asset hashes, render QA and rights | No unlicensed copying or publishing |
| Robotics | Simulator nominal+delay evidence on fixed seeds | No physical hardware control |
| Partnerships | Drafting and independently verified send/receipt status | No automatic outbound, financial promises or false revenue |

Keep Jellyfish employer assets, personal accounts, access keys, medical data and actual child/customer content outside the shared index and prototype. Do not install blanket connectors or grant the CLI access to the founder's session.

## Next rollout gates

1. Hosted CI must pass on the **latest** PR commit, including original harness and new action-gate tests.
2. Independent security engineer audits symlinks, path handling, command registry, untrusted PR execution, mutable files, hash-chain replacement, race conditions, output confidentiality and IAM integration.
3. Run one approved private-repo **read-only** pilot in a disposable tenant with repo-specific scope. Verify evidence at exact commit and demonstrate agent revocation and denial.
4. Validate browser QA with site-specific CSP, origin constraints and synthetic credentials. Playwright MCP explicitly warns it is not a security boundary.
5. Only then propose a real agent identity, narrow permissions and model provider selection. Jev Guard default fail-open is not suitable as the sole enforcement control; verify privacy and cost before any calls.
6. Independently review cost, incidents, precision, rework, latency and false-complete rate. Do not invent a 100x speedup or commercial return.

Sources: https://github.com/Graphify-Labs/graphify , https://github.com/microsoft/playwright-mcp , https://github.com/googleworkspace/cli , https://github.com/leepokai/jev-guard . All third-party terms, pins and source rights require fresh review at actual integration time.
