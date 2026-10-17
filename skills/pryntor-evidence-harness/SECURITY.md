# Pryntor Sentinel V2: Security and trust boundaries

This is a defensive engineering verification tool, **not** a security sandbox, signer, secrets broker, independently trusted source of truth, release approval or production agent.

## In-scope trust

1. **Trusted contract:** registered commands are arbitrary local executable code and have every permission the invoking user has. The `--approved-contract-sha256` comparison detects drift relative to the explicitly supplied digest, but cannot prove who approved that digest. Pin the reviewed constant in protected CI configuration or a code-owner-reviewed workflow. Never accept the digest/contract from an agent or an untrusted PR as an equivalent approval.
2. **Project snapshot:** hashes regular included files and refuses symlink directories/files, but excludes `.git`, virtual environments, `node_modules`, bytecode, caches and `graphify-out`. Do not claim complete dependency integrity without lockfile provenance and separate supply-chain checks. Tampering with out-of-scope dependency sources or time-dependent external systems is not ruled out. A check could mutate a file and put it back before the final hash.
3. **Process isolation:** process groups and timeouts limit normal child survival. A check could create a new session, launch services, perform network calls, or access accessible files. Containerize with no egress and no secrets at the runner/OS layer. Never trust a worker-generated check on a privileged runner.
4. **Evidence:** a self-contained checksum catches accidental corruption. It does not authenticate its author or prevent fabrication by someone who controls evidence files. Hosted CI checks on the exact commit and independent acceptance are stronger provenance than a locally replayed report. Evidence is not written over existing files and defaults to 0600, but local admins may still read it.
5. **Output and privacy:** standard output and errors are *not* persisted by default, only hashes/lengths; enabled tail redaction is heuristic and can miss secrets. The full stream is briefly spooled to OS temporary storage. Avoid sensitive targets and do not publish evidence containing personal, child, customer, employer, finance or credential data.
6. **Optional model:** `route_diagnostic` is pure advisory. Jev is not connected and no paid model is required. Confidence isn't empirical accuracy. Unavailable/invalid/ambiguous suggestions never trigger a command or completion.
7. **Review:** HTML uses escaped content and an inline-only CSP. It intentionally has no JavaScript, network calls, editable decisions or release-action button.

## Independent review needed before production adaptation

- Threat-model arbitrary executable test registries and insecure runner environment.
- Check that trusted CI and branch protection protect reviewed contract digests and evidence artifacts.
- Review symlink TOCTOU, file-graph exclusions, unbounded disk writes by subprocesses, shell execution inside approved scripts, processes escaping group cleanup, race conditions, output leak paths and platform assumptions (Linux/macOS only).
- Add durable artifact signing or trusted CI attestations only if provider-issued provenance can actually be verified, not a self-signed JSON checksum.
- Test a real held-out integration and negative tests with an independent reviewer, not the same worker.
- Authorize business-specific release separately: accessibility, curriculum/safety, customer-data privacy, licensed assets, POPIA, hardware and finance as applicable.
- Log R0 financial spend based on actual provider billing, not assumptions about free tiers.

**Explicit HOLD:** no vendor tokens, no hosted private repo upload, no spending, no production secrets, no product release and no unsupervised repair loop are authorized by this V2.