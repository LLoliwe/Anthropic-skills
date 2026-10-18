---
name: pryntor-improvement-loop
version: 0.1.0
summary: Offline, bounded, independently verified iteration with immutable evaluation inputs and human-only promotion.
---

# Pryntor improvement loop R0 | group engineering policy

Use for a narrowly scoped, reversible engineering task with an executable, separately owned acceptance test. Discover, Plan, Execute, Verify, Iterate. The same governance pattern applies selectively to Studios, Recover, LVL7, SYW, Robotics, BTWW and other teams with domain-specific reviewers. It is not a blanket AI agent deployment or a substitute for expertise.

## Before running
1. Confirm exact task owner, authorised repository, project-local brand/security constraints and fixed objective. Identify baseline, test inputs, expected failing test, separate verifier owner, allowed changes and explicit human promotion gate.
2. Confirm all runner commands are operator-reviewed offline binaries/scripts. No agent may rewrite its own evaluator or `AGENTS.md`. Never use a private dataset or secrets in a public example or GitHub artifact.
3. Zero NEW spend, no cloud/GPU/API procurement, no usage-based calls, no credentials, no external access by default. Work must use a separately configured and verified OS/container sandbox with blocked egress for untrusted agent commands. The Python controller itself does **not** provide OS isolation, secure credential containment or network enforcement.
4. Existing verifier must fail for a valid reason. If baseline already passes, stop rather than generating changes. Define measurable acceptance and domain-specific negative tests up front.

## Execute R0 controller
Use `tools/pryntor-improvement-loop/loop.py` with an approved JSON task specification. The controller validates commands as argv arrays (no shell), runs on an ephemeral copy, caps attempts (at most 5) and each command (at most 60 seconds), records output hashes and verifier integrity, returns a review-only `candidate.patch` and retains an experiment ledger. No automatic merge, deployment, runtime scheduling or customer operations.

**Examples:**
```
python3 -m unittest discover -s tools/pryntor-improvement-loop -v
python3 tools/pryntor-improvement-loop/loop.py --spec /approved/task.json --root /approved/safe-fixture --out /tmp/pryntor-loop-001
python3 tools/pryntor-improvement-loop/loop.py --spec /approved/task.json --root /approved/safe-fixture --out /tmp/pryntor-loop-002 --execute
```

JSON specification:
```
{
  "goal": "Make the fixed acceptance suite pass",
  "candidate_argv": ["python3", "candidate.py"],
  "verify_argv": ["python3", "verify.py"],
  "protected_files": ["verify.py"],
  "max_attempts": 3,
  "timeout_seconds": 20
}
```

A real agent adapter may replace `candidate.py` only after checking provenance, external access, sandbox isolation, token caps and entitlements. A stringified shell pipeline is rejected. The verifier should be an independently maintained deterministic test, not the agent's own opinion. Include human review of requirement completeness and independent held-out checks before adoption.

## Record and decide
Preserve `events.jsonl`, `receipt.json`, optional `candidate.patch`, exact base commit, dependency lockfiles, test logs under controlled private storage, runtime cost evidence and reviewer identity. Unredacted outputs are not persisted by this example controller, only hashes. Absence of a `candidate.patch` is not a passing run. A verified candidate means **review required**, not production-ready. Record failures, no-progress stopping, timeouts and verifier tampering. Never claim a model/provider was invoked unless receipts prove it.

## Venture gates
- Engineering: exact-head CI, negative regression tests, secure coding review, authorized PR.
- Studios / ZOWIBO / BTWW: real frame/audio render checks plus original IP, rights, accessibility, distinct brand and human editorial QA. Automated tests cannot decide artistic quality.
- Recover / revenue: sandbox-only merchant isolation, opt-outs, deterministic replay, measured outcomes and independent privacy/security sign-off; never transact or message customers automatically.
- LVL7 / SYW: held-out learning goals, expert educator approval, child-safety and assessment integrity checks.
- Robotics / Lens: simulation-only isolated tests, latency safety cases and human safety approval before physical interaction.

## Disallowed status claims
A reference skill in a repository is not a live agent, a scheduled workflow, an installed skill in every venture or production proof. This R0 does not integrate Jev or Furies as active runtimes; both may inform proposals, but independent verification remains decisive. Track per-repo installations, CI runs, measured real experiments and release approvals separately in Linear. For scientific discovery use stricter PRY-199 held-out protocols.