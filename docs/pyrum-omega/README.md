# Pyrum OMEGA R1 | Scoped handoff gate

**Purpose:** support first verified handoff to the existing Pryntor Dot through the existing TRIAGE-001 and PRY-83 ledger, without creating a competing agent fleet.

## Source available on this draft branch

- tools/pyrum-handoff/preflight.py: static, stdlib-only advisory validation, no network.
- tools/pyrum-handoff/tests/test_preflight.py: 42 synthetic positive/adversarial checks, including false ACK, false connection, privileges, spend and input validation.
- tools/pyrum-handoff/examples/safe-public-research.json: illustrative proposed work only, NOT assigned to an agent.
- skills/pryntor-pyrum-omega/SKILL.md: explicit work/identity/security/quality policy for separately authorized clients.
- .github/workflows/pryntor-pyrum-handoff-r1.yml: isolated test job with no secrets.
- tools/pyrum-handoff/README.md: reproducible commands.

Do NOT put live prompts, customer content, real credentials or confidential evidence in the public repository. Deeper company findings and activation procedures remain controlled in the founder's private work package/Linear source-of-truth.

## Real-world acceptance remains open

1. Actual Pyrum Dot signed into an authorized account can read a harmless one-time challenge posted to existing [PRY-96](https://linear.app/pryntor/issue/PRY-96).
2. Distinct actor permissions and Dot task ID/URL are independently verified, not inferred from a Slack mention.
3. TRIAGE-001 confirms one owner/lease, rejects duplicate/fake ACK, then approves a narrowly scoped task if authorized.
4. Pyrum produces a genuine linked internal artifact, separate verifier reopens and checks it; no outgoing communication, new spending, or release.
5. If a connector is unavailable, record NOT CONNECTED. This software cannot itself bind a live Dot, grant rights or execute tasks.

Release and production remain HOLD. A hosted Python unit suite is not an audit of external provider authorization or sandbox isolation.
