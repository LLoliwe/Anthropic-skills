# Pryntor source fidelity R0 (PRY-264)

This Pryntor-original dependency-free offline tool validates **declared exact spans** of an answer against specified spans of a supplied source, and checks the source's declared SHA-256 digest. It is **not** a Copy-Paste Language Model neural head, LLM, semantic fact-checker, citation retriever, mathematical grader, or evidence of improved model accuracy.

## Usage

Run `node --test tools/source-fidelity/test.mjs` and `node tools/source-fidelity/audit.mjs tools/source-fidelity/example.json` from the repository root (Node 22+). The CLI returns JSON with `ok`, `checked`, and error codes; exit 0 passes, exit 1 holds. No packages, GPUs, credentials, network calls or external sources are used.

Manifest format: `version:1`, `source:{ref,text,sha256}`, `answer:string`, `claims:[...]`. For a `copy` claim supply `id`, `value`, `sourceSpan:[start,end]`, `answerSpan:[start,end]`. For an `absent` claim supply `id`, `needle`. Spans are JS UTF-16 code-unit offsets, **not byte or grapheme indices**. The sample contains only invented identifiers and amounts.

Hard bounds: CLI file 1MiB, source 200k code units, answer 100k, claims 1–500. No claim values or source content are logged in the standard error output. The test suite includes 100 generated synthetic fixtures plus negative checks; these are **unit tests**, not held-out evaluation against a real model.

## Important limitations

- A source text and matching hash can both be forged; authenticate provenance/revision independently.
- Checks cover only **declared** claims, not omitted claims or the entire answer; a correctly copied phrase may be the wrong phrase for the question.
- A literal `absent` check cannot prove the agent actually abstained, or that a fact does not exist elsewhere.
- Exact case-sensitive matching intentionally preserves negatives, decimals, IDs, dates, equations, UTMs and punctuation; there is no semantic numeric parsing or auto-rewrite.
- A passing output says only that this narrow mechanical contract holds. Human/domain QA, security/privacy checks, citations, correct math, freshness, source authority and full-answer truth require other gates.
- Never insert sensitive company, campaign customer, student or traveller data in experimental/public endpoints. Do not treat the tool as a production guard without field discovery, all-claim coverage and independent held-out model evaluation.

## Company rollout

Central opt-in skill: `skills/pryntor-source-fidelity/SKILL.md`. High-fit pathways: Pryntor research/Context Fabric, code, LVL7/SYW transcription, paid social QA, approved Tirisano workflows. Others only for demonstrated literal-accuracy requirements. This central repository does NOT automatically install to every agent, product or production runtime.

Before external or user-facing rollout: PRY-199 preregistration, frozen baseline and independent holdout, all results/failures, security and rights review, business-domain owner approval and rollback. Zero new spend; no paid retraining or third-party pretrained weights.

Source: https://arxiv.org/abs/2610.19247 | Company brief: https://docs.google.com/document/d/1L24vhrqp8zOk4Zjh7fBP5QnxJMg88YsufpopM6-tWnI/edit | Tracker: https://linear.app/pryntor/issue/PRY-264
