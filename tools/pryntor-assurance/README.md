# Pryntor Assurance Gate R0

Offline, dependency-free, fail-closed evidence completeness checker, for use inside controlled review branches.

## What it actually does

Checks that each required control has a VERIFIED status, a separate reviewer, explicit independent-review assertion, fresh review date, unexpired evidence date, HTTPS evidence URL and an expected SHA-256 digest format. Rejects missing and duplicate control records, missing proof and stale records. Returns exit code 0 when a synthetic complete metadata record passes, 1 on missing/incorrect evidence and 2 for invalid input.

**It does not authenticate the reviewer, open or verify an external URL, verify the hash against actual evidence, validate an ISO certificate, audit the underlying control, prove compliance, or act as an independently accredited certification body.** A green metadata result is not sufficient to release anything. A competent independent assessor must inspect the actual evidence.

## Run

Run the following commands from repository root in an isolated trusted checkout:

    python3 tools/pryntor-assurance/assurance_gate.py tools/pryntor-assurance/requirements.example.json tools/pryntor-assurance/evidence.example.json --as-of 2026-10-20

The example deliberately fails because its controls are OPEN/CONTROL DESIGN and do not have evidence. This is correct and protective.

    python3 -m unittest discover -s tools/pryntor-assurance -p 'test_*.py' -v

Twenty tests cover positive synthetic metadata and negative/malformed inputs. No external Python dependencies, provider calls, payment, network access or secrets.

## Controlled adoption

1. Freeze product, obligations and required control IDs before evaluating the associated evidence.
2. Collect original source links, immutable commit/run digests, actual tests and names of independent reviewers outside this toy fixture.
3. Confirm substantive results, scopes, independence and nonapplicability separately with domain experts.
4. Adopt on individual reviewed product branches with explicit release owners and keep this gate advisory until separate technical review and merge.
5. Never mark evidence VERIFIED just to pass this program.

Status: review-only draft PR. Not commissioned as production CI, persistent chief or independent auditor. Do not publish customer, child or secret material in a public repository.

Related: https://linear.app/pryntor/issue/PRY-364
Control tower: https://docs.google.com/spreadsheets/d/1zQJytwllwMGdKa0R5wo48cUM_BkIyB37mptqQJmT4V0/edit
