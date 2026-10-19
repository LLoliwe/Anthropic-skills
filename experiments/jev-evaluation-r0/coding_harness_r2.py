#!/usr/bin/env python3
"""Pryntor coding harness R2, deterministic, offline, advisory-only.

Proof-of-concept for the existing PRY-307 Jev evaluation branch. This is not
Jev inference, a real Codex/Claude hook, a sandbox or production authorization.
Do not send user/private source, model credentials, or customer data here.
"""
from __future__ import annotations

import argparse
import json
import re
from decimal import Decimal
from typing import Any

WORD = re.compile(r"[a-z0-9_]+")
STOP = frozenset({"a", "an", "and", "at", "by", "do", "for", "from", "in", "is", "it",
                  "of", "on", "or", "the", "this", "to", "with", "we", "why", "how"})
SENSITIVE = re.compile(r"(^|/)(\.env(?:\.[^/]*)?|\.ssh|secrets?|credentials?|private_keys?)(/|$)", re.I)
NETWORK = re.compile(r"\b(curl|wget|ssh|scp|nc|netcat|requests\.|urllib\.|socket\.|fetch\s*\(|http[s]?://)\b", re.I)
DANGEROUS = re.compile(r"\b(rm\s+-|chmod\b|chown\b|sudo\b|git\s+push\b|git\s+reset\b|deploy\b|publish\b)\b", re.I)
SHELL_META = re.compile(r"[;|&<>\x60$\n\r]")

# Only these capabilities can be exposed. There is no tool executor.
TOOLS = {
    "repo_search": {"snippet": "Search approved repository text (read-only).", "schema": {"query": "str", "paths": "list[str]"}},
    "file_read": {"snippet": "Read a selected, approved repository file.", "schema": {"path": "str"}},
    "test_request": {"snippet": "Propose a test to a separate approved runner, no execution here.", "schema": {"command": "str", "scope": "str"}},
}

# Entirely invented examples, never real private sources.
DEMO_CHUNKS: tuple[dict[str, Any], ...] = (
    {"id": "governance", "path": "AGENTS.md", "kind": "policy", "full":
     "Synthetic company policy: never spend, send email, merge, publish, or deploy without explicit human authorization. Every reported fix requires actual test evidence.",
     "short": "Human authorization required.", "long": "No spending or external changes; preserve independent tests."},
    {"id": "zow_safari", "path": "games/zowibo/safari_play_test.txt", "kind": "test", "full":
     "Synthetic Safari play button touch test: tapping the play button starts the canvas but a second touch does not update movement; retain pointercancel and blur checks.",
     "short": "Safari play test fails.", "long": "Safari play button touch starts canvas but follow-up movement stalls."},
    {"id": "zow_pointer", "path": "games/zowibo/camera_pointer.txt", "kind": "source", "full":
     "Synthetic pointer handling: track activePointerId, ignore wrong pointerup, handle touch pointercancel, reset on blur, and retain touch-safe camera state.",
     "short": "Pointer handler source.", "long": "Touch pointercancel and blur must reset the active camera pointer."},
    {"id": "zow_style", "path": "games/zowibo/typography.txt", "kind": "docs", "full":
     "Synthetic editorial reference for character lettering kerning typography captions readability desktop and 3D game title design.",
     "short": "Typography guide.", "long": "Character lettering and desktop readability notes."},
    {"id": "recover", "path": "apps/recover/sandbox_receipts.txt", "kind": "test", "full":
     "Synthetic PayPal sandbox receipts have no settlement proof and cannot count as recovered merchant cash or processor-confirmed revenue.",
     "short": "Recover sandbox note.", "long": "PayPal sandbox receipts must not be counted as revenue."},
    {"id": "robotics", "path": "robotics/simulator/ankle_delay.txt", "kind": "source", "full":
     "Synthetic ankle feedback robot simulator delayed action at ten milliseconds fails safety trial and needs independent controls review.",
     "short": "Robotics simulation note.", "long": "Ten millisecond actuator delay fails a simulation trial."},
)


