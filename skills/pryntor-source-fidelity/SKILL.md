---
name: pryntor-source-fidelity
description: Optional source-span verification for evidence-grounded agent outputs where IDs, amounts, equation transcriptions, code or exact quotes must be preserved.
---

# Pryntor source fidelity R0

Select this optional skill only when source-preserving generation is materially relevant. Examples: R&D documents/Context Fabric, code/config, LVL7 and Show Your Working question/work transcription (NOT automatic grading), paid social budgets/UTMs, and authorised Tirisano records. Never install across all ventures blindly. Artwork, original writing and robotics controls ordinarily do not need this.

## Procedure

1. Identify an **authorised** and independently trusted source version; verify access/privacy; freeze ref and source SHA-256. Never upload sensitive, child or customer data to public endpoints.
2. List the exact identifiers, signs, decimals, units, equations, dates, text/code and quotations that matter. Require matching source and answer UTF-16 spans.
3. Create `version:1` manifest and use `node tools/source-fidelity/audit.mjs path/to/manifest.json`; 0 indicates checked literal consistency; 1 indicates HOLD. Log failed IDs/codes without leaking raw source.
4. Separately review citations, relevance, whole-answer coverage, numeric interpretation, refusals/absence and domain correctness. A declared-span pass cannot validate undeclared claims or source authority.
5. For a performance claim, follow PRY-199 preregistration, frozen baseline and independent holdout; record full run failures, latency, spend and human review. R0 new spend; production remains gated.

Technical contract, sample and tests: `tools/source-fidelity/README.md`. This original deterministic utility is **not** the trained Copy-Paste Language Models architecture by Nathan Godey and Yoav Artzi (https://arxiv.org/abs/2610.19247). Never describe a shared skill registration as persistent deployment on a separate agent client.

Research record: https://linear.app/pryntor/issue/PRY-264
