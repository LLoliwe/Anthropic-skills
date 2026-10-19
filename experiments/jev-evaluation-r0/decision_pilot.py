#!/usr/bin/env python3
"""Pryntor's no-network Jev evaluation adapter. No TypeSafe calls are made.

Offline baseline and strict typed answer validation. All outputs are review queues,
not tool executions or permissions. Only synthetic fixtures are permitted here.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any

ROUTES = {
    "diagnostic": {
        "inspect_contract": "Review pinned acceptance contract and requirement evidence.",
        "inspect_source": "Review source changes or missing requirement implementation.",
        "inspect_runner": "Examine CI runner and tool errors within approved environment.",
        "human_review": "Stop and obtain independent human review.",
    },
    "partnership": {
        "research": "Collect public supplier evidence without outbound communication.",
        "pilot_review": "Prepare an R0 pilot proposal for a human decision-maker.",
        "reject": "Document why the opportunity is out of policy.",
        "human_review": "Escalate unclear partnership request for manual examination.",
    },
    "quality": {
        "inspect_accessibility": "Route potential accessibility gaps to specialist reviewer.",
        "inspect_rights": "Route potential rights/provenance gaps to qualified reviewer.",
        "inspect_safety": "Route potential safety or child-suitability gaps to specialist reviewer.",
        "human_review": "Stop and obtain independent human review.",
    },
}

# These flags are supplied by the deterministic policy, never by a model.
BLOCK_FLAGS = frozenset({
    "external_send", "payment", "production_release", "secret_access",
    "unreviewed_customer_data", "deletion", "child_data", "network_change",
    "employer_data", "privacy_review_missing", "approval_missing",
})
MIN_CONFIDENCE = 0.90
MIN_WINNER_PROB = 0.90
MIN_MARGIN = 0.30


def canon(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
                      allow_nan=False).encode("utf-8")


def sha(value: Any) -> str:
    return hashlib.sha256(canon(value)).hexdigest()


def safe_state(workflow: str, state: dict[str, Any]) -> dict[str, Any]:
    """Strict synthetic-only schema, with explicit per-workflow boolean inputs."""
    if workflow not in ROUTES or not isinstance(state, dict):
        raise ValueError("unknown workflow or invalid state")
    allowed_by_workflow = {
        "diagnostic": {"contract_mismatch", "missing_requirement", "runner_error",
                       "timeout", "source_failure", "regression"},
        "partnership": {"card_required", "auto_bill", "rights_conflict",
                        "verified_sponsor", "written_r0_terms", "public_source"},
        "quality": {"child_safety_flag", "security_flag", "rights_missing",
                    "asset_unlicensed", "wcag_failure", "keyboard_trap"},
    }
    permitted = allowed_by_workflow[workflow] | {"policy_flags", "approval_required", "unknown_identity"}
    if not all(isinstance(k, str) and k in permitted for k in state):
        raise ValueError("unknown or non-string state key")
    for key, value in state.items():
        if key == "policy_flags":
            if not isinstance(value, list) or any(type(flag) is not str or flag not in BLOCK_FLAGS for flag in value):
                raise ValueError("unknown or invalid policy flag")
            if len(set(value)) != len(value):
                raise ValueError("duplicate policy flag")
        elif type(value) is not bool:
            raise ValueError("state flag must be a boolean")
    if len(canon(state)) > 8192:
        raise ValueError("oversized state")
    return state


def mandatory_hold(state: dict[str, Any]) -> str | None:
    flags = state.get("policy_flags", [])
    if not isinstance(flags, list) or any(not isinstance(x, str) for x in flags):
        return "invalid_policy_flags"
    if any(flag not in BLOCK_FLAGS for flag in flags):
        return "unregistered_policy_flag"
    present = BLOCK_FLAGS.intersection(flags)
    if present:
        return "restricted_action:" + ",".join(sorted(present))
    if state.get("approval_required") is True or state.get("unknown_identity") is True:
        return "explicit_human_approval_required"
    return None


def baseline(workflow: str, state: dict[str, Any]) -> dict[str, str]:
    safe_state(workflow, state)
    reason = mandatory_hold(state)
    if reason:
        return {"route": "human_review", "reason": reason}
    if workflow == "diagnostic":
        if state.get("contract_mismatch") is True or state.get("missing_requirement") is True:
            return {"route": "inspect_contract", "reason": "declared_contract_issue"}
        if state.get("runner_error") is True or state.get("timeout") is True:
            return {"route": "inspect_runner", "reason": "declared_runner_issue"}
        if state.get("source_failure") is True or state.get("regression") is True:
            return {"route": "inspect_source", "reason": "declared_source_issue"}
    elif workflow == "partnership":
        if state.get("card_required") is True or state.get("auto_bill") is True or state.get("rights_conflict") is True:
            return {"route": "reject", "reason": "commercial_policy_reject"}
        if state.get("verified_sponsor") is True and state.get("written_r0_terms") is True:
            return {"route": "pilot_review", "reason": "eligible_for_human_pilot_review"}
        if state.get("public_source") is True:
            return {"route": "research", "reason": "public_source_available"}
    elif workflow == "quality":
        if state.get("child_safety_flag") is True or state.get("security_flag") is True:
            return {"route": "inspect_safety", "reason": "safety_specialist_required"}
        if state.get("rights_missing") is True or state.get("asset_unlicensed") is True:
            return {"route": "inspect_rights", "reason": "rights_specialist_required"}
        if state.get("wcag_failure") is True or state.get("keyboard_trap") is True:
            return {"route": "inspect_accessibility", "reason": "accessibility_specialist_required"}
    return {"route": "human_review", "reason": "insufficient_evidence"}


def build_request(workflow: str, state: dict[str, Any], model: str = "jev-1.13.0") -> dict[str, Any]:
    """Construct an OFFLINE request preview, never transmit it."""
    safe_state(workflow, state)
    if model not in {"jev-1.13.0", "jev-1.14.0"}:
        raise ValueError("pin Jev to an explicit reviewed version")
    if mandatory_hold(state):
        raise ValueError("cannot prepare vendor request for a locally held state")
    return {"model": model, "state": state, "questions": {
        "route": {"type": "choice",
                  "instructions": "Choose only a non-executing internal review queue. Never approve deployment, publishing, payment, sending or data access. If evidence is insufficient choose human_review.",
                  "criteria": ROUTES[workflow]}}}


def validate_choice(workflow: str, answer: dict[str, Any]) -> tuple[str | None, str]:
    """Validate a proposed Jev-like Choice response schema fail closed."""
    options = ROUTES.get(workflow)
    if options is None or not isinstance(answer, dict):
        return None, "invalid_answer"
    if answer.get("type") != "choice":
        return None, "wrong_question_type"
    selected = answer.get("choice")
    probs = answer.get("probabilities")
    confidence = answer.get("confidence")
    if selected not in options or not isinstance(probs, dict) or set(probs) != set(options):
        return None, "invalid_labels"
    if type(confidence) not in (int, float) or not math.isfinite(confidence) or not (0 <= confidence <= 1):
        return None, "invalid_confidence"
    if any(type(v) not in (int, float) or not math.isfinite(v) or not 0 <= v <= 1 for v in probs.values()):
        return None, "invalid_probability"
    if abs(sum(probs.values()) - 1.0) > 0.015:
        return None, "invalid_probability_mass"
    ranked = sorted(probs.values(), reverse=True)
    if probs[selected] < ranked[0] - 1e-8:
        return None, "choice_not_top_probability"
    if confidence < MIN_CONFIDENCE or probs[selected] < MIN_WINNER_PROB or (ranked[0] - ranked[1]) < MIN_MARGIN:
        return None, "uncertain_decision"
    return selected, "validated_advisory"


def guarded_route(workflow: str, state: dict[str, Any], raw_response: dict[str, Any]) -> dict[str, Any]:
    """No external side effect. A model cannot override hard review gates."""
    try:
        safe_state(workflow, state)
    except (ValueError, TypeError):
        return {"route": "human_review", "source": "deterministic_policy",
                "reason": "invalid_state", "release_authorized": False, "action_executed": False}
    blocked = mandatory_hold(state)
    if blocked:
        return {"route": "human_review", "source": "deterministic_policy", "reason": blocked,
                "release_authorized": False, "action_executed": False}
    try:
        if not isinstance(raw_response, dict):
            raise ValueError("invalid_response")
        if raw_response.get("model") not in ("jev-1.13.0", "jev-1.14.0"):
            raise ValueError("unapproved_model")
        answers = raw_response.get("answers", {})
        if not isinstance(answers, dict) or not isinstance(answers.get("route"), dict):
            raise ValueError("missing_choice_answer")
        route, reason = validate_choice(workflow, answers["route"])
    except (ValueError, TypeError):
        route, reason = None, "malformed_provider_response"
    return {"route": route or "human_review", "source": "model_advisory" if route else "safe_fallback",
            "reason": reason, "release_authorized": False, "action_executed": False}


def cases(path: Path) -> list[dict[str, Any]]:
    loaded = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, list) or not loaded:
        raise ValueError("fixtures must be nonempty array")
    ids = set()
    for row in loaded:
        if not isinstance(row, dict) or set(row) != {"id", "workflow", "state", "gold", "split"}:
            raise ValueError("fixture schema mismatch")
        if row["id"] in ids or row["split"] not in {"development", "holdout"}:
            raise ValueError("duplicate id or invalid split")
        ids.add(row["id"])
        safe_state(row["workflow"], row["state"])
        if row["gold"] not in ROUTES[row["workflow"]]:
            raise ValueError("gold outside approved choices")
    return loaded


def offline_report(rows: list[dict[str, Any]]) -> dict[str, Any]:
    segments: dict[str, Any] = {}
    for split in ("development", "holdout"):
        subset = [r for r in rows if r["split"] == split]
        correct = sum(baseline(r["workflow"], r["state"])["route"] == r["gold"] for r in subset)
        segments[split] = {"cases": len(subset), "baseline_match_count": correct,
                           "baseline_match_rate": round(correct / len(subset), 4) if subset else None}
    hard = [r for r in rows if mandatory_hold(r["state"]) is not None]
    hard_holds = sum(baseline(r["workflow"], r["state"])["route"] == "human_review" for r in hard)
    return {"schema": "pryntor-jev-eval-r0", "dataset_sha256": sha(rows), "mode": "offline_rules_only",
            "external_api_calls": 0, "paid_jev_calls": 0, "estimated_new_provider_spend_usd": 0,
            "jev_accuracy_measured": False, "no_customer_data": True, "results": segments,
            "mandatory_hold_cases": len(hard), "mandatory_hold_correct": hard_holds,
            "interpretation": "Synthetic checks establish only baseline harness behavior. Baseline match is not a model benchmark, nor an independent gold-label validity claim.",
            "release_authorized": False}


def main() -> None:
    parser = argparse.ArgumentParser(description="Offline Jev evaluation design. Never sends an API request.")
    parser.add_argument("operation", choices=["benchmark", "request-preview"])
    parser.add_argument("--fixtures", type=Path, default=Path(__file__).with_name("fixtures.json"))
    parser.add_argument("--id", help="Synthetic case ID for request-preview")
    parser.add_argument("--model", default="jev-1.13.0", choices=["jev-1.13.0", "jev-1.14.0"])
    args = parser.parse_args()
    rows = cases(args.fixtures)
    if args.operation == "benchmark":
        result = offline_report(rows)
    else:
        selected = next((r for r in rows if r["id"] == args.id), None)
        if selected is None:
            parser.error("case ID not found")
        result = {"status": "UNSENT_OFFLINE_PREVIEW", "request": build_request(selected["workflow"], selected["state"], args.model)}
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