def _words(text: str) -> set[str]:
    return {word for word in WORD.findall(text.lower()) if word not in STOP and len(word) > 1}


def _path(path: str) -> str:
    """Parse only relative POSIX repo paths; deny traversal and sensitive roots."""
    if type(path) is not str or not (1 <= len(path) <= 180):
        raise ValueError("invalid path")
    if path.startswith(("/", "~")) or "\\" in path or any(p in ("", ".", "..") for p in path.split("/")):
        raise ValueError("invalid relative path")
    if SENSITIVE.search(path):
        raise ValueError("sensitive path rejected")
    return path


def _validated_chunks(chunks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if type(chunks) is not list or not (1 <= len(chunks) <= 64):
        raise ValueError("invalid chunk collection")
    seen: set[str] = set()
    for row in chunks:
        if type(row) is not dict or set(row) != {"id", "path", "kind", "full", "short", "long"}:
            raise ValueError("unknown or missing chunk fields")
        cid = row["id"]
        if type(cid) is not str or not re.fullmatch(r"[a-z][a-z0-9_-]{0,49}", cid) or cid in seen:
            raise ValueError("invalid or duplicate chunk id")
        seen.add(cid)
        _path(row["path"])
        if row["kind"] not in ("policy", "source", "test", "docs", "log"):
            raise ValueError("invalid kind")
        for field in ("full", "short", "long"):
            if type(row[field]) is not str or not (1 <= len(row[field]) <= 8000):
                raise ValueError("chunk content missing or oversized")
    return chunks


def assemble_context(query: str, chunks: list[dict[str, Any]], *,
                     required_ids: tuple[str, ...] = (), word_budget: int = 1000) -> dict[str, Any]:
    """Return an immutable-looking proposal. Never truncate pinned policy or required evidence.

    All supplied abstracts are authored inputs, NOT trustworthy auto-summaries.
    Overlap is a simple deterministic baseline, not a Jev prediction or recall proof.
    """
    if type(query) is not str or not (2 <= len(query) <= 500) or not _words(query):
        raise ValueError("invalid query")
    if type(word_budget) is not int or not (20 <= word_budget <= 100_000):
        raise ValueError("invalid budget")
    chunks = _validated_chunks(chunks)
    ids = {c["id"] for c in chunks}
    if type(required_ids) is not tuple or not all(type(i) is str and i in ids for i in required_ids):
        raise ValueError("unknown required evidence")
    required = set(required_ids)
    q = _words(query)
    proposed = []
    for c in chunks:
        # Every policy is pinned; explicit evidence IDs are never compacted away.
        must = c["kind"] == "policy" or c["id"] in required
        relevant = len(q & _words(c["path"] + " " + c["full"]))
        level = "full" if must or relevant >= 3 else ("long" if relevant == 2 else ("short" if relevant == 1 else "hide"))
        proposed.append({"id": c["id"], "path": c["path"], "visibility": level,
                         "text": c["full"] if level == "full" else (c[level] if level != "hide" else ""),
                         "score": relevant, "required": must})
    cost = lambda rows: sum(len(r["text"].split()) for r in rows)
    # The optional results are reduced before mandatory evidence. No silent truncation.
    if cost([p for p in proposed if p["required"]]) > word_budget:
        raise ValueError("HOLD: policy or required evidence exceeds context budget")
    for p in sorted((p for p in proposed if not p["required"] and p["text"]),
                    key=lambda x: (x["score"], x["id"])):
        if cost(proposed) <= word_budget:
            break
        p["visibility"], p["text"] = "hide", ""
    if cost(proposed) > word_budget:
        raise ValueError("HOLD: incomplete budget plan")
    return {
        "status": "OFFLINE_ADVISORY_NOT_MODEL_CONTEXT_INJECTION",
        "query": query,
        "context": proposed,
        "word_proxy_full": sum(len(c["full"].split()) for c in chunks),
        "word_proxy_shown": cost(proposed),
        "required_preserved": all(p["visibility"] == "full" for p in proposed if p["required"]),
        "provider_calls": 0, "code_executed": False, "release_authorized": False,
    }


def capability_snippets() -> dict[str, str]:
    return {name: item["snippet"] for name, item in TOOLS.items()}


def inspect_tool_schema(name: str) -> dict[str, str]:
    if type(name) is not str or name not in TOOLS:
        raise ValueError("unregistered tool")
    return TOOLS[name]["schema"].copy()


def command_preflight(command: str, paths: list[str], script_source: str | None = None) -> dict[str, Any]:
    """Advisory ONLY: cannot inspect filesystem, shell semantics or isolation."""
    result = {"status": "HUMAN_REVIEW", "reason": "unproved_execution_safety",
              "command_executed": False, "permission_granted": False}
    if type(command) is not str or not (1 <= len(command) <= 500):
        return {**result, "status": "DENY", "reason": "invalid_command"}
    if type(paths) is not list or len(paths) > 32:
        return {**result, "status": "DENY", "reason": "invalid_path_list"}
    try:
        for p in paths:
            _path(p)
    except ValueError:
        return {**result, "status": "DENY", "reason": "unsafe_or_sensitive_path"}
    if SHELL_META.search(command) or DANGEROUS.search(command) or NETWORK.search(command):
        return {**result, "status": "DENY", "reason": "shell_or_risky_command"}
    if script_source is not None and (type(script_source) is not str or len(script_source) > 50_000):
        return {**result, "status": "DENY", "reason": "invalid_script_source"}
    if script_source and (NETWORK.search(script_source) or DANGEROUS.search(script_source)):
        return {**result, "status": "DENY", "reason": "risky_script_body"}
    if command in ("git status --short", "git diff --stat") and script_source is None:
        return {**result, "status": "READONLY_CANDIDATE", "reason": "requires_approved_runner"}
    return result


def route_cost_example(context_tokens: int, generated_tokens: int, tool_tokens: int,
                       *, trusted_data: bool = False) -> dict[str, Any]:
    """Hypothetical paper arithmetic only, prices in USD/1M; never schedules calls."""
    if any(type(x) is not int or x < 0 or x > 100_000_000 for x in (context_tokens, generated_tokens, tool_tokens)):
        raise ValueError("invalid token counts")
    x, y, z = map(Decimal, (context_tokens, generated_tokens, tool_tokens))
    divisor = Decimal(1_000_000)
    frontier_only = (25 * y + 5 * z) / divisor
    delegated = (3 * x + 20 * y + 8 * z) / divisor
    return {"frontier_only_usd": str(frontier_only), "delegated_usd": str(delegated),
            "route": "STAY_FRONTIER" if trusted_data or delegated >= frontier_only else "CHEAPER_ROUTE_REVIEW_ONLY",
            "model_calls": 0, "prices": "illustrative September 2026 PDF assumptions, not vendor quotes"}


def main() -> None:
    parser = argparse.ArgumentParser(description="R0 Jev coding harness principles, offline-only")
    parser.add_argument("operation", choices=["demo", "tools", "economics"])
    args = parser.parse_args()
    if args.operation == "demo":
        result = {"sample": "fictional_ZOWIBO_Safari_play_touch_failure",
                  "view": assemble_context("Fix ZOWIBO Safari play button touch and pointercancel",
                                           list(DEMO_CHUNKS), required_ids=("zow_safari",), word_budget=200),
                  "command_gate": command_preflight("python3 tools/fix.py", ["games/zowibo/camera_pointer.txt"],
                                                      "import requests\nrequests.post('https://example.invalid')"),
                  "tool_snippets": capability_snippets()}
    elif args.operation == "tools":
        result = {"tier1": capability_snippets(), "tier2_example": inspect_tool_schema("file_read")}
    else:
        result = route_cost_example(650_000, 120_000, 230_000)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
