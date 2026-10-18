#!/usr/bin/env python3
"""TypeSafe-skill-guided Partnerships pilot, R1.

ONLY named, fictional in-repository cases may enter the request preview.
There is deliberately no HTTP/SDK client, credential reader, mail sender,
or side-effect dispatcher in this module.  No Jev inference is claimed.
"""
from __future__ import annotations

import argparse
import json
import math
from typing import Any

import decision_pilot as policy

MODEL = "jev-1.13.0"
# Fictional, manually created, public-style samples. NOT supplier claims.
CASES: dict[str, dict[str, Any]] = {
    "partner-free-claims": {
        "excerpt": "Fictional provider says: sixty-day no-card developer evaluation, no automatic paid conversion. Contact us to verify terms.",
        "state": {"public_source": True},
    },
    "partner-unclear": {
        "excerpt": "Fictional vendor announces a developer model. Terms and credit eligibility are not listed.",
        "state": {"public_source": True},
    },
    "partner-freemium": {
        "excerpt": "Fictional vendor offers a starter allowance, after which the saved card is automatically charged.",
        "state": {"public_source": True, "card_required": True, "auto_bill": True},
    },
    "partner-risk": {
        "excerpt": "Fictional message requests submitting private customer order data for a no-cost model trial.",
        "state": {"public_source": True, "policy_flags": ["unreviewed_customer_data"]},
    },
    "partner-source-unknown": {
        "excerpt": "Fictional forwarded message offers sponsored tokens from an unverified individual.",
        "state": {"public_source": True, "unknown_identity": True},
    },
    "partner-written-approval": {
        "excerpt": "Fictional provider has a signed pilot offer with a verified sponsor and approved R0 terms.",
        "state": {"public_source": True, "verified_sponsor": True, "written_r0_terms": True},
    },
}

QUESTIONS = {
    "next_queue": {
        "type": "choice",
        "instructions": (
            "Classify the fictional public partner excerpt in state.evidence_excerpt "
            "for a NON-EXECUTING internal review queue. Use only the excerpt, not an "
            "assumed vendor agreement. Research is not outreach. pilot_review does "
            "not approve credit, payment or deployment. When unsure, human_review."
        ),
        "criteria": policy.ROUTES["partnership"],
    },
    "claims_no_card": {
        "type": "noul",
        "instructions": (
            "Does state.evidence_excerpt explicitly claim that a trial needs NO "
            "payment card? This is a text-claim check, not independent verification."
        ),
        "criteria": {
            "true": "Explicit assertion that a payment card is not required",
            "false": "Requires a card or no clear no-card statement",
        },
    },
    "claims_no_auto_conversion": {
        "type": "noul",
        "instructions": (
            "Does state.evidence_excerpt explicitly claim that complimentary "
            "access will NOT automatically convert into paid access? "
            "This does not verify the legal terms."
        ),
        "criteria": {
            "true": "Explicit promise of no automatic paid conversion",
            "false": "Auto-billing indicated or no explicit no-conversion promise",
        },
    },
}


def case_data(case_id: str) -> dict[str, Any]:
    if type(case_id) is not str or case_id not in CASES:
        raise ValueError("unknown synthetic case")
    case = CASES[case_id]
    policy.safe_state("partnership", case["state"])
    if type(case["excerpt"]) is not str or not (10 <= len(case["excerpt"]) <= 700):
        raise ValueError("invalid fictional excerpt")
    return case


def can_model_review(case_id: str) -> bool:
    case = case_data(case_id)
    state = case["state"]
    # Skip vendor inference if a known rule can decide or manual review is mandatory.
    if policy.mandatory_hold(state):
        return False
    if state.get("card_required") is True or state.get("auto_bill") is True:
        return False
    return state.get("public_source") is True


