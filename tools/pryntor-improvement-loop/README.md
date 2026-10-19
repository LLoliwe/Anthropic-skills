# Pryntor bounded improvement loop R0

Original dependency-free Python 3.11+ offline harness. Start with `python3 -m unittest discover -s tools/pryntor-improvement-loop -v`.

* Default mode: validate inputs and emit `DRY_RUN`; never run a candidate or verifier.
* `--execute`: run a trusted, locally configured candidate and independently configured verifier in an ephemeral copy of the staged source tree. Only use with an **external OS sandbox and blocked egress** for untrusted executable agents.
* `--out` must point to a new folder outside the source. It produces `events.jsonl`, `receipt.json` and a review-only text `candidate.patch` on successful measured correction. Original source remains unchanged.
* Preserve positive and negative tests, all attempt receipts, the exact base revision and a named human reviewer. The example verifies protected file bytes but cannot prove the complete correctness, independence, or security of the test itself. No automatic PR or merge.
* Process timeouts and retry counts are bounded. Budget guard is R0 procedural: the controller provides **no metered API, GPU or credential integrations**. Running arbitrary agent commands outside an OS sandbox could still make network requests or incur costs. Do not do that.
* For actual development, seed isolated fixtures from a reviewed pull-request head, run existing tests read-only, and apply generated patches only after human diff review on a branch.

Failure outcomes include `BLOCKED_VERIFIER_MODIFIED`, `BLOCKED_BASELINE_VERIFIER_MODIFIED`, `STOPPED_NO_PROGRESS`, and `STOPPED_ATTEMPT_LIMIT`. `CANDIDATE_VERIFIED_REVIEW_REQUIRED` is not an authorization to deploy.

## Founder-level work selection and receipt gate (19 Oct 2026)

`founder_dispatch.py` is a **separate original, deterministic, stdlib-only operator aid**, not a model or an unattended service. It accepts an already validated JSON list of EXISTING Pryntor issues and ranks only fresh, reproducibly failing, unclaimed, reversible, R0-spend internal work with an exact repo/source SHA, functional acceptance and a negative case. Critical security, ZOWIBO user-journey defects and corporate site/first-cash blockers take precedence over task volume. Stale/repeated/foreign/claimed/paid work is rejected. Metadata is **caller-provided** and cannot itself prove authenticity or acquire a lock.

```bash
python3 tools/pryntor-improvement-loop/founder_dispatch.py --mode select --input /reviewed/current-issue-snapshot.json
python3 tools/pryntor-improvement-loop/founder_dispatch.py --mode evidence --input /reviewed/worker-receipt.json
```

`--mode evidence` checks revision difference, immutable artifact hash, functional and adversarial command receipts, browser evidence for UI products, and review-declaration completeness. It NEVER authenticates logs, confirms a real device, grants release or spends funds. An apparently complete manifest returns `READY_FOR_EXTERNAL_RECEIPT_CHECK`, NOT `SHIPPED`. The real next actor must independently compare GitHub SHA, actual CI/browser/media behavior, human review and permissions with live provider sources before approving any code change. Use `python3 -m unittest discover -s tools/pryntor-improvement-loop -v` for the local pure/fixture-only regression suite.

**Commissioning state:** PRY-309 draft PR. This feature is not connected to live Linear as a scheduled worker, to remote Hark/Pyrum/Kimi/Krea runtimes, nor to a verified sandbox. The existing ChatGPT Product/Robotics/Studios hourly task received an updated founder-level production and no-spend contract; that schedule alone is not an independent agent ACK or acceptance proof. Do not enable `loop.py --execute` with untrusted scripts until genuine no-egress OS sandbox, protected evaluations, independent security review and an actual tested product pilot are verified.
