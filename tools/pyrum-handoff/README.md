# Pryntor Pyrum handoff preflight R1

A tiny **offline-only, fail-closed** proposal gate for existing Pryntor fleet work. It never contacts, installs, authenticates or dispatches a Dot. It does not hold leases and must NOT compete with existing TRIAGE-001 or PRY-83.

## Use

Run from the repository root:

~~~bash
python3 -m unittest discover -s tools/pyrum-handoff/tests -v
python3 tools/pyrum-handoff/preflight.py tools/pyrum-handoff/examples/safe-public-research.json
~~~

Valid safe shapes output REVIEW_ONLY with dispatches_work=false and releases_execution=false. Denied inputs output HOLD (exit 1) and invalid file/JSON input outputs INVALID (exit 2). This validation is metadata and structure only. It cannot prove the source references were retrieved or that goal text is benign. No cryptographic attestation or external access.

## Single approved route

1. Check the existing Linear owner, task, permissions and TRIAGE-001 lease.
2. Require an actual independent read-after-write challenge and agent task URL for PRY-96.
3. Deliver one bounded artifact, independently reopen and test it, record exact source revision and cost.
4. Ask the founder before any external sends, publishing, production, security, money, privileged access or other governed actions.
5. If the Dot cannot be reached, record NOT_CONNECTED; a third-party relay is not an ACK.

The public source includes no credentials or tenant data. Do not put private approvals or production history in this repository. The current first-party Skill is at skills/pryntor-pyrum-omega/SKILL.md.

**Release state:** R1 synthetic gate for human review only. It is not a production bridge, live worker, unattended runtime or completed security audit.
