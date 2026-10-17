# Pryntor Evidence Harness: zero-spend R0

This is a runnable, deliberately **offline** prototype, not an installed agent, a production release gate or a deployment. No accounts, keys, third-party packages, Graphify installation or Jev API calls are needed. It provides the most important control from the Jev harness article: independent proof of every mandatory requirement.

## Quickstart

```bash
cd pryntor_evidence_harness
python3 -B -m unittest discover -s tests -v
python3 -B harness.py run --project fixture --contract contract.json --evidence /tmp/pryntor-run.json --claim 'Worker says DONE'
# exit 2, HOLD: title passes, description fails
python3 -B harness.py replay --project fixture --contract contract.json --evidence /tmp/pryntor-run.json
```

Run from Python 3.10 or newer on Linux/macOS with `python3` in PATH. The harness computes a SHA256 snapshot of the project before and after each check, runs only **registered** commands, separately records worker claims, and makes a `contract_satisfied` decision only when all mandatory check results pass against the current snapshot. Any missing, stale, failing, mutated, crashing or unknown check holds. `release_authorized` is **always false** pending independent signoff.

`route_diagnostic` is a pure function for a possible future Jev adapter. It strictly validates a typed Choice distribution, confidence and permitted check ID; its output is a suggestion or stop, never a shell invocation. Jev is NOT connected. There is no estimated gain, monetisation, semantic accuracy or 1,000x claim without new measurements.

**Security model:** The contract is a trusted code-owned registry. Its commands execute locally with the caller's permissions and MUST be code-reviewed. Do not let an AI model, untrusted PR, customer, or web page edit it or supply executable commands. `shell=False` is not a sandbox. Run the harness in a disposable, least-privileged environment without secrets or network egress. Avoid logging sensitive output and avoid exposing generated evidence publicly. Digest checks detect staleness, not malicious forgery or cryptographic authenticity. This sample's fixture contains an intentional bug.

## Adoption gates

1. Confirm company-owned private repository and select one synthetic, narrow requirement from PRY-26 / PRY-86.
2. Add author-maintained checks and test missing, failing, stale, and recovery paths.
3. Pin and security-review Graphify source/package, use its code-only local mode on non-sensitive fixture first, compare graph edges against actual source.
4. Compare fixed/all diagnostic policies to optional Jev on held-out cases, with per-call explicit spend approval; default is no Jev calls.
5. Require independent security and product QA, reviewed CI, cost confirmation and founder release approval before extending beyond R0.

Upstream inspiration: Graphify Labs `Graphify-Labs/graphify` (Apache-2.0), TypeSafe AI Jev, and `Archive228/jev-harness-engineering` (verify source rights before copying). No upstream code has been copied.