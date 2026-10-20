#!/usr/bin/env python3
"""Pryntor workcell proposals, never an agent launcher or authority service.

Consumes the existing founder_dispatch.py selection output. It cannot access
external tools, authenticate receipts, allocate budgets, provision models,
merge, publish or contact anyone. Standard library only.
"""
import argparse
import json
import re
import sys
from pathlib import Path

ISSUE = re.compile(r"PRY-[1-9][0-9]{0,5}\Z")
SHA = re.compile(r"[0-9a-f]{40}\Z")
REPOS = frozenset({
    "LLoliwe/pryntor-motion", "LLoliwe/pryntor-forge",
    "LLoliwe/pryntor-recover", "LLoliwe/pryntor-company-site",
    "LLoliwe/Leseli", "LLoliwe/pryntor-home-intelligence",
    "LLoliwe/Anthropic-skills", "LLoliwe/agent-spend-proof",
    "LLoliwe/OPEN-AI-skills", "LLoliwe/knowledge-work-plugins",
})

# Roles are independent scopes under EXISTING TRIAGE-001, not new dispatchers.
ROLES = {
    "security-reviewer": ("Find scope/privacy/rights/credential threats", "Threat model and reproducible negative tests"),
    "implementation-engineer": ("Repair a verified broken user journey", "Reviewable code patch and functional tests"),
    "browser-device-qa": ("Reproduce and retest the actual end-to-end journey", "Browser/device traces, screenshots, and failure cases"),
    "commercial-operator": ("Improve an existing first-cash conversion journey", "Evidence-backed offer, lawful draft and measurable funnel proof"),
    "partnership-researcher": ("Research reciprocal partner value without contacting anyone", "Verified partner landscape and thoughtful unsigned draft"),
    "original-world-builder": ("Build original, rights-safe interactive worlds", "Playable source change and captured interaction evidence"),
    "visual-integrity-reviewer": ("Protect approved character and brand canon", "Asset diffs, rights trace and visual regression report"),
    "film-director": ("Direct coherent shots, lighting, action and sound", "Rendered timed scene, A/V checks and visual notes"),
    "payments-sandbox-qa": ("Test recovery claims without touching real money", "Sandbox-only reproducible receipt and negative tests"),
    "learning-experience-designer": ("Build educational interactions with measured learning value", "Working lesson interaction and educator review pack"),
    "assessment-safety-reviewer": ("Find false credit, leakage, unsafe or ungrounded assessment", "Held-out cases, first-error traces and abstention results"),
    "robotics-simulation-engineer": ("Reproduce sim controller baselines and latency failures", "Seed-locked sim metrics and regression report"),
    "evidence-auditor": ("Independently compare work with acceptance criteria", "Source-pinned PASS/HOLD verdict and missing proof"),
}

WORKCELLS = {
    "security": ("security-reviewer", "implementation-engineer", "evidence-auditor"),
    "zowibo": ("original-world-builder", "implementation-engineer", "visual-integrity-reviewer"),
    "company_site": ("commercial-operator", "implementation-engineer", "browser-device-qa"),
    "first_cash": ("commercial-operator", "partnership-researcher", "evidence-auditor"),
    "recover": ("payments-sandbox-qa", "implementation-engineer", "evidence-auditor"),
    "studios": ("film-director", "implementation-engineer", "visual-integrity-reviewer"),
    "btww": ("film-director", "implementation-engineer", "visual-integrity-reviewer"),
    "robotics_sim": ("robotics-simulation-engineer", "implementation-engineer", "evidence-auditor"),
    "lvl7": ("learning-experience-designer", "implementation-engineer", "browser-device-qa"),
    "syw": ("assessment-safety-reviewer", "implementation-engineer", "evidence-auditor"),
    "general": ("implementation-engineer", "browser-device-qa", "evidence-auditor"),
}

POLICY = (
    "R0 unapproved spend. No paid calls, subscriptions, auto-topups or renewals. "
    "No external messages, partner contact, client data, child data, publishing, "
    "public release, merge, deployment, account/permission changes, physical control "
    "or payment actions without separately recorded founder and required owner approval. "
    "Do not use Jellyfish property, data, accounts, credentials, assets or source. "
    "Never claim a role definition is a running agent. No self-approval."
)

