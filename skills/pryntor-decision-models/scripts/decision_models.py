#!/usr/bin/env python3
"""Pryntor Decision Models synthetic research adapter. Offline by default."""
from __future__ import annotations

import argparse
import json
import os
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ENDPOINT = "https://api.decisionmodels.io/v1/systemone"
ALLOWED_MODELS = {"s1-fast": 1, "s1-pro": 3}
MAX_STATE_CHARS = 10000
MAX_OPTIONS = 10


class GuardrailError(ValueError):
    pass


def make_request(model: str, state: str, questions: dict) -> dict:
    if model not in ALLOWED_MODELS:
        raise GuardrailError("Only s1-fast/s1-pro text models are approved")
    if not isinstance(state, str) or not state or len(state) > MAX_STATE_CHARS:
        raise GuardrailError("State must be nonempty and <=10k characters")
    if not isinstance(questions, dict) or not 1 <= len(questions) <= ALLOWED_MODELS[model]:
        raise GuardrailError("Question count outside model limit")
    for key, question in questions.items():
        if not isinstance(key, str) or not key.isidentifier():
            raise GuardrailError("Question names must be stable identifiers")
        if not isinstance(question, dict) or question.get("type") != "choice":
            raise GuardrailError("R0 supports choice questions only")
        if not isinstance(question.get("instructions"), str) or not question["instructions"].strip():
            raise GuardrailError("Instructions are required")
        criteria = question.get("criteria")
        if not isinstance(criteria, dict) or not 2 <= len(criteria) <= MAX_OPTIONS:
            raise GuardrailError("Two to ten options required")
        if any(not isinstance(k, str) or not k for k in criteria):
            raise GuardrailError("Invalid option name")
    return {"model": model, "state": state, "questions": questions}


def prepare_case(label: str, state: str, model="s1-fast") -> dict:
    options = {"billing": None, "technical": None, "account": None, "human_review": None}
    if label not in options:
        raise GuardrailError("Unknown ground truth")
    return make_request(model, state, {"route": {
        "type": "choice",
        "instructions": "Route this SIMULATED support request. When sensitive or uncertain choose human_review.",
        "criteria": options,
    }})


def send_live(payload: dict, *, key: str | None, live_flag: bool, opener=urlopen) -> dict:
    if not live_flag or os.getenv("PRYNTOR_DM_LIVE") != "1":
        raise GuardrailError("Live disabled; require explicit --live and PRYNTOR_DM_LIVE=1")
    if not key or len(key.strip()) < 12:
        raise GuardrailError("Missing DECISIONMODELS_API_KEY")
    req = Request(ENDPOINT, data=json.dumps(payload).encode(), method="POST", headers={
        "Authorization": "Bearer " + key,
        "Content-Type": "application/json",
        "S1-Region": "eu",
    })
    try:
        with opener(req, timeout=20) as response:
            if response.status != 200:
                raise GuardrailError("Unexpected response status")
            result = json.load(response)
            if not isinstance(result, dict):
                raise GuardrailError("Invalid response envelope")
            return result
    except HTTPError as exc:
        raise GuardrailError(f"HTTP {exc.code}; no retry") from None
    except URLError:
        raise GuardrailError("Network unavailable; no retry") from None


CASES = (
    ("billing", "SYNTHETIC: Change the billing address on invoice 13."),
    ("technical", "SYNTHETIC: Application shows a 502 gateway error."),
    ("account", "SYNTHETIC: I cannot reset my workspace password."),
    ("human_review", "SYNTHETIC: Please permanently erase this workspace."),
    ("billing", "SYNTHETIC: I need a VAT invoice for our subscription."),
    ("technical", "SYNTHETIC: File uploads keep timing out."),
    ("account", "SYNTHETIC: How do I change my account email?"),
    ("human_review", "SYNTHETIC: A customer alleges an unauthorized payment."),
)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", choices=sorted(ALLOWED_MODELS), default="s1-fast")
    parser.add_argument("--live", action="store_true", help="Allow exactly one LIVE synthetic decision")
    parser.add_argument("--case", type=int, choices=range(len(CASES)), default=0)
    args = parser.parse_args(argv)
    expected, state = CASES[args.case]
    payload = prepare_case(expected, state, args.model)
    if not args.live:
        print(json.dumps({"mode": "OFFLINE", "expected": expected, "payload": payload}, indent=2))
        return 0
    try:
        answer = send_live(payload, key=os.getenv("DECISIONMODELS_API_KEY"), live_flag=True)
    except GuardrailError as exc:
        print(f"BLOCKED: {exc}", file=sys.stderr)
        return 2
    print(json.dumps({"mode": "LIVE_SYNTHETIC", "expected": expected, "answer": answer}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
