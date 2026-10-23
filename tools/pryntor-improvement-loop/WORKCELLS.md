# Pryntor specialist workcells R0

**Status: code and offline test proposal on existing PR #58. Not installed, hosted, scheduled or executing.**

Inspired by Google Cloud Tech's June 2026 Google ADK tutorial on sequential planner/worker/checker teams. This code is stdlib-only and provider-agnostic. It is not an ADK installation, model instance or persistent workforce.

## Reuse before expansion

- Authority and dispatch remain in existing TRIAGE-001 and `founder_dispatch.py`.
- Existing work tracking remains the canonical PRY issue and repository.
- Existing `loop.py` owns separately reviewed bounded source improvement, if activated by an authenticated human operator.
- This module only turns an already-screened `READY_FOR_SCOPED_OPERATOR` dispatch result into a review-only, specialist-role handoff.
- All 11 existing dispatch lanes are covered by 13 reusable roles. The workcell stages are planner, maker and independent checker, followed by at most 2 bounded repair attempts if an approved runtime is separately connected.
- Reviewer must be a separate authenticated actor. Merely putting a different role name in JSON is not independent review.

## Run offline

```sh
python3 tools/pryntor-improvement-loop/founder_dispatch.py --mode select --input /path/to/verified-input.json --now 2026-10-20T04:00:00Z > /tmp/dispatch.json
python3 tools/pryntor-improvement-loop/agent_workcells.py --input /tmp/dispatch.json --format prompt
python3 -m unittest discover -s tools/pryntor-improvement-loop -p 'test_*.py' -v
```

These commands do **not** cause an agent to act. They can prepare review briefs from locally supplied data. A passing suite does not establish deployment, authorizations or useful product output.

## For a future execution pilot

1. Inspect the existing agent registry and assigned issues, and deduplicate.
2. Retrieve authenticated live code at the pinned SHA, task ownership, founder approvals and allowed tools.
3. Planner states acceptance tests, negative cases, data classification and hard stop.
4. Maker writes an original change only to a bounded review branch, with no customer content, payments or external communication.
5. Independent checker reproduces product tests, including a real browser/device journey where applicable.
6. If failed, return scoped feedback to the maker. Stop after 2 attempts with HOLD, preserve failed attempts and receipts.
7. Check artifact/commit hashes, independent operator identity, CI logs, cost, rights and approval. No auto merge, publish or deployment.

A handoff is not a work receipt. All tool credentials and runtime capabilities must be checked in their actual account context. If unavailable, mark BLOCKED or UNVERIFIED.

## Non-negotiable

R0 unapproved expenditure, no subscriptions or overages, no autonomous outbound partner messages, no children/customer data, and no Jellyfish-owned materials. Portfolio-specific instructions can remain in authorized private Pryntor records rather than this public repository.

Reference: [Google Cloud's official ADK codelab](https://codelabs.developers.google.com/build-ai-agent-google-adk).
