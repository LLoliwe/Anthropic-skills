# Pryntor Context Vault — R0 portable context handoff

Original, dependency-free reference implementation for **portable, scoped, provenance-linked agent memory**, using Soul, Memory, Artifacts, Skills and Lessons. Related company issue: https://linear.app/pryntor/issue/PRY-84/fleet-03-verified-shared-memory-permissions-immutable-handovers-and

**Security notice:** This is an **offline R0 prototype**, not a production vault, cross-application SSO, security boundary, hosted MCP, Notion sync integration or live nightly job. This repository contains no company records or credentials. Local folders must be secured by the OS and owner. Reviewer strings are not authenticated identities. Secret scanning is best effort, not data-loss prevention.

## Run

    python3 -m unittest discover -s tests -v
    python3 vault.py --root /tmp/portable-vault propose --key sample:lesson --kind Lesson --scope Company --sensitivity Internal --content 'Verify releases using latest-head evidence' --source local:synthetic-demo --owner demo-owner
    python3 vault.py --root /tmp/portable-vault approve --key sample:lesson --expected-revision 1 --reviewer demo-reviewer --agent-read
    python3 vault.py --root /tmp/portable-vault export-agent --scope Company --output /tmp/agent-company.json
    python3 vault.py --root /tmp/portable-vault verify
    python3 vault.py --root /tmp/new-agent-vault import-handoff --input /tmp/agent-company.json --owner receiving-agent

Imports are quarantined as proposals, requiring review before re-export; updates require exact expected revision. Scope-mismatched, restricted, unapproved and non-agent-readable records are excluded from outgoing bundles. Exports carry a SHA-256 checksum and state changes are hash-chained.

## Architecture and release gates

- Notion: private visual R0 pilot in a personal workspace, not automatically connected to this code.
- Runtime: local vault.json and JSON agent handoff bundles.
- R1: verified private Notion read/write adapter, scoped authenticated permissions, collision handling, monitoring, scheduled sync and restore.
- R2: independent read-after-write across two authorized clients, access revocation and security/backup acceptance.

A scheduled CI unit test is **not** a live data sync. Never upload actual vault data to public GitHub.