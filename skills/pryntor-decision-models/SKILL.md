---
name: pryntor-decision-models
description: Optional EU-only, fail-closed synthetic decision-inference research pilot for Pryntor.
---

# Pryntor Decision Models — R0 Research Pilot

**Scope:** Classify/reroute original synthetic cases for benchmarking only. Never grant permissions, move funds, message customers, grade learners, change ads, or delete records based on model answers. TRIAGE-001 remains Pryntor's sole dispatcher. No new spending. No credentials in GitHub, Slack, Drive, Linear or prompts.

## Manual activation

1. Visit https://decisionmodels.io/signup with company identity. Accept standard Terms of Service v1.4 and DPA v1.2. On 17 Oct 2026 vendor clarified the separately published Free Pilot Addendum does NOT apply to self-service invitation accounts.
2. Use dashboard **Have an invite code?**, retrieving secret privately from Florian's 16 Oct email. Invitation code expires 5 Dec 2026; allowance is **100,000,000 input tokens for 60 days after redemption**. Never copy invitation code into this repository or chat.
3. Confirm free allowance and its activation/expiry on dashboard. Create **EU-tier** API key only, with worldwide and network processing disabled. Store in approved secrets manager (DECISIONMODELS_API_KEY). Do not add payment method, purchase credits or enable auto-top-ups.
4. Vendor reserves up to 4,096 free input tokens before each request; if insufficient, requests fail rather than being charged (17 Oct email). This client has **no account balance read capability**. Human must verify dashboard before any live run.
5. Without any network calls, run `python3 scripts/decision_models.py` and `python3 -m unittest discover -s tests -v`.
6. A single synthetic test can only run with --live, PRYNTOR_DM_LIVE=1 and DECISIONMODELS_API_KEY securely injected from a secrets manager: `python3 scripts/decision_models.py --live --case 0`. Never paste keys into command history.
7. Capture real request ID, model_version, account tier, latency and allowance change from provider receipts for review. The R0 client does NOT validate all response telemetry; no claims of real accuracy or EU-region independent verification yet.

## Engineering gates

- Only s1-fast/s1-pro text choice questions; s1-vision separately gated for image consent/rights.
- 8,192 provider input-token limit includes state, question and options. The client uses a conservative character guard; **character count is NOT token counting**.
- Zero automatic retries, zero global fallbacks, no secret logging, no payment operations.
- Only synthetic/no PII in preapproved CLI fixtures; real user/customer/student or financial data needs explicit privacy/security sign-off.
- One adapter means not company-wide production adoption. Pilot is replaceable. Model probability is advisory, not a final action.
- Independent holdout tests, baseline comparison, critical false-negative escalation rate and production approval required prior to any deployment.

**Source:** 16 and 17 Oct 2026 vendor company email; https://decisionmodels.io/docs/api and https://decisionmodels.io/docs/api/reference

**Control ledger:** https://linear.app/pryntor/issue/PRY-259/dm-001-activate-100m-token-decision-models-eu-pilot-and-benchmark
