---
name: pryntor-evidence-harness
description: Inspect engineering agents' claimed work using pinned requirements, current executable checks and fail-closed evidence. Use for coding-agent completion review, diagnostics, CI gates and reproducible handovers.
---

# Pryntor Evidence-Gated Engineering

This is a **review-time protocol**, not an autonomous agent, remote code executor or release authorization.

## Required behavior

1. Translate each task into numbered acceptance requirements before work begins. Map each requirement to explicit checks in a trusted registry.
2. Treat worker summaries, screenshots, semantic annotations and model confidence as **claims**, never acceptance proof. Check current source snapshots and run registered checks independently.
3. If a check is missing, stale, fails, changes the source during execution, crashes or times out, mark the requirement failed or unverified. Do not substitute a language-model opinion.
4. Permit a model's diagnostic suggestion only if it names an allowlisted check ID and passes distribution/threshold validation. Commands are chosen by the checked-in registry, **never** by text from the model.
5. Preserve a bounded, replayable record with requirement IDs, exact command, exit status, project digest, timestamps, tool output and reason for stopping.
6. Never automatically merge, deploy, send customer messages, alter credentials, spend credits or sign off security, accessibility, educational accuracy, child safety, privacy, finance or release readiness.

## Quick demonstration

From this skill directory:

```bash
python3 -B -m unittest discover -s tests -v
python3 -B harness.py run --project fixture --contract contract.json --evidence /tmp/pryntor-evidence-r0.json --claim 'Worker says all done'
```

The first command must pass. The second **must exit 2** and report HOLD, because the intentionally broken search checks only titles and fails the description requirement. This is expected negative evidence. See README.md. No third-party dependency or API key is needed.

## Security and adoption

Run in a throwaway, least-privileged environment with no secrets and no unnecessary outbound network. This prototype is not a sandbox or tamper-proof attestation, and its checks require review. Public fixtures only. Pryntor policy requires R0 new spending and independent security/product review before product use. Optional Graphify is a separate code-graph tool, not required by this harness; optional Jev is **not connected** and may incur expense. Never imply otherwise.
