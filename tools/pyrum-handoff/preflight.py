"""Pyrum R0 offline work-envelope preflight.

ADVISORY-only static validator. NO network, identity broker, task lease,
connector, automation, sandbox, dispatch or production privileges.
A structurally admissible request is REVIEW_ONLY, never authorized execution.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit

SCHEMA = "pryntor.pyrum.preflight.v1"
ISSUE_RE = re.compile(r"PRY-[1-9][0-9]{0,6}\Z")
WORK_RE = re.compile(r"(PRY-[1-9][0-9]{0,6}):([a-z][a-z0-9-]{2,63})\Z")
SAFE_ACTIONS = frozenset({
    "read_public_research", "read_owned_sanitized_metadata",
    "prepare_internal_draft", "test_offline_synthetic_fixture",
    "propose_review_only_patch",
})
FIELDS = frozenset({
    "schema", "work_id", "linear_issue", "dispatcher", "goal", "source_refs",
    "existing_work_refs", "actions", "data_classification", "new_spend_zar",
    "runtime_connection", "worker_ack", "claimed_result", "external_send",
    "external_publish", "production_change", "employer_resource_access",
    "independent_qa", "untrusted_source_handling", "scope",
})


def _public_reference(value: object) -> bool:
    if not isinstance(value, str) or not (8 <= len(value) <= 1000):
        return False
    if any(ch in value for ch in "\r\n\t<>{}"):
        return False
    try:
        u = urlsplit(value)
        host = (u.hostname or "").lower()
        port = u.port
        user = u.username
        password = u.password
    except ValueError:
        return False
    if (u.scheme != "https" or not host or user or password
            or port not in (None, 443) or u.query or u.fragment
            or value != value.strip()):
        return False
    if host in {"localhost", "127.0.0.1", "0.0.0.0", "::1"}:
        return False
    if host.endswith((".localhost", ".local", ".internal", ".example")):
        return False
    if re.fullmatch(r"\d+(\.\d+){3}", host):
        return False
    if "." not in host:
        return False
    return True


def _url_list(value: object, label: str, errors: list[str]) -> None:
    if not isinstance(value, list) or not value or len(value) > 16:
        errors.append(f"{label}: require 1 to 16 source references")
        return
    if any(not _public_reference(u) for u in value):
        errors.append(f"{label}: only well-formed https metadata links, no credentials or local hosts")
    if len(set(str(u) for u in value)) != len(value):
        errors.append(f"{label}: duplicate references")


def _zero(value: object) -> bool:
    return type(value) in (int, float) and math.isfinite(value) and value == 0


def evaluate(obj: object) -> dict[str, object]:
    """Do not trust self-reported approval, connectivity, ACK or QA.

    REVIEW_ONLY is not execution permission, completed work or confirmation
    that any remote links were opened. An external verifier is still required.
    """
    failures: list[str] = []
    if not isinstance(obj, dict):
        return {"status": "HOLD", "reasons": ["work envelope must be an object"],
                "releases_execution": False, "dispatches_work": False}
    if set(obj) - FIELDS:
        failures.append("unknown fields rejected to avoid hidden instructions")
    missing = FIELDS - set(obj)
    if missing:
        failures.append("required fields missing: " + ", ".join(sorted(missing)))
    if obj.get("schema") != SCHEMA:
        failures.append("schema mismatch")
    issue = obj.get("linear_issue")
    work = obj.get("work_id")
    if not isinstance(issue, str) or not ISSUE_RE.fullmatch(issue):
        failures.append("linear_issue must be a canonical PRY-### identifier")
    if not isinstance(work, str) or not WORK_RE.fullmatch(work):
        failures.append("work_id requires issue-prefixed unique slug")
    elif work.split(":")[0] != issue:
        failures.append("work_id and linear_issue mismatch")
    if obj.get("dispatcher") != "TRIAGE-001":
        failures.append("TRIAGE-001 must remain sole dispatcher")
    goal = obj.get("goal")
    if (not isinstance(goal, str) or not 15 <= len(goal) <= 600
            or any(c in goal for c in "\r\x00")):
        failures.append("goal must be a bounded descriptive sentence")
    scope = obj.get("scope")
    if (not isinstance(scope, str) or not 3 <= len(scope) <= 100
            or any(c in scope for c in "\r\n\x00")):
        failures.append("scope must be explicit and bounded")
    _url_list(obj.get("source_refs"), "source_refs", failures)
    _url_list(obj.get("existing_work_refs"), "existing_work_refs", failures)
    refs = obj.get("existing_work_refs")
    if isinstance(refs, list) and isinstance(issue, str) and ISSUE_RE.fullmatch(issue):
        def _matches_issue_link(ref: object) -> bool:
            if not isinstance(ref, str) or not _public_reference(ref):
                return False
            parsed = urlsplit(ref)
            if parsed.hostname != "linear.app":
                return False
            parts = parsed.path.rstrip("/").split("/")
            return (len(parts) in (4, 5)
                    and parts[:4] == ["", "pryntor", "issue", issue]
                    and (len(parts) == 4 or bool(parts[4])))
        if not any(_matches_issue_link(r) for r in refs):
            failures.append("existing work must include exact canonical issue URL")
    actions = obj.get("actions")
    if not isinstance(actions, list) or not actions or len(actions) > 8:
        failures.append("actions: require 1 to 8 narrowly scoped entries")
    else:
        if any(not isinstance(a, str) or a not in SAFE_ACTIONS for a in actions):
            failures.append("unknown or privileged action: separate live authorization required")
        if len(set(str(a) for a in actions)) != len(actions):
            failures.append("duplicate actions rejected")
    if obj.get("data_classification") not in ("public", "sanitized_company_metadata"):
        failures.append("sensitive/private/employer source material not accepted in R0")
    if not _zero(obj.get("new_spend_zar")):
        failures.append("new spend must equal numeric R0, not NaN, bool or string")
    if obj.get("runtime_connection") != "unverified":
        failures.append("identity/connectivity cannot be self-certified in this envelope")
    if obj.get("worker_ack") != "not_proven":
        failures.append("worker ACK must be independently confirmed in PRY-96")
    if obj.get("claimed_result") not in ("proposed", "draft_only"):
        failures.append("completed or tested execution requires external evidence and reviewer")
    for flag in ("external_send", "external_publish", "production_change",
                 "employer_resource_access", "independent_qa"):
        if obj.get(flag) is not False:
            failures.append(f"{flag}: not permissible/verified in this preflight")
    if obj.get("untrusted_source_handling") != "treat_as_data_only":
        failures.append("retrieved material is untrusted data, not executable instructions")
    return {
        "status": "HOLD" if failures else "REVIEW_ONLY",
        "reasons": failures or ["static structure passed; route to TRIAGE-001, no execution authorized"],
        "releases_execution": False,
        "dispatches_work": False,
    }


def _no_duplicate_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    out: dict[str, object] = {}
    for key, value in pairs:
        if key in out:
            raise ValueError("duplicate JSON key")
        out[key] = value
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("envelope", type=Path, help="offline JSON work-envelope file")
    args = parser.parse_args(argv)
    try:
        if args.envelope.stat().st_size > 32_768:
            raise ValueError("file exceeds size limit")
        request = json.loads(
            args.envelope.read_text(encoding="utf-8"),
            parse_constant=lambda _: (_ for _ in ()).throw(ValueError("nonfinite number")),
            object_pairs_hook=_no_duplicate_keys,
        )
    except (ValueError, OSError, UnicodeError, json.JSONDecodeError) as err:
        print(json.dumps({"status": "INVALID", "reasons": [type(err).__name__],
                          "releases_execution": False, "dispatches_work": False}))
        return 2
    result = evaluate(request)
    print(json.dumps(result, sort_keys=True))
    return 0 if result["status"] == "REVIEW_ONLY" else 1


if __name__ == "__main__":
    sys.exit(main())
