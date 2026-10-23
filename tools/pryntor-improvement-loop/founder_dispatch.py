#!/usr/bin/env python3
"""Founder-priority router and evidence gate for existing Pryntor work.

Offline advisory code. It does not authenticate sources, execute tasks, acquire
locks, provision agents, call models, spend credits, send messages or release.
"""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import sys

REPOS = frozenset({
    "LLoliwe/pryntor-motion", "LLoliwe/pryntor-forge",
    "LLoliwe/pryntor-recover", "LLoliwe/pryntor-company-site",
    "LLoliwe/Leseli", "LLoliwe/pryntor-home-intelligence",
    "LLoliwe/Anthropic-skills", "LLoliwe/agent-spend-proof",
    "LLoliwe/OPEN-AI-skills", "LLoliwe/knowledge-work-plugins",
})
# Tier order follows existing founder decisions: safety, ZOWIBO, site/first cash.
LANES = {"security": 42, "zowibo": 40, "company_site": 36,
         "first_cash": 34, "recover": 23, "studios": 20, "btww": 20,
         "robotics_sim": 19, "lvl7": 18, "syw": 18, "general": 8}
UI_LANES = {"zowibo", "company_site", "recover", "studios", "btww", "lvl7"}
URGENCY = {"P0": 22, "P1": 12, "P2": 5}
IMPACT = {"broken_user_journey": 22, "verified_blocker": 18,
          "quality_gap": 12, "preventive": 5}
EFFORT = {"small": 0, "medium": 6, "large": 13}
ISSUE = re.compile(r"^PRY-[1-9][0-9]{0,5}$")
SHA = re.compile(r"^[0-9a-f]{40}$")
PROOF = re.compile(r"^[0-9a-f]{64}$")
FORBIDDEN = frozenset({
    "send", "outreach", "partner_contact", "purchase", "paid_api",
    "merge", "deploy", "publish", "submit", "contract", "payment",
    "new_account", "iam_change", "secret_access", "physical_control",
    "unapproved_data_transfer", "customer_data", "child_data",
})
ALLOWED_ACTIONS = {"internal_patch", "offline_original_asset", "internal_test"}
MAX_ITEMS = 100


def parse_time(value):
    if not isinstance(value, str):
        raise ValueError("Timestamp must be a string")
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("Invalid ISO timestamp") from exc
    if dt.tzinfo is None:
        raise ValueError("Timestamp must include timezone")
    return dt.astimezone(timezone.utc)


def exact_fields(obj, required, optional=()):
    if not isinstance(obj, dict):
        raise ValueError("Expected a JSON object")
    missing, unknown = set(required) - obj.keys(), obj.keys() - set(required) - set(optional)
    if missing or unknown:
        raise ValueError("Missing or unknown fields: " + ",".join(sorted(missing | unknown)))


def known(value, choices):
    return isinstance(value, str) and value in choices


def valid_ref(value, repo):
    return (known(repo, REPOS) and isinstance(value, str)
            and value.startswith("https://github.com/" + repo + "/"))


def screen(item, now):
    """Fail closed for protected actions and cases without a proven failure."""
    required = ("issue", "repo", "source_sha", "source_url", "lane", "urgency",
                "impact", "effort", "updated_at", "failure_state", "repro",
                "acceptance", "negative_case", "action", "risks",
                "claimed_by_other", "spend_required", "review_required")
    exact_fields(item, required)
    problems = []
    if not isinstance(item["issue"], str) or not ISSUE.fullmatch(item["issue"]):
        problems.append("INVALID_CANONICAL_ISSUE")
    if not known(item["repo"], REPOS) or not valid_ref(item["source_url"], item["repo"]):
        problems.append("UNAPPROVED_SOURCE")
    if not isinstance(item["source_sha"], str) or not SHA.fullmatch(item["source_sha"]):
        problems.append("UNPINNED_SOURCE")
    if not known(item["lane"], LANES) or not known(item["urgency"], URGENCY):
        problems.append("UNKNOWN_PRIORITY")
    if not known(item["impact"], IMPACT) or not known(item["effort"], EFFORT):
        problems.append("UNKNOWN_WORK_SCOPE")
    try:
        age = (now - parse_time(item["updated_at"])).total_seconds()
        if age < -300 or age > 86400:
            problems.append("STALE_OR_FUTURE_SNAPSHOT")
    except ValueError:
        problems.append("INVALID_SNAPSHOT_TIME")
    if item["failure_state"] != "reproduced_failing":
        problems.append("NO_REPRODUCED_FAILURE")
    if not isinstance(item["repro"], str) or len(item["repro"].strip()) < 12:
        problems.append("NO_REPRO_STEPS")
    for field in ("acceptance", "negative_case"):
        if not isinstance(item[field], str) or len(item[field].strip()) < 12:
            problems.append("MISSING_" + field.upper())
    if not known(item["action"], ALLOWED_ACTIONS):
        problems.append("UNAPPROVED_ACTION")
    if not isinstance(item["risks"], list) or any(not isinstance(x, str) for x in item["risks"]):
        problems.append("INVALID_RISK_LIST")
    elif set(item["risks"]) & FORBIDDEN or item["risks"]:
        problems.append("UNREVIEWED_RISK")
    if item["claimed_by_other"] is not False:
        problems.append("OWNERSHIP_NOT_CLEAR")
    if item["spend_required"] != 0 or type(item["spend_required"]) is not int:
        problems.append("NONZERO_OR_UNVERIFIED_SPEND")
    if item["review_required"] is not True:
        problems.append("MISSING_REVIEW_GATE")
    return sorted(set(problems))


