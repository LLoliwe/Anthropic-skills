# WTB&W | Pryntor competitive evidence and evaluation contract

**State: proposed central standard in a draft review PR.** Applies by explicit opt-in, then separately verified per venture, not automatically enforced at runtime.

## Two different scorecards
**Discovery scorecard:** leader / exact user job / original source URL / publisher / source check date / firsthand artifact / observable mechanism / why it works / counterexamples / direct or lateral / competing weaknesses / rights notes / original Pryntor advantage. Label each source A (independently repeatable or verified direct task), B (credible observable demo/spec), C (marketing, awards, opinions, unverified leaderboard). A category can have different leaders depending on the job.

**Proof scorecard:** baseline, candidate and testable references, same fixed held-out fixture, same cost/time/environment, frozen evaluator, exact version, raw scores + error cases, scored by independent humans or deterministic method. A reference that cannot be tested like-for-like must remain **RESEARCH_ONLY** with no numerical competitive parity claim.

### Minimum proof packet
- One PRY issue, accountable human owner, source repository and exact pre-change SHA, target user, measurable need and observed failure.
- Two direct references and one lateral expert mechanism, each with URL, checked date, rights and why-it-works explanation. These references form the discovery shortlist, *not* automatically testable competitors.
- Frozen SHA256 fixture and preregistered metrics, weights, sample count, reviewer qualifications, blind design for subjective work, performance/cost ceilings, safety-critical negative tests and success margin. Data may not be revised after candidate scores arrive.
- Actual artefact run, logs/video/source evidence, exact runner and version. Use realistic devices, physical source and real production workflow. Distinguish emulator, simulation, mock, synthetic QA, and live provider behavior.
- Independent acceptance and a genuine expert for creative, educational, medical and hardware decisions. A builder and an independent evaluator must not be same identity.
- Mandatory rights/originality, privacy/client separation, source-fidelity, safety and R0 no-spend gates. One hard-stop failure blocks release regardless of weighted score.
- At least 20 objective cases for *initial review* or 3 blind independent editorial judges with adequately diverse examples. Larger samples and appropriate confidence intervals required for stronger scientific/commercial claims; these minima do not confer significance.
- A reproducible negative suite, holdout leakage check, confidence/uncertainty, cost per **accepted** result, rollback and next experiment. Never optimize metric proxies that degrade human outcome.
- Final status: RESEARCH_ONLY, PROPOSED, EXECUTED_OFFLINE, INDEPENDENTLY_REPRODUCED, REVIEW_REQUIRED, or separate independently approved RELEASED. Automated validator can only emit HOLD, ITERATE, REVIEW_REQUIRED, never RELEASED.

## Real tool candidates, verified docs 20 October 2026
- UK AISI Inspect: https://inspect.aisi.org.uk/ ; scoring https://inspect.aisi.org.uk/scoring.html . Task datasets, sandbox, tool and scorer composability. Use in an approved sandbox only.
- Hugging Face LightEval: https://huggingface.co/docs/lighteval/main/index . Many backends and tasks, Inspect backend highlighted. Hub model cards/leaderboards are research, not local performance evidence.
- Hugging Face Evaluation: https://huggingface.co/docs/evaluate/index .
- Langfuse: https://langfuse.com/docs/evaluation/overview . Traces, datasets, offline experiments, CI score/regression evaluation, requires deliberate configuration.
- Promptfoo: https://www.promptfoo.dev/docs/guides/llm-redteaming/ . Prompt injection, privacy, refusal, adversarial and app quality, may consume inference credits.
- OSWorld-V2: https://github.com/xlang-ai/OSWorld-V2 . Version-pinned GUI/computer-use agent research, costly environments require approval.
- Stanford HELM: https://github.com/stanford-crfm/helm . Holistic evaluation precedent, **maintenance mode since 1 June 2026**, not default active backend.
- Existing Pryntor: PRY-309, PRY-199, PRY-67, PRY-366. **Reuse** current improvement controller, scientific holdouts, visual QA and authenticated agent action laws.

## Implementation and status honesty
`tools/pryntor-wtbw/validate.py` checks packet structure and comparative measurement consistency using no third-party libraries, no network, no model, no GPU, no mailbox and no credentials. Report clearly: synthetic tests vs real artefact; local vs exact-head hosted CI; referenced source vs installed tool; proposed agent vs verified online runtime. Integrity, reviewer signatures, provenance and rights are separate external decisions and cannot be validated from JSON alone. Do not claim production security enforcement without real provider-path negative tests. No automatic merges, publish, email, fees, procurement or unapproved actions.
