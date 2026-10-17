#!/usr/bin/env python3
"""Read PUBLIC Lab Automation Forums Discourse topics; no credentials or writes.

Use only after checking forum terms and rate limits. Never run as a crawler.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

BASE = "https://labautomation.io"
USER_AGENT = "PryntorPublicForumResearch/0.1 (public-read-only; https://github.com/LLoliwe/Anthropic-skills)"
MAX_BYTES = 2_000_000


class PublicForumError(RuntimeError):
    """A request or data-shape problem, not a reason to request a password."""


def public_json(path: str) -> dict:
    """Fetch only a fixed set of public routes on the fixed Discourse host."""
    if not re.fullmatch(r"/(?:latest|categories)\.json|/c/[a-z0-9-]+/[0-9]+\.json", path):
        raise ValueError("Unsafe/unsupported public Discourse path")
    if os.environ.get("LABAUTOMATION_FORUM_WRITTEN_PERMISSION") != "YES":
        raise PublicForumError("Automated forum access disabled: operator permission required")
    req = Request(BASE + path, headers={"User-Agent": USER_AGENT, "Accept": "application/json"}, method="GET")
    try:
        with urlopen(req, timeout=15) as response:
            if response.geturl().split("/", 3)[:3] != ["https:", "", "labautomation.io"]:
                raise PublicForumError("Unexpected redirect outside forum host")
            raw = response.read(MAX_BYTES + 1)
    except (URLError, HTTPError, TimeoutError) as exc:
        raise PublicForumError(f"Public endpoint unavailable: {type(exc).__name__}") from exc
    if len(raw) > MAX_BYTES:
        raise PublicForumError("Oversized public endpoint response")
    try:
        payload = json.loads(raw)
    except (ValueError, UnicodeError) as exc:
        raise PublicForumError("Public endpoint did not return valid JSON") from exc
    if not isinstance(payload, dict):
        raise PublicForumError("Invalid public endpoint structure")
    return payload


def category_path(categories: dict, wanted: str) -> str:
    """Resolve category slug/name via returned public metadata; don't guess ids."""
    items = categories.get("category_list", {}).get("categories", [])
    if not isinstance(items, list):
        raise PublicForumError("Invalid category list")
    wanted = wanted.casefold().strip()
    for item in items:
        slug = item.get("slug") if isinstance(item, dict) else None
        name = item.get("name") if isinstance(item, dict) else None
        cid = item.get("id") if isinstance(item, dict) else None
        if (isinstance(slug, str) and slug.casefold() == wanted) or (isinstance(name, str) and name.casefold() == wanted):
            if not isinstance(cid, int) or cid < 1 or not isinstance(slug, str) or not re.fullmatch(r"[a-z0-9-]+", slug):
                raise PublicForumError("Invalid category metadata")
            return f"/c/{slug}/{cid}.json"
    raise PublicForumError(f"Unknown public category: {wanted}")


def clean_topics(payload: dict, categories: dict, maximum: int = 12, keywords: tuple[str, ...] = ()) -> list[dict]:
    """Keep only public topic metadata, retaining original attribution URLs."""
    if not 1 <= maximum <= 40:
        raise ValueError("maximum must be 1..40")
    raw_topics = payload.get("topic_list", {}).get("topics", [])
    if not isinstance(raw_topics, list):
        raise PublicForumError("Invalid topics list")
    catnames = {x["id"]: x["name"] for x in categories.get("category_list", {}).get("categories", [])
                if isinstance(x, dict) and type(x.get("id")) is int and isinstance(x.get("name"), str)}
    out = []
    for item in raw_topics:
        if not isinstance(item, dict):
            continue
        tid, title = item.get("id"), item.get("title")
        if type(tid) is not int or tid < 1 or not isinstance(title, str):
            continue
        if keywords and not any(k.casefold() in title.casefold() for k in keywords if k):
            continue
        post = item.get("last_posted_at") or item.get("created_at")
        out.append({
            "id": tid,
            "title": title[:300],
            "url": f"{BASE}/t/{tid}",
            "category": catnames.get(item.get("category_id"), "Unclassified"),
            "last_activity": post if isinstance(post, str) else None,
            "posts": item.get("posts_count") if type(item.get("posts_count")) is int else None,
            "source": "Lab Automation Forums (public Discourse feed)",
        })
    # Pinned topics can appear first in raw feeds despite old dates; sort for recency.
    out.sort(key=lambda x: x["last_activity"] or "", reverse=True)
    return out[:maximum]


def collect(category: str | None = None, maximum: int = 12, keywords: tuple[str, ...] = ()) -> dict:
    categories = public_json("/categories.json")
    path = category_path(categories, category) if category else "/latest.json"
    topics = clean_topics(public_json(path), categories, maximum, keywords)
    return {
        "provider": "Lab Automation Forums",
        "scope": "public-read-only",
        "feed": BASE + path,
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "count": len(topics),
        "topics": topics,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--category", help="Exact public category slug or name (e.g. open-source)")
    parser.add_argument("--limit", type=int, default=12, help="1-40 public topics, default 12")
    parser.add_argument("--keyword", action="append", default=[], help="Optional title substring match, repeatable")
    parser.add_argument("--format", choices=("json", "markdown"), default="markdown")
    args = parser.parse_args(argv)
    try:
        results = collect(args.category, args.limit, tuple(args.keyword))
    except (PublicForumError, ValueError) as exc:
        print(f"Forum read failed safely: {exc}", file=sys.stderr)
        return 2
    if args.format == "json":
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        print(f"# {results['provider']} — public read-only\n\nFeed: {results['feed']}\n")
        for topic in results["topics"]:
            title = re.sub(r"([\\\[\]()*_`])", r"\\\1", topic["title"]).replace("\n", " ")
            print(f"- [{title}]({topic['url']}) · {topic['category']} · {topic['last_activity'] or 'date unknown'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
