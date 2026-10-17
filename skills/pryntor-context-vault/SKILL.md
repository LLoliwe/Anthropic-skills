---
name: pryntor-context-vault
version: 0.1.0
summary: Evidence-backed, scoped, manually approved cross-agent memory handoffs.
---

# Context Vault — R0

## When to use
An authorized agent is continuing work between runtimes and needs approved context only. Never infer permission from a URL.

## Procedure
1. Obtain owner-approved, task-specific vault and scope; do not request passwords, keys or recovery codes.
2. Read only approved exported agent bundle. Verify checksum, provenance and source recency independently.
3. Distinguish prior record approval from current correctness.
4. Propose new facts or changes for review without overwriting version conflicts.
5. Human owner approves and grants agent-read explicitly per record.
6. Report exact tests, remaining blockers, ownership and next steps.

## Boundaries
R0 has no authentication, hosted agent server, Notion API adapter, scheduler, global sync or production deployment. SHA-256 state-chain detects accidental changes but is not digitally signed or protection against malicious local administrators. Use separate OS or connector permissions. Never copy private records into public code or CI fixtures.