# Company adoption, 18 October 2026

## Governance

Status: Sentinel V2 synthetic prototype, independent review needed. Graphify 0.9.92 was installed on a disposable GitHub runner for synthetic mapping only; no production Graphify installation, Jev key, hosted indexing, active background worker or paid service is demonstrated by this package. R0 spend verified within this local run only, not across external provider accounts.

Canonical connected tickets: PRY-26 (portable worker and continuity), PRY-86 (security and commissioning), PRY-15 (source and license decision). Keep TRIAGE-001 as the sole dispatcher and ACCESS-01 as security authority.

## Adoption matrix

| Area | First acceptance contract | Owner/release gate |
|---|---|---|
| Pryntor Core/Mission Control | A claimed action never becomes verified without an exact artifact or provider confirmation | System owner + ACCESS-01 |
| Web/Mobile/Game Studios | Current commit build, deterministic navigation, baseline accessibility checks | Product owner + independent UX/security QA |
| LVL7/Show Your Working/ZOWIBO | Educator or child-safety review is independent of test coverage | Child safety + specialist + founder |
| Recover/Tirisano | Sandbox-only financial and travel workflow checks, no live payments or customer actions | Finance/operations + security |
| Robotics | Offline nominal/latency regression and simulator provenance, never infer hardware success | Robotics specialist + safety |
| Pryntor Studios/BTWW | Render-export artifact identity, rights and independent creative QA | Editorial/product owner + rights |
| Partnerships/first cash | Verified sent mail, contract status and settled receipts, not drafted outreach or promises | Partnerships + finance |

Do not bring employer/Jellyfish, private customer, child, medical or owner credential material into the shared graph.

## Rollout sequence

1. Review the original harness source in PR, run 33 tests and verify fail-closed outcomes on an unchanged and deliberately broken fixture.
2. Independently evaluate security (registered-command trust boundary, sandbox, output redaction, symlinks, untrusted PR code, replay tamper resistance). The digest is not a signed attestation.
3. Evaluate Graphify's official Apache-2.0 repository and the `graphifyy` package. Pin a specific reviewed release and hash before invoking it in an isolated synthetic project. Graphify's structural map is optional and must not override acceptance tests.
4. Compare deterministic routing and run-all-cheap-diagnostics against Jev's allowlisted recommendations on blinded cases. API call count and cost default to zero. Seek sponsored credits only if pricing, privacy and billing caps are verified first.
5. Integrate one owner-approved venture repo on a draft PR without release permissions. Require hosted CI on that exact head SHA and independent review before reuse.
6. Reuse the same gates in other repos only after evidence of correctness, safety and no additional spend. No bulk auto-deployment or blanket permission expansion.

## Outcome metrics, measured per task

- False-complete rate; fresh mandatory checks passed / total; held-out acceptance success.
- Mean time to independently verified repair; repeat-failure rate; number of worker iterations.
- Tokens and cash consumed per accepted task, including Graphify/Jev if enabled.
- Artifact recovery, incident rate, rollback readiness and external approvals.
- Commercial: shipping lead-time reduction, paid customer conversion, and bank-confirmed settled revenue, recorded separately from estimates.

Current sample is not evidence of an enterprise-scale speedup, active employees or profit increase.

## V2 upgrade and release gate

- Trusted contract approval is an explicit pinned checksum in CI. Never generate and approve a checksum from an untrusted PR in the same step.
- Add immutable write-once JSON and static HTML inspector to each *synthetic* pilot run. Replays recompute checksums and always evaluate against the current project.
- Human reviewer must inspect actual test coverage, Graphify map correctness, completeness of source scope, and source/contract provenance.
- Separate source-inspection/diagnostic improvement from product business acceptance.
- An independent owner-approved **Recover synthetic merchant-flow adapter** is the first proposed next pilot; do not claim it exists or is tested yet. Do not touch real PayPal/CRM credentials or external customers.
- Require independent final acceptance, a negative mutation scenario, red-team review, exact-head hosted CI and verified R0 spend before scaling.