# Pryntor Jev decision evaluation R0

**Scope: offline synthetic fixtures only. Not live Jev, not live customer data, not release authorization.**

Owned by Pryntor. Canonical engineering ticket: [PRY-307](https://linear.app/pryntor/issue/PRY-307/jev-eval-r0-offline-typed-decision-adapter-synthetic-corpus-and-safety). Partnership campaign: [PRY-305](https://linear.app/pryntor/issue/PRY-305/partner-typesafe-001-sponsored-jev-evaluation-60-day-no-card-pilot).

## Proof

- Original Python 3.10+ stdlib-only program
- 3 decision-only queues: acceptance diagnostics, partnership triage, creative/technical QA
- 60 hand-curated synthetic fixtures; 42 development and 18 reserved. These were not independently labeled or blinded.
- 40 unit/adversarial tests, and path-scoped hosted GitHub Actions workflow.
- Model outputs can only select internal queues; no sending, payments, publishing, deleting, secret use, production change, customer data access, or other side effects.
- Input is a synthetic state map only. State input is restricted to a fixed per-workflow boolean allowlist and known policy flags. This is still not full DLP, secret scanning, sandbox isolation or permission control.

## Run (no API key or packages needed)

From the directory containing this file:

    python3 -B make_fixtures.py
    python3 -B -m unittest discover -s tests -v
    python3 -B decision_pilot.py benchmark
    python3 -B decision_pilot.py request-preview --id DI-03 --model jev-1.13.0

The request-preview prints candidate JSON; it **does not** contact Jev. The answer validator is for a proposed Jev-like raw shape, not proof that the live API returns that exact wrapper. The shape must be independently reconciled with current TypeSafe SDK and live API evidence after separate authorization.

## Important limits

- The 100% fixture agreement is manufactured by design, not measured predictive model accuracy.
- The label 'holdout' simply identifies 18 separately designated fixture cases, not an independently sourced unseen evaluation.
- The 18/18 policy holds and 7 added schema regression cases demonstrate only bundled negative behavior, not complete safety.
- The GitHub Actions job executes synthetic code in a disposable runner; it does not deploy any Pryntor worker.
- No production release, payment, automatic communication or independent security approval is conferred.
- Company-wide rollout must wait for independent technical/security review, a genuinely blind labeled holdout, partner entitlements, privacy and billing checks, and measured vendor decision quality.

**Source and negotiation background:** https://typesafe.ai/ ; https://docs.typesafe.ai/introduction/quickstart ; https://typesafe.ai/legal/mca .

No credentials, personal email, client/employer data or customer source files belong in this repository. No new spending or Jev calls are authorized by this PR.
