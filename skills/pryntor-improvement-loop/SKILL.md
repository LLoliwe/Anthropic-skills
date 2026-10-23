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

## Founder probation: finish the user journey, not merely the task (18 Oct 2026)

Before a builder agent starts, the accountable owner must pin one **outcome contract** to the existing GitHub/Linear item: exact source commit and failing build; the founder's intended user experience in plain words; current observed failure; the smallest reproducible start-to-finish journey; independent acceptance tests and negative cases; original creative/brand assets and rights; device/browser matrix; R0 spend ceiling; and stop/rollback conditions. No duplicate issue or fresh prototype if a canonical version exists.

Only delegate bounded slices when they reduce measured time-to-working-output. A lead builder integrates the product, a domain reviewer checks art/gameplay or specialist safety, and a separate verifier checks tests and user-visible behavior. No worker may grade its own completion, silently alter benchmark fixtures, bypass failed CI, self-approve a release or claim that another agent ran without an execution receipt.

For games, **Play must enter active gameplay** in the exact requested version. Exercise movement, threat/chase or challenge where specified, meaningful interactions, scoring/goal, end state, restart, rotation, no overlay interception, real animation/frame change, touch and keyboard controls. Check responsive browser tests and physical target hardware separately. For ZOWIBO, source-faithful original 3D character continuity and a human art lead's editorial judgement are mandatory; generic 2D or screenshots do not satisfy that brief.

For films, validate actual audiovisual footage and motion, not static slides. For enterprise software, exercise the real permitted end-to-end business workflow instead of counting mock dashboards. Preserve protected tests, held-out cases and named human verification. A working browser simulation is not real Safari, a procedural model is not a Unity/Blender native production build, and a drafted email is not an outbound conversion.

**Handoff must include** exact SHA, runnable preview/build location, what the user can now do, explicit PASS/FAIL/NOT RUN per device and acceptance test, real bug evidence, source rights/creative review, independent reviewer, cost, and decision `REVIEW_REQUIRED` / `BLOCKED` / `RELEASE_CANDIDATE`. A file existing or passing synthetic tests alone may never be called shipped. Keep fixed requirements; if the founder says it looks wrong or the button does nothing, treat that as a failing acceptance case and iterate on the same canonical version.

The R0 controller now verifies on disposable copies and requires a real source change before issuing a review-only patch. Its new negative-case suite needs exact-head execution and independent security review. It does not itself supply a live model, a complete artistic evaluator, actual device access, or secure network sandbox.

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