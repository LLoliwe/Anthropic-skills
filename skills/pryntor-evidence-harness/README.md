# Pryntor Sentinel V2

**Inspectable, fail-closed acceptance for agent-written code.** Pure Python 3.10+, offline, no runtime packages or API keys. Source-code graph analysis is an optional, separate workflow using the reviewed Graphify package. The evidence harness does not summon an agent, perform autonomous repairs, connect to Jev, or deploy code.

## What changed from R0

- **A usable audit page:** generates a static `sentinel-dashboard.html`, with a requirement-by-requirement evidence table and explicit release HOLD. Strict CSP, escaped untrusted strings, no external resources.
- **Approval at the command boundary:** a run/replay requires a **pinned, reviewed canonical contract digest**. Merely having a contract file isn't approval. This is defense against accidental drift, not an authorization server.
- **More defensible evidence:** V2 records have a unique run ID, policy ID, project and contract digests, per-check stdout/stderr hashes and byte counts, and a record checksum. Missing, modified, incomplete and stale records HOLD. A checksum is NOT authentication or a digital signature; anyone able to alter records can recompute it.
- **Safer bounded checks:** direct process invocation, new process session, terminate same-session descendants even after a parent timeout, optional short redacted output only, untrusted environment credentials stripped, memory-bounded capture. The check still has host network, filesystem permissions and could evade process groups: use a locked-down disposable runner.
- **Less misleading model routing:** optional Choice suggestions require valid distributions and separately satisfy both confidence and winner-probability thresholds. The model never chooses executable text or clears release.
- **Adversarial regression suite:** original 17 tests plus 16 new integrity, process, privacy, dashboard and CLI checks, 33 total. The sample has an intentional R2 failure.

## Run a zero-cost demonstration

```bash
cd pryntor-evidence-harness
python3 -B -m unittest discover -s tests -v
python3 -B harness.py digest --contract contract.json
```

For the included `contract.json` the approved demo digest is:

```
2c818ceea2656b76bf125282c73213c251b077350d8aefc23b1e24a9d4a02699
```

After reviewing the contract, run once using unique output file paths **outside** the project:

```bash
python3 -B harness.py run \
  --project fixture --contract contract.json \
  --approved-contract-sha256 2c818ceea2656b76bf125282c73213c251b077350d8aefc23b1e24a9d4a02699 \
  --evidence /tmp/pryntor-sentinel-example.json \
  --html /tmp/pryntor-sentinel-example.html \
  --claim 'Worker says everything is finished'
```

The intended exit status is **2 (HOLD)**. Title search passes, description search fails. The worker's claim is visible but not evidence. Replaying against the **same** project and approved contract digest also returns HOLD:

```bash
python3 -B harness.py replay \
  --project fixture --contract contract.json \
  --approved-contract-sha256 2c818ceea2656b76bf125282c73213c251b077350d8aefc23b1e24a9d4a02699 \
  --evidence /tmp/pryntor-sentinel-example.json
```

The default record omits stdout/stderr tails to minimize accidental information disclosure. `--include-output` enables short, best-effort redacted tails for **synthetic checks only**. Evidence and HTML files are created with mode 0600 and not overwritten.

## Actual guarantees and limits

| Control | What it establishes | What it does not establish |
|---|---|---|
| Project SHA-256 | Byte changes across included regular files | Authenticity, excluded-path integrity, or malicious mutation-and-revert |
| Pinned contract SHA-256 | Executed contract matches a supplied known digest | Who approved the digest, safe check content, or any authorization |
| JSON record checksum | Accidental record alteration after capture | Protection against deliberate rewriting/forgery |
| Bounded checks | Timeout and same-session descendant cleanup | Container sandboxing, egress control, or escaping children |
| All checks pass | Defined contract currently satisfied | Security review, licensing, customer suitability, product release |
| Model hint | Candidate allowlisted diagnostic only | Trustworthy confidence calibration or an executable action |

**`release_authorized` is always `false`.** See `SECURITY.md` and `ROLLOUT.md` before pointing this at anything except disposable fixtures. Never run an untrusted contract or checkout on a privileged runner, and don't index live customer/private repos in hosted Graphify by default.

## Architecture

```
Trusted and pinned contract
        │
        ├── Source snapshot before
        │       └── Bounded registered checks, one by one
        │               ├── Exit status + output digest
        │               └── Source snapshot after
        │
        ├── Evidence record with audit checksum
        ├── Deterministic policy evaluation (no LLM)
        └── JSON verdict + static inspector
             ├── HOLD: missing/failing/stale/invalid
             └── CONTRACT SATISFIED, RELEASE STILL HELD
```

**Company rollout:** PRY-26, PRY-86, PRY-15. Existing single-dispatcher, security, spending, product-review and founder release authorities remain unchanged. Hosted CI results and exact source heads must be checked on the GitHub PR.