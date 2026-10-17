"""Portable context vault, R0 reference implementation. No external dependencies.

This deliberately does NOT provide production authentication or hosted scheduling.
Run inside a secured, user-controlled directory; all clients must be authorized by
its owner at the operating-system and connector layers.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
from datetime import datetime, timezone

KINDS = {"Soul", "Memory", "Artifact", "Skill", "Lesson", "Decision"}
SCOPES = {"Personal", "Company", "Project"}
SENSITIVITY = {"Public", "Internal", "Restricted"}
SECRET_PATTERN = re.compile(r"(?i)(?:\b(?:password|api[_ -]?key|secret|access[_ -]?token|recovery[_ -]?code)\s*[:=]\s*\S+|\bgh[pousr]_[a-zA-Z0-9]{20,}|\bsk-[a-zA-Z0-9_-]{20,}|\bAKIA[0-9A-Z]{16}\b)")


def canonical(x):
    return json.dumps(x, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def digest(x):
    return hashlib.sha256(canonical(x).encode("utf-8")).hexdigest()


def now():
    return datetime.now(timezone.utc).isoformat()


def atomic_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp = tempfile.mkstemp(prefix=".vault-", dir=str(path.parent))
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(obj, f, sort_keys=True, indent=2, ensure_ascii=False)
            f.write("\n")
            f.flush()
            os.fsync(f.fileno())
        os.replace(temp, path)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)


class VaultError(ValueError):
    pass


class Vault:
    def __init__(self, root):
        self.root = Path(root)
        self.path = self.root / "vault.json"

    def _load(self):
        if not self.path.exists():
            return {"schema": 1, "entries": {}, "events": []}
        obj = json.loads(self.path.read_text(encoding="utf-8"))
        if obj.get("schema") != 1 or not isinstance(obj.get("entries"), dict) or not isinstance(obj.get("events"), list):
            raise VaultError("Unsupported or invalid vault schema")
        return obj

    def _commit(self, state, action, key, entry):
        # SHA-256 chains detect accidental edits. They are not digital signatures.
        old = state["events"][-1]["hash"] if state["events"] else "0" * 64
        event = {"at": now(), "action": action, "key": key,
                 "revision": entry["revision"], "record_hash": digest(entry), "prev": old}
        event["hash"] = digest(event)
        state["events"].append(event)
        state["entries"][key] = entry
        atomic_json(self.path, state)
        return entry

    def verify(self):
        state = self._load()
        previous = "0" * 64
        latest = {}
        for event in state["events"]:
            if event.get("prev") != previous or event.get("hash") != digest({k: v for k, v in event.items() if k != "hash"}):
                raise VaultError("Audit chain mismatch")
            previous = event["hash"]
            latest[event["key"]] = event["record_hash"]
        if set(latest) != set(state["entries"]):
            raise VaultError("Entry/audit manifest mismatch")
        for key, entry in state["entries"].items():
            if digest(entry) != latest[key]:
                raise VaultError(f"Record tampering detected: {key}")
        return {"verified_records": len(latest), "audit_events": len(state["events"]), "chain_head": previous}

    def propose(self, *, key, kind, scope, sensitivity, content, source, owner, expected_revision=None):
        if not key or len(key) > 160 or not re.fullmatch(r"[a-z0-9][a-z0-9._:-]*", key):
            raise VaultError("Stable key must be 1–160 lowercase alphanumeric/dot/colon/underscore/hyphen")
        if kind not in KINDS or scope not in SCOPES or sensitivity not in SENSITIVITY:
            raise VaultError("Invalid category, scope or sensitivity")
        if not isinstance(content, str) or not content.strip() or len(content.encode("utf-8")) > 32000:
            raise VaultError("Content must have 1–32000 bytes")
        if SECRET_PATTERN.search(content):
            raise VaultError("Possible credential: keep secrets in a dedicated secrets broker")
        if not isinstance(source, str) or not (source.startswith("https://") or source.startswith("local:")):
            raise VaultError("Require an HTTPS or local: evidence reference")
        if not owner or len(owner) > 160:
            raise VaultError("Owner required")
        state = self._load()
        before = state["entries"].get(key)
        old_rev = before["revision"] if before else 0
        if expected_revision is not None and expected_revision != old_rev:
            raise VaultError("Revision conflict; reload before writing")
        if before and expected_revision is None:
            raise VaultError("Existing key; explicit expected revision required")
        entry = {"key": key, "kind": kind, "scope": scope, "sensitivity": sensitivity,
                 "content": content, "source": source, "owner": owner,
                 "revision": old_rev + 1, "review": "Proposed", "agent_read": False,
                 "updated_at": now()}
        return self._commit(state, "propose", key, entry)

    def approve(self, key, expected_revision, reviewer, agent_read=False):
        state = self._load()
        entry = state["entries"].get(key)
        if not entry or entry["revision"] != expected_revision:
            raise VaultError("Missing record or revision conflict")
        if not reviewer or len(reviewer) > 160:
            raise VaultError("Reviewer required")
        if entry["sensitivity"] == "Restricted" and agent_read:
            raise VaultError("Restricted content cannot enter agent exports")
        updated = {**entry, "revision": entry["revision"] + 1, "review": "Approved",
                   "reviewer": reviewer, "agent_read": bool(agent_read), "updated_at": now()}
        return self._commit(state, "approve", key, updated)

    def export_agent(self, scope, output):
        if scope not in SCOPES:
            raise VaultError("Invalid export scope")
        self.verify()
        state = self._load()
        records = []
        for x in sorted(state["entries"].values(), key=lambda e: e["key"]):
            if x["scope"] != scope or x["sensitivity"] == "Restricted":
                continue
            if x["review"] != "Approved" or not x["agent_read"]:
                continue
            records.append({k: x[k] for k in ("key", "kind", "scope", "sensitivity", "content", "source", "owner", "revision")})
        payload = {"schema": 1, "purpose": "scoped-agent-context", "scope": scope,
                   "records": records, "checksum": digest(records)}
        dest = Path(output)
        if dest.resolve() == self.path.resolve():
            raise VaultError("Cannot export over the primary vault")
        atomic_json(dest, payload)
        return {"records": len(records), "checksum": payload["checksum"], "path": str(dest)}

    def import_handoff(self, input_path, owner):
        # An external handoff is always untrusted and must go back through proposal review.
        payload = json.loads(Path(input_path).read_text(encoding="utf-8"))
        records = payload.get("records", [])
        if payload.get("schema") != 1 or payload.get("checksum") != digest(records) or not isinstance(records, list):
            raise VaultError("Invalid handoff checksum or schema")
        proposed = []
        for x in records:
            key = x["key"]
            proposed.append(self.propose(key=key, kind=x["kind"], scope=x["scope"],
                                         sensitivity=x["sensitivity"], content=x["content"],
                                         source=x["source"], owner=owner))
        return {"imported_proposals": len(proposed)}


def main():
    p = argparse.ArgumentParser(description="Portable context vault R0: local, owner-managed, not production auth")
    p.add_argument("--root", default=".vault", help="Private local data folder")
    sub = p.add_subparsers(dest="command", required=True)
    a = sub.add_parser("propose")
    for arg in ("key", "kind", "scope", "sensitivity", "content", "source", "owner"):
        a.add_argument("--" + arg.replace("_", "-"), required=True)
    a.add_argument("--expected-revision", type=int)
    a = sub.add_parser("approve")
    a.add_argument("--key", required=True)
    a.add_argument("--expected-revision", type=int, required=True)
    a.add_argument("--reviewer", required=True)
    a.add_argument("--agent-read", action="store_true")
    a = sub.add_parser("export-agent")
    a.add_argument("--scope", required=True, choices=sorted(SCOPES))
    a.add_argument("--output", required=True)
    a = sub.add_parser("import-handoff")
    a.add_argument("--input", required=True)
    a.add_argument("--owner", required=True)
    sub.add_parser("verify")
    args = vars(p.parse_args())
    command = args.pop("command").replace("-", "_")
    v = Vault(args.pop("root"))
    result = getattr(v, command)(**args)
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
