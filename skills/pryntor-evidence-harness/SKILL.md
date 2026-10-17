---
name: pryntor-evidence-harness
description: Use for Pryntor tasks requiring independently checked requirements, controlled diagnostics, reviewable evidence, and a deterministic HOLD or contract-satisfied decision.
---

# Pryntor Sentinel V2: A test is evidence. A worker claim is not.

This reusable skill never overrides TRIAGE-001's sole dispatch, ACCESS-01 security authority, the product owner, code review or founder-gated publishing.

1. State the requirement precisely and map it to a cheap, independently executable mandatory check. Keep acceptance criteria and tests in code-owner-controlled files, not worker instructions alone.
2. Select a disposable non-sensitive source copy. Optionally map its architecture with pinned Graphify code-only mode **after** reviewing package provenance and target permissions. Structure graphs do not prove correctness.
3. Inspect the contract and use `python3 -B harness.py digest --contract contract.json` to calculate its canonical SHA-256. A trusted reviewer or protected CI configuration, NOT the agent-under-test, must pin the approved value. Do not approve every digest dynamically in the same untrusted job.
4. Run `python3 -B -m unittest discover -s tests -v`, then run `harness.py run` with `--approved-contract-sha256`, an evidence path outside the project, and optionally `--html` for a static review page. Never use a privileged runner on untrusted code.
5. Missing, stale, mutating, crashing, timed-out, modified or failing evidence is HOLD. A blank or forged report is not a success. Never promote Jev/Noul/Choice confidence into release acceptance.
6. If a diagnostic is useful, permit only a registered, human-reviewed command. Avoid indefinite retries; surface a minimal repro and require new source snapshot and independent acceptance after any repair.
7. Use evidence to request independent code/security/QA review. A passing contract is not a release. `release_authorized` remains false even after all green tests.
8. Measure false-complete, held-out acceptance, lead time to independently verified fixes, interventions, actual provider spend, and bank-settled cash. Do not report multiplicative gains or sales from benchmark demos.

Refer to README.md, SECURITY.md, ROLLOUT.md and PROVENANCE.md. The sample fixture intentionally fails description search. Jev isn't connected. Graphify has only been tested against synthetic code in disposable hosted CI.