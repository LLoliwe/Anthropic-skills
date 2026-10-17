---
name: pryntor-learning-graph
description: Evidence-first, zero-new-spend curriculum prerequisite graph adapter and teacher-reviewed learning pathways. Use for LVL7, Show Your Working, authorised kids learning work and selected training; not a default dependency across all ventures.
---

# Pryntor Learning Graph — R0 internal shared capability

**Upstream:** Marble Skill Taxonomy, Generative Spark, Inc. / Marble: https://github.com/withmarbleapp/os-taxonomy . This integration is original Pryntor code; Marble's Water Lab, Ecosystem Simulator, 3D visualisation and learner application source are NOT part of the open-source dataset and are not installed or copied.

## Safe use

1. Pin upstream v1 to commit 96a7933754af672e1bfdbf7ecb05c325860c6e0d. Validate topics.json SHA-256 2d99fc3b5e57d9ddb86b6c179b58a1b0390f048d9798585fe03b13cbc183719b and dependencies.json SHA-256 86a24efb44b480e5be23082b4bdea653f69f6d6fd54c5409a2f33c185be1d87f. The official upstream data/manifest.json is the source of these checksums. Review any version changes.
2. Database (structure, IDs, graph edges): ODbL 1.0; Marble-authored text: CC BY-SA 4.0, attribution and share-alike required. Third-party curriculum standards carry SEPARATE licences. Review upstream PROVENANCE.md. NGSS, IB and C3 verbatim text may not be backfilled without rights. CCSS text use is purpose-restricted. Notices for uses: 'Marble Skill Taxonomy (v1) · © Generative Spark, Inc. (Marble) · https://withmarble.com · licensed under ODbL 1.0 (database) and CC BY-SA 4.0 (content).' Additional source notices when applicable.
3. Do not vendor upstream data into Pryntor core repositories or use it to train AI automatically. This pilot fetches unchanged files into temporary CI storage only; product redistribution needs formal legal/IP clearance.
4. Original Pryntor graph engine: tools/learning-graph/graph.mjs. CLI: tools/learning-graph/cli.mjs. A pathway lists prerequisites before a topic (hard-only or hard-plus-soft) and does not certify mastery, enforce learning progression or generate assessment scores. Dangling edges, cycles, duplicates, invalid strengths and self-edges fail closed.
5. Teaching layer needs learner age band, local learning standard with source/rights, lesson objective, teacher-approved solutions, accessibility accommodations and actual reviewer. This is PRIMARY/elementary and US/UK-oriented; not automatically CAPS/NSC, IGCSE, IB, AP or university aligned. Each country mapping must be original, sourced, reviewed and versioned.
6. No child names, IDs, learner profiles or progress telemetry. Before collecting any real child records: consent, safeguarding, lawful basis and retention/privacy assessment. AI teaching recommendations require teacher/parent review.

## Venture applicability

- LVL7: trial maths/science prerequisite paths and original interactive labs, subject to educator review, correctness, learner study and accessibility.
- Show Your Working: prerequisite/misconception RESEARCH only; no unapproved Grade 12 marking, method scores or false credit.
- Children's games/Studios: original game design using educational objectives; obtain gameplay, child-safety, IP and expert review.
- Robotics: teach mechanics and progression; not a safety, physics, latency or hardware validation substitute.
- Pryntor Core / Mission Control: optionally reuse versioned graph utility and provenance guardrails; do not enable learner-specific services without tenant/privacy isolation.
- Tirisano, BTWW, Recover and remaining units: optional analogous staff-training graph method only. NO mandatory install or asserted educational fit.

## Run / review

Local original tests: node --test tools/learning-graph/tests/graph.test.mjs (no npm dependencies).
With already verified JSON files: node tools/learning-graph/cli.mjs TOPICS_FILE DEPS_FILE summary
Other commands: search fraction; path TOPIC_ID --hard-only.
CI workflow: .github/workflows/pryntor-learning-graph.yml validates the original offline regressions; downloads TWO unchanged source-pinned Marble files into a transient CI runner; matches official SHA-256; checks full 1,590-topic/3,221-edge DAG. No personal or learner data is involved.
Local synthetic tests are not pedagogy review. CI green is not installed into venture repositories or publicly deployed. Application owner must review fit, deliver a reversible scoped diff, accept curriculum/privacy/licensing/accessibility and independently validate pedagogy before production rollout.
Zero-new-spend default. No GPUs, paid calls, vendor outreach, publication or customer changes authorised by this R0.