def score(item):
    """Simple auditable ordering. The caller must independently verify input facts."""
    return (LANES[item["lane"]] + URGENCY[item["urgency"]]
            + IMPACT[item["impact"]] - EFFORT[item["effort"]])


def select(frame, now):
    exact_fields(frame, ("schema_version", "tasks"))
    if type(frame["schema_version"]) is not int or frame["schema_version"] != 1 or not isinstance(frame["tasks"], list):
        raise ValueError("Invalid work-item schema")
    if len(frame["tasks"]) > MAX_ITEMS:
        raise ValueError("Too many work items")
    # Duplicate tasks could distort priorities or cause concurrent worker claims.
    seen = set()
    eligible, rejected = [], []
    for item in frame["tasks"]:
        if not isinstance(item, dict):
            raise ValueError("Task must be an object")
        key = item.get("issue")
        if not isinstance(key, str) or key in seen:
            raise ValueError("Missing or duplicate issue")
        seen.add(key)
        blockers = screen(item, now)
        if blockers:
            rejected.append({"issue": key, "reasons": blockers})
        else:
            eligible.append((score(item), item["issue"], item))
    eligible.sort(key=lambda x: (-x[0], x[1]))
    winner = eligible[0] if eligible else None
    return {
        "status": "READY_FOR_SCOPED_OPERATOR" if winner else "HOLD_NO_ELIGIBLE_WORK",
        "selected": ({"issue": winner[1], "repo": winner[2]["repo"],
                      "source_sha": winner[2]["source_sha"],
                      "lane": winner[2]["lane"], "score": winner[0],
                      "next_step": "recheck live branch and ownership before one review-only change"}
                     if winner else None),
        "ranking": [{"issue": issue, "score": points}
                    for points, issue, _ in eligible[:5]],
        "rejected": rejected, "execution_started": False,
        "independent_review_complete": False, "release_authorized": False,
        "paid_spend_authorized": False,
        "notice": "Advisory ranking from caller-supplied metadata; verify live source and proof.",
    }


def evidence_gate(record):
    """Assess completeness only. JSON assertions are not independent verification."""
    exact_fields(record, ("issue", "repo", "lane", "base_sha", "result_sha",
                          "artifact_sha256", "tests", "source_changed",
                          "independent_review"))
    gaps = []
    if not isinstance(record["issue"], str) or not ISSUE.fullmatch(record["issue"]):
        gaps.append("INVALID_ISSUE")
    if not known(record["repo"], REPOS) or not known(record["lane"], LANES):
        gaps.append("UNKNOWN_OWNER_OR_LANE")
    if any(not isinstance(record[k], str) or not SHA.fullmatch(record[k])
           for k in ("base_sha", "result_sha")):
        gaps.append("UNPINNED_REVISION")
    elif record["base_sha"] == record["result_sha"]:
        gaps.append("NO_NEW_COMMIT")
    if not isinstance(record["artifact_sha256"], str) or not PROOF.fullmatch(record["artifact_sha256"]):
        gaps.append("NO_IMMUTABLE_ARTIFACT")
    if record["source_changed"] is not True:
        gaps.append("NO_WORK_PRODUCT")
    needed = {"functional", "negative"} | ({"browser"} if known(record["lane"], UI_LANES) else set())
    actual = set()
    tests = record["tests"]
    if not isinstance(tests, list) or not tests or len(tests) > 30:
        gaps.append("MISSING_EXECUTED_TESTS")
    else:
        for t in tests:
            if not isinstance(t, dict) or set(t) != {"type", "command", "exit_code", "log_sha256"}:
                gaps.append("INVALID_TEST_RECEIPT")
                continue
            if (not known(t["type"], {"functional", "negative", "browser", "integration"})
                    or not isinstance(t["command"], list) or not t["command"]
                    or any(not isinstance(a, str) or not a for a in t["command"])
                    or type(t["exit_code"]) is not int or t["exit_code"] != 0
                    or not isinstance(t["log_sha256"], str) or not PROOF.fullmatch(t["log_sha256"])):
                gaps.append("INVALID_OR_FAILED_TEST")
            else:
                actual.add(t["type"])
        for kind in sorted(needed - actual):
            gaps.append("MISSING_" + kind.upper() + "_PROOF")
    if record["independent_review"] not in ("PENDING", "FAILED", "PASSED"):
        gaps.append("UNKNOWN_REVIEW_STATE")
    elif record["independent_review"] != "PASSED":
        gaps.append("INDEPENDENT_REVIEW_PENDING")
    return {"status": "READY_FOR_EXTERNAL_RECEIPT_CHECK" if not gaps else "HOLD_EVIDENCE_GAPS",
            "gaps": sorted(set(gaps)), "tests_declared": sorted(actual),
            "external_test_logs_authenticated": False,
            "human_review_authenticated": False, "release_authorized": False,
            "paid_spend_authorized": False,
            "notice": "Manifests cannot authenticate CI, device tests, reviewer identity or rights."}


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--mode", choices=("select", "evidence"), required=True)
    p.add_argument("--input", required=True, type=Path)
    p.add_argument("--now", default=None, help="UTC ISO timestamp, useful for deterministic replay")
    args = p.parse_args(argv)
    if args.input.stat().st_size > 500_000:
        raise ValueError("Input frame exceeds offline limit")
    data = json.loads(args.input.read_text(encoding="utf-8"))
    now = parse_time(args.now) if args.now else datetime.now(timezone.utc)
    result = select(data, now) if args.mode == "select" else evidence_gate(data)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"].startswith("READY") else 2


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "BLOCKED_INVALID_INPUT", "error": str(exc),
                          "execution_started": False, "release_authorized": False}))
        sys.exit(2)