def plan_workcell(selection):
    """Advisory routing only, never proof of actor authentication or execution."""
    if not isinstance(selection, dict):
        raise ValueError("Selection must be an object")
    if selection.get("status") != "READY_FOR_SCOPED_OPERATOR":
        raise ValueError("Existing dispatcher did not select eligible work")
    for flag in ("execution_started", "independent_review_complete", "release_authorized", "paid_spend_authorized"):
        if selection.get(flag) is not False:
            raise ValueError("Untrusted or missing dispatch safety flag: " + flag)
    selected = selection.get("selected")
    if not isinstance(selected, dict):
        raise ValueError("Missing selected work item")
    issue, repo, sha, lane = (selected.get(x) for x in ("issue", "repo", "source_sha", "lane"))
    if not isinstance(issue, str) or not ISSUE.fullmatch(issue):
        raise ValueError("Invalid canonical issue")
    if not isinstance(repo, str) or repo not in REPOS:
        raise ValueError("Repository not allowlisted")
    if not isinstance(sha, str) or not SHA.fullmatch(sha):
        raise ValueError("Unpinned source")
    if not isinstance(lane, str) or lane not in WORKCELLS:
        raise ValueError("Unknown lane")
    planner, maker, checker = WORKCELLS[lane]
    return {
        "status": "DRAFT_HANDOFF_NOT_EXECUTED",
        "existing_router": "TRIAGE-001 / founder_dispatch.py",
        "issue": issue, "repo": repo, "source_sha": sha, "lane": lane,
        "roles": [
            {"stage": stage, "role": role, "mission": ROLES[role][0], "expected_artifact": ROLES[role][1]}
            for stage, role in zip(("plan", "build", "independent_check"), (planner, maker, checker))
        ],
        "loop": {"pattern": "plan > build > inspect > repair > inspect > founder review",
                 "max_repair_attempts": 2, "on_failed_acceptance": "HOLD_REVIEW_REQUIRED"},
        "tool_permissions": ["read_approved_source", "propose_branch_patch", "run_approved_offline_tests", "draft_evidence"],
        "policy": POLICY,
        "required_receipt": ["authenticated_operator", "issue", "repo", "source_sha", "new_commit_or_artifact_sha256",
                             "test_commands_exit_codes_and_log_digests", "negative_cases", "independent_reviewer",
                             "cost_receipt", "founder_release_decision"],
        "execution_started": False, "model_provisioned": False,
        "independent_review_complete": False, "release_authorized": False,
    }

def render_prompt(plan):
    if not isinstance(plan, dict) or plan.get("status") != "DRAFT_HANDOFF_NOT_EXECUTED":
        raise ValueError("Plan must be a non-executing workcell handoff")
    lines = ["PRYNTOR WORKCELL | Review-only handoff", "",
             "Existing controller: " + plan["existing_router"],
             "Task: " + plan["issue"], "Repository: " + plan["repo"],
             "Pinned baseline: " + plan["source_sha"], "Lane: " + plan["lane"], "",
             "REQUIRED PROCESS"]
    for item in plan["roles"]:
        lines.append(f"{item['stage'].upper()}: {item['role']} | {item['mission']} | Output: {item['expected_artifact']}")
    lines.extend(["", "Complete no more than two repair cycles. If proof fails, stop with HOLD.",
                  "Recheck permissions, authenticated actor, source and ownership before touching any workspace.",
                  "Record source commit, real artifact, functional + negative tests, owner, independent review and cost.",
                  "No green status from self-reported flags. Keep drafts unmerged and unpublished.", "",
                  "NON-NEGOTIABLE: " + plan["policy"]])
    return "\n".join(lines) + "\n"

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--format", choices=("json", "prompt"), default="json")
    args = parser.parse_args(argv)
    if args.input.stat().st_size > 500_000:
        raise ValueError("Selection file too large")
    plan = plan_workcell(json.loads(args.input.read_text(encoding="utf-8")))
    print(json.dumps(plan, indent=2, sort_keys=True) if args.format == "json" else render_prompt(plan),
          end="\n" if args.format == "json" else "")
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, OSError, json.JSONDecodeError) as err:
        print(json.dumps({"status": "HOLD_INVALID_SELECTION", "reason": str(err), "execution_started": False}))
        sys.exit(2)
