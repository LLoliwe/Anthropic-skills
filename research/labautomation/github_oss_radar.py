#!/usr/bin/env python3
"""Pryntor's allowlisted open-source lab automation GitHub metadata snapshot.

No credentials required, no repo clone, no comments, no third-party forum polling.
Uses GitHub's official public repository API under normal API limits. Repository
metadata and license identifiers are leads to evaluate, not legal certification.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, Request, build_opener

API = "https://api.github.com/repos/"
REPOS = (
    "PyLabRobot/pylabrobot", "AD-SDL/MADSci", "emdgroup/baybe",
    "pachterlab/poseidon", "Mokey2002/OpenLIMS", "AD-SDL/wei",
    "Opentrons/opentrons", "Edinburgh-Genome-Foundry/Plateo",
    "sciencecorp/galago-core", "sciencecorp/galago-tools",
)
MAX_BYTES = 250_000


class RepoFetchError(RuntimeError):
    pass


class RefuseRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def open_no_redirect(req, timeout=12):
    return build_opener(RefuseRedirect()).open(req, timeout=timeout)


def fetch_one(repo: str, opener=open_no_redirect, token: str = "") -> dict:
    if repo not in REPOS:
        raise ValueError("Only allowlisted GitHub repositories are permitted")
    url = API + repo
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "PryntorOSSResearch/0.1", "X-GitHub-Api-Version": "2022-11-28"}
    if token:
        headers["Authorization"] = "Bearer " + token
    req = Request(url, headers=headers, method="GET")
    try:
        with opener(req, timeout=12) as response:
            if response.geturl() != url:
                raise RepoFetchError("unexpected API redirect")
            raw = response.read(MAX_BYTES + 1)
    except (HTTPError, URLError, TimeoutError) as exc:
        raise RepoFetchError("GitHub API request unavailable or rate-limited") from exc
    if len(raw) > MAX_BYTES:
        raise RepoFetchError("GitHub response exceeds size limit")
    try:
        obj = json.loads(raw)
    except (ValueError, UnicodeError) as exc:
        raise RepoFetchError("Invalid GitHub JSON response") from exc
    if not isinstance(obj, dict) or obj.get("full_name", "").casefold() != repo.casefold():
        raise RepoFetchError("Unexpected GitHub repository identity")
    license_obj = obj.get("license")
    return {
        "repository": repo,
        "url": "https://github.com/" + repo,
        "description": str(obj.get("description") or "")[:250],
        "default_branch": obj.get("default_branch") if isinstance(obj.get("default_branch"), str) else None,
        "last_pushed_at": obj.get("pushed_at") if isinstance(obj.get("pushed_at"), str) else None,
        "last_metadata_update_at": obj.get("updated_at") if isinstance(obj.get("updated_at"), str) else None,
        "archived": obj.get("archived") is True,
        "github_license_spdx": license_obj.get("spdx_id") if isinstance(license_obj, dict) and isinstance(license_obj.get("spdx_id"), str) else None,
        "license_certified": False,
    }


def collect(opener=open_no_redirect, token: str = "", max_repos: int | None = None) -> dict:
    if max_repos is not None and not 1 <= max_repos <= len(REPOS):
        raise ValueError("max_repos outside fixed allowlist")
    entries, errors = [], []
    for repo in REPOS[:max_repos]:
        try:
            entries.append(fetch_one(repo, opener=opener, token=token))
        except RepoFetchError as exc:
            errors.append({"repository": repo, "error": str(exc)})
    return {"source": "GitHub public repository API", "scope": "allowlisted-metadata-only",
            "collected_at_utc": datetime.now(timezone.utc).isoformat(), "count": len(entries),
            "failed": len(errors), "repositories": entries, "errors": errors,
            "notes": "GitHub license metadata is not a legal audit. No forum scraping, private data or automatic deployment."}


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--max-repos", type=int, default=None, help="limit API calls during verification")
    args = p.parse_args(argv)
    try:
        report = collect(token=os.environ.get("GITHUB_TOKEN", ""), max_repos=args.max_repos)
    except ValueError as exc:
        print(f"Config error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if report["failed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