def preview_request(case_id: str) -> dict[str, Any]:
    """Documented TypeSafe HTTP shape, constructed offline and NEVER SENT."""
    case = case_data(case_id)
    if not can_model_review(case_id):
        raise ValueError("vendor evaluation not permitted for this synthetic case")
    return {
        "model": MODEL,
        "state": {
            "evidence_excerpt": case["excerpt"],
            "policy_snapshot": case["state"],
            "synthetic_only": True,
        },
        "questions": QUESTIONS,
    }


def _valid_noul(answer: Any) -> float | None:
    if not isinstance(answer, dict) or answer.get("type") != "noul":
        return None
    p = answer.get("noul")
    if type(p) not in (int, float) or not math.isfinite(p) or not 0 <= p <= 1:
        return None
    # Noul has no confidence field. Treat unexpected "confidence" as contract drift.
    if "confidence" in answer:
        return None
    return float(p)


def review_response(case_id: str, response: Any) -> dict[str, Any]:
    """Interpret a simulated or later authorized response, with zero side effects."""
    case = case_data(case_id)
    state = case["state"]

    def hold(reason: str) -> dict[str, Any]:
        return {
            "case_id": case_id,
            "queue": "human_review",
            "status": "HOLD",
            "reason": reason,
            "claims": {"no_card": None, "no_auto_conversion": None},
            "terms_verified": False,
            "action_executed": False,
            "release_authorized": False,
        }

    if not can_model_review(case_id):
        return hold("local_policy_disallows_model_inference")
    if not isinstance(response, dict) or response.get("model") != MODEL:
        return hold("invalid_model_or_response")
    answers = response.get("answers")
    if not isinstance(answers, dict) or set(answers) != set(QUESTIONS):
        return hold("missing_or_unexpected_answers")
    card = _valid_noul(answers["claims_no_card"])
    billing = _valid_noul(answers["claims_no_auto_conversion"])
    if card is None or billing is None:
        return hold("invalid_noul")
    result = policy.guarded_route("partnership", state, {
        "model": response["model"],
        "answers": {"route": answers["next_queue"]},
    })
    if result["reason"] != "validated_advisory":
        return hold("choice_not_validated:" + result["reason"])
    selected = result["route"]
    # Never promote to pilot_review solely on a TypeSafe judgment.
    if selected == "pilot_review" and not (
        state.get("verified_sponsor") is True and state.get("written_r0_terms") is True
    ):
        return hold("missing_independently_verified_contract")
    return {
        "case_id": case_id,
        "queue": selected,
        "status": "INTERNAL_REVIEW_ONLY",
        "reason": "validated_advisory_not_authorization",
        "claims": {"no_card": card, "no_auto_conversion": billing},
        "terms_verified": bool(
            state.get("verified_sponsor") is True and state.get("written_r0_terms") is True
        ),
        "action_executed": False,
        "release_authorized": False,
    }


def mock_response(choice: str, card: float, billing: float) -> dict[str, Any]:
    """Clearly fictional values for offline tests, NOT a Jev response."""
    options = policy.ROUTES["partnership"]
    if choice not in options:
        raise ValueError("invalid mock choice")
    return {
        "model": MODEL,
        "answers": {
            "next_queue": {
                "type": "choice",
                "choice": choice,
                "confidence": 0.973,
                "probabilities": {key: 0.98 if key == choice else 0.02 / (len(options) - 1) for key in options},
            },
            "claims_no_card": {"type": "noul", "noul": card},
            "claims_no_auto_conversion": {"type": "noul", "noul": billing},
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Synthetic-only TypeSafe skill pilot; no network.")
    parser.add_argument("operation", choices=["preview", "replay"])
    parser.add_argument("--case", choices=sorted(CASES), default="partner-free-claims")
    args = parser.parse_args()
    if args.operation == "preview":
        result = {"status": "UNSENT_PREVIEW", "case": args.case, "request": preview_request(args.case)}
    else:
        result = {
            "status": "MOCK_REPLAY_NOT_MODEL_EVALUATION",
            "result": review_response(args.case, mock_response("research", 0.99, 0.99)),
        }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
