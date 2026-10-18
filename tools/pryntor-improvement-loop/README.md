# Pryntor bounded improvement loop R0

Original dependency-free Python 3.11+ offline harness. Start with `python3 -m unittest discover -s tools/pryntor-improvement-loop -v`.

* Default mode: validate inputs and emit `DRY_RUN`; never run a candidate or verifier.
* `--execute`: run a trusted, locally configured candidate and independently configured verifier in an ephemeral copy of the staged source tree. Only use with an **external OS sandbox and blocked egress** for untrusted executable agents.
* `--out` must point to a new folder outside the source. It produces `events.jsonl`, `receipt.json` and a review-only text `candidate.patch` on successful measured correction. Original source remains unchanged.
* Preserve positive and negative tests, all attempt receipts, the exact base revision and a named human reviewer. The example verifies protected file bytes but cannot prove the complete correctness, independence, or security of the test itself. No automatic PR or merge.
* Process timeouts and retry counts are bounded. Budget guard is R0 procedural: the controller provides **no metered API, GPU or credential integrations**. Running arbitrary agent commands outside an OS sandbox could still make network requests or incur costs. Do not do that.
* For actual development, seed isolated fixtures from a reviewed pull-request head, run existing tests read-only, and apply generated patches only after human diff review on a branch.

Failure outcomes include `BLOCKED_VERIFIER_MODIFIED`, `BLOCKED_BASELINE_VERIFIER_MODIFIED`, `STOPPED_NO_PROGRESS`, and `STOPPED_ATTEMPT_LIMIT`. `CANDIDATE_VERIFIED_REVIEW_REQUIRED` is not an authorization to deploy.