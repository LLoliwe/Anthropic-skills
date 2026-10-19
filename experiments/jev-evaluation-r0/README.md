# Pryntor Jev decision evaluation R0

**Scope: offline synthetic fixtures only. Not live Jev, not live customer data, not release authorization.**

Owned by Pryntor. Canonical engineering ticket: [PRY-307](https://linear.app/pryntor/issue/PRY-307/jev-eval-r0-offline-typed-decision-adapter-synthetic-corpus-and-safety). Partnership campaign: [PRY-305](https://linear.app/pryntor/issue/PRY-305/partner-typesafe-001-sponsored-jev-evaluation-60-day-no-card-pilot).

## Proof

- Original Python 3.10+ stdlib-only program
- 3 decision-only queues: acceptance diagnostics, partnership triage, creative/technical QA
- 60 hand-curated synthetic fixtures; 42 development and 18 reserved. These were not independently labeled or blinded.
- Automated unit/adversarial, official-envelope and skill-guided pilot tests, with a path-scoped hosted GitHub Actions workflow. Verify the exact count from the latest head's CI.
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

## Partner handoff and official SDK contract

Public evidence-backed contact dossier: [PARTNER_ONE_PAGER.md](PARTNER_ONE_PAGER.md).

New `tests/test_official_shape.py` documents the authoritative TypeSafe raw JSON envelope (`model`, `answers`, `type`, `choice`, `confidence`, `probabilities`), based on the official [TypeSafe quickstart](https://docs.typesafe.ai/introduction/quickstart). All test values are synthetic. The adapter is not a real API client, and authorization, response provenance, billability, commercial entitlements and model calibration are not demonstrated. The bundled samples are only contract-shaped fixtures.

## R1: apply the installed TypeSafe skill to Partnerships triage

The official project-local skill is available under .agents/skills/typesafe-ai/SKILL.md. The new R1 file typesafe_pilot_r1.py is a concrete first implementation for internal partnership opportunities.

Live TypeSafe docs consulted on 18 October 2026: https://docs.typesafe.ai/llms.txt ; https://docs.typesafe.ai/api ; https://docs.typesafe.ai/primitives/choice ; https://docs.typesafe.ai/primitives/noul ; https://docs.typesafe.ai/confidence ; https://docs.typesafe.ai/sdk/python

R1 reads *fictional* supplier excerpts only. Deterministic rules handle known payment, auto-billing, private data, and identity restrictions before any planned model inference. It builds an UNSENT official-structure request using one Choice for internal queues and two independent Nouls for no-card and no-auto-conversion claims. Noul probabilities are unverified claims, not accepted supplier terms.

All R1 response tests use mock values, never live Jev. Any output is internal-review-only or HOLD. The script has no provider connection, credentials, network code, email sender, payments, publishing, deployment, or autonomous release. A fictitious case with written terms still cannot be marked as externally verified.

Run locally from experiments/jev-evaluation-r0:

    python3 -B typesafe_pilot_r1.py preview --case partner-free-claims
    python3 -B typesafe_pilot_r1.py replay --case partner-free-claims
    python3 -B -m unittest discover -s tests -v

No live model performance, cost, latency or accuracy is measured by these sample runs. Before a separate authorized live adapter: verify sponsored no-card credits and zero auto-conversion, establish approved secret management, independently label an unseen evaluation set, assess privacy and commission an independent engineering/security review. Do not allow any model output to authorize external effects.

## R2: Coding-agent harness design, implemented as an offline opt-in example

Studied the [12-page independent Jev Engineering synthesis](https://jevforagents.com/media/Jev-Engineering-for-Coding-Agents.pdf) dated September 2026. It is **not** a TypeSafe-endorsed technical specification and does not prove 200x end-to-end speed or 400x end-to-end cost reduction.

New `coding_harness_r2.py` and `tests/test_coding_harness_r2.py` extend the **same PRY-307 draft PR**, without modifying any real game or agent runtime:
- Addressable fictional evidence chunks with query-dependent hide / short / long / full visibility. Every policy chunk and explicitly required evidence ID is retained in full, or the context proposal HOLDS for insufficient budget. The supplied summaries are authored evidence, not an unverified auto-compression.
- Fixed registry of three read-only/request-only tool hints and single-tool schema disclosure; there is no actual tool runner.
- Advisory preflight checks the proposed command, declared paths and caller-provided script text. Malicious scripts and sensitive path candidates are rejected, unknown commands escalate, and even read-only candidates do not receive runtime authorization. This is **not** a security sandbox, parser, filesystem inspection, credential broker or permission enforcement system.
- Paper's Opus/Sonnet model-handoff arithmetic computed using Decimal, with a trust override; it never chooses a real provider or makes a charge.

Run from `experiments/jev-evaluation-r0`:

    python3 -B coding_harness_r2.py demo
    python3 -B coding_harness_r2.py tools
    python3 -B coding_harness_r2.py economics
    python3 -B -m unittest discover -s tests -v

Local, pre-commit offline result: 23/23 new unit tests passed. The fictional ZOWIBO Safari-touch context sample reduced a **whitespace word-count proxy** from 119 to 69 words (42% fewer words in that one illustrative context). This is not a tokenizer measurement, a Jev model accuracy evaluation, an actual coding speedup, nor a change to ZOWIBO's game. Exact-head GitHub CI must be verified independently after commits.

No live Jev inference, customer data, cost entitlement, provider payment, external outreach, production change or security approval has occurred. Next permitted pilot is an **opt-in read-only shadow comparison** against a real preapproved failing regression, with mandatory facts fixed in advance, a blind retrieval/recall evaluation, total tokens+wall time+task success+cost measured, and independent QA. Advance only with owner and security sign-off. Keep this PR draft/unmerged.
