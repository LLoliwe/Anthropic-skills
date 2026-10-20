# Pyrum OMEGA R1 | Offline handoff acceptance proposal

A self-contained, source-driven proposal for safely connecting an **existing** ChatGPT Dot to **existing** Pryntor fleet work. This is NOT another agent/runtime/dispatcher, does not authenticate to any service, and cannot tell whether Pyrum has received a task.

```bash
python3 -m unittest discover -s tools/pyrum-handoff/tests -v
python3 tools/pyrum-handoff/preflight.py tools/pyrum-handoff/examples/safe-public-research.json
```

The validator emits only `HOLD`, `INVALID`, or `REVIEW_ONLY`, never `APPROVED`, `RUNNING`, `CONNECTED`, or `RELEASED`. It is deliberately dependency-free and offline. Admitted R0 tasks still need genuine TRIAGE-001 ownership, scoped permissions, explicit approvals when necessary, independent end-to-end evidence and release gates.

- `docs/pyrum-omega/RESEARCH-DECISION.md`: current primary sources and technical evaluation.
- `docs/pyrum-omega/PYRUM-BOOTSTRAP.md`: exact manual Dot setup and first test message.
- `skills/pryntor-pyrum-omega/SKILL.md`: optional reusable scoped guidance.
- `tools/pyrum-handoff/preflight.py`: deny-by-default *metadata-only* checks.
- `tools/pyrum-handoff/tests/test_preflight.py`: 37 synthetic local negative/positive tests.

**Not covered:** provider authentication, genuine runtime ACK, cryptographic proofs, token binding, independent workflow execution, code QA outside these files, telemetry export, persistent schedules, POPIA certification, GitHub CI or new infrastructure. Keep zero unapproved spending and current security and IP release holds intact. Existing Pryntor trackers: PRY-63/81/83/84/86/96/209/309.