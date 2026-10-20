#!/usr/bin/env python3
"""Pure-stdlib, offline, fail-closed *evidence completeness* gate.

This never verifies certificates, checks remote evidence contents, or substitutes
for independent auditors. No network, subprocess, filesystem mutation or secrets.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
import ipaddress
from pathlib import Path
from urllib.parse import urlsplit

SCHEMA = 1
HEX64 = re.compile(r"^[0-9a-fA-F]{64}$")
ID = re.compile(r"^[A-Z][A-Z0-9_-]{2,63}$")
PASS = "VERIFIED"


def _date(value, context, violations):
    if not isinstance(value, str):
        violations.append(f"{context}: expected ISO date string")
        return None
    try:
        return dt.date.fromisoformat(value)
    except ValueError:
        violations.append(f"{context}: invalid ISO date")
        return None


def _https(value):
    if not isinstance(value, str):
        return False
    try:
        parsed = urlsplit(value)
        host = (parsed.hostname or "").lower().rstrip(".")
        if not host or host == "localhost" or host.endswith((".local", ".internal")):
            return False
        try:
            if not ipaddress.ip_address(host).is_global:
                return False
        except ValueError:
            pass  # DNS hostnames only validated syntactically; no network requests.
        return parsed.scheme == "https" and parsed.username is None and parsed.password is None
    except ValueError:
        return False


def evaluate(requirements, evidence, *, as_of=None):
    """Return (passed: bool, violations: list[str]) for offline supplied records.

    A VERIFIED result only means the *record* has an independent named reviewer
    and externally addressable evidence metadata. It does not inspect the URL,
    verify a person's identity or prove technical implementation.
    """
    violations = []
    if not isinstance(requirements, dict) or not isinstance(evidence, dict):
        return False, ["Root inputs must both be JSON objects"]

    if requirements.get("schema_version") != SCHEMA:
        violations.append("Requirements schema_version must be 1")
    if evidence.get("schema_version") != SCHEMA:
        violations.append("Evidence schema_version must be 1")

    project = requirements.get("project")
    if not isinstance(project, str) or not project.strip():
        violations.append("Requirements project must be a nonempty string")
    if evidence.get("project") != project:
        violations.append("Evidence project does not match requirements project")

    required = requirements.get("required_controls")
    if not isinstance(required, list) or not required:
        return False, violations + ["required_controls must be a nonempty list"]
    if any(not isinstance(cid, str) or not ID.fullmatch(cid) for cid in required):
        violations.append("required_controls contains invalid control IDs")
    if len(set(map(str, required))) != len(required):
        violations.append("Duplicate required control IDs")

    max_age = requirements.get("max_evidence_age_days", 90)
    if type(max_age) is not int or not 1 <= max_age <= 365:
        violations.append("max_evidence_age_days must be an integer from 1 to 365")
        max_age = 90
    today = as_of or dt.datetime.now(dt.timezone.utc).date()
    if not isinstance(today, dt.date):
        return False, violations + ["as_of must be a date"]

    controls = evidence.get("controls")
    if not isinstance(controls, list):
        return False, violations + ["Evidence controls must be a list"]
    by_id = {}
    for index, record in enumerate(controls):
        if not isinstance(record, dict):
            violations.append(f"control index {index}: expected object")
            continue
        cid = record.get("id")
        if not isinstance(cid, str) or not ID.fullmatch(cid):
            violations.append(f"control index {index}: invalid id")
            continue
        if cid in by_id:
            violations.append(f"{cid}: duplicate evidence record")
        else:
            by_id[cid] = record

    for cid in required:
        if not isinstance(cid, str):
            continue
        record = by_id.get(cid)
        if record is None:
            violations.append(f"{cid}: REQUIRED CONTROL MISSING")
            continue
        if record.get("status") != PASS:
            violations.append(f"{cid}: status must be VERIFIED (not {record.get('status')!r})")
        owner = record.get("owner")
        reviewer = record.get("reviewer")
        if not isinstance(owner, str) or not owner.strip():
            violations.append(f"{cid}: missing human owner")
        if not isinstance(reviewer, str) or not reviewer.strip():
            violations.append(f"{cid}: missing independent reviewer")
        if (
            isinstance(owner, str)
            and isinstance(reviewer, str)
            and owner.strip().casefold() == reviewer.strip().casefold()
        ):
            violations.append(f"{cid}: owner cannot self-review")
        if record.get("independent_review") is not True:
            violations.append(f"{cid}: explicit independent_review=true required")
        if not _https(record.get("evidence_url")):
            violations.append(f"{cid}: valid HTTPS evidence_url required")
        if not isinstance(record.get("evidence_sha256"), str) or not HEX64.fullmatch(record["evidence_sha256"]):
            violations.append(f"{cid}: evidence_sha256 must be 64 hex digits")
        checked = _date(record.get("reviewed_at"), f"{cid} reviewed_at", violations)
        expiry = _date(record.get("valid_until"), f"{cid} valid_until", violations)
        if checked:
            if checked > today:
                violations.append(f"{cid}: review date is in the future")
            elif (today - checked).days > max_age:
                violations.append(f"{cid}: evidence review is stale")
        if expiry and expiry < today:
            violations.append(f"{cid}: evidence expired")
    return len(violations) == 0, violations


def main(argv=None):
    parser = argparse.ArgumentParser(description="Offline evidence completeness check, not ISO certification")
    parser.add_argument("requirements", type=Path)
    parser.add_argument("evidence", type=Path)
    parser.add_argument("--as-of", help="ISO date for reproducible testing, defaults to UTC today")
    args = parser.parse_args(argv)
    try:
        requirements = json.loads(args.requirements.read_text(encoding="utf-8"))
        evidence = json.loads(args.evidence.read_text(encoding="utf-8"))
        at = dt.date.fromisoformat(args.as_of) if args.as_of else None
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        print(json.dumps({"gate": "FAIL", "error": type(exc).__name__, "reason": str(exc)}))
        return 2

    ok, problems = evaluate(requirements, evidence, as_of=at)
    print(json.dumps({
        "gate": "PASS" if ok else "FAIL",
        "as_of": (at or dt.datetime.now(dt.timezone.utc).date()).isoformat(),
        "project": requirements.get("project"),
        "required_control_count": len(requirements.get("required_controls", [])),
        "violations": problems,
        "note": "Record completeness only. Independent assessor must inspect underlying source and approve."
    }, sort_keys=True, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
