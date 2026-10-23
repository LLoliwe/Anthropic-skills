#!/usr/bin/env python3
"""Execute a fixed, offline QA workcell for existing PRY-309 source.

No LLM provision, no arbitrary task commands, no write to code, no external
messages or payment authority. A hosted runner is NOT a no-egress sandbox.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

ROOT_PATH = Path("tools/pryntor-improvement-loop")
SOURCE = ("agent_workcells.py", "founder_dispatch.py", "loop.py", "workcell_execute.py")
TESTS = ("test_agent_workcells.py", "test_founder_dispatch.py", "test_loop.py", "test_workcell_execute.py")
CMD = (sys.executable, "-m", "unittest", "discover", "-s", str(ROOT_PATH), "-p", "test_*.py", "-v")
COUNT = re.compile(r"^Ran\s+(\d+)\s+tests\s+in\s+[\d.]+s$", re.M)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def source_snapshot(root):
    """Fail closed for missing/symlink/oversize protected source or test."""
    result = {}
    for name in SOURCE + TESTS:
        f = root / ROOT_PATH / name
        if f.is_symlink() or not f.is_file() or f.stat().st_size > 250_000:
            raise ValueError("Protected source missing, linked or oversized: " + name)
        result[str(ROOT_PATH / name)] = sha(f.read_bytes())
    return result


def run_workcell(root, execute=None):
    """Run one reviewed static command, not a generic process executor."""
    root = Path(root).resolve(strict=True)
    before = source_snapshot(root)
    executor = execute or subprocess.run
    with tempfile.TemporaryDirectory(prefix="pryntor-qa-home-") as home:
        safe_env = {
            "HOME": home,
            "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
            "PYTHONDONTWRITEBYTECODE": "1",
            "PYTHONNOUSERSITE": "1",
            "PYTHONPATH": "",
            "LANG": "C.UTF-8",
        }
        try:
            proc = executor(list(CMD), cwd=str(root), env=safe_env, text=True,
                            capture_output=True, timeout=75, check=False)
            log = (proc.stdout or "") + "\n" + (proc.stderr or "")
            code = proc.returncode
            timed_out = False
        except subprocess.TimeoutExpired as exc:
            log, code, timed_out = str(exc), -1, True
    after = source_snapshot(root)
    match = COUNT.search(log)
    n = int(match.group(1)) if match else 0
    passed = bool(code == 0 and match and n >= 1 and
                  re.search(r"^OK\s*$", log, re.M) and
                  before == after and not timed_out)
    receipt = {
        "schema_version": 1,
        "status": "QA_EXECUTED_REVIEW_REQUIRED" if passed else "HOLD_QA_FAILED",
        "issue": "PRY-309", "repo": "LLoliwe/Anthropic-skills",
        "kind": "bounded_offline_qa_workcell",
        "ran_at_utc": datetime.now(timezone.utc).isoformat(),
        "stages": ["source_inventory", "run_real_unit_tests", "verify_source_immutability"],
        "before": before, "after": after,
        "source_immutable": before == after,
        "test_argv": list(CMD), "test_count": n,
        "exit_code": code, "timed_out": timed_out,
        "test_log_sha256": sha(log.encode("utf-8")),
        "model_workers_provisioned": 0,
        "external_calls": 0, "spend_authorized": False,
        "independent_human_review": "PENDING",
        "product_impact": "NOT_ASSESSED",
        "release_authorized": False,
        "warning": "GitHub Actions runner is not a no-egress sandbox or independent reviewer.",
    }
    return receipt, log


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    root, out = args.root.resolve(), args.out.resolve()
    if out == root or root in out.parents:
        parser.error("Receipt path must be outside checked-out repository")
    out.mkdir(parents=True, exist_ok=True)
    try:
        rec, log = run_workcell(root)
    except (ValueError, OSError) as exc:
        rec = {"status": "HOLD_PRECHECK_FAILED", "issue": "PRY-309",
               "execution_started": False, "release_authorized": False,
               "reason": str(exc)}
        log = ""
    (out / "receipt.json").write_text(json.dumps(rec, indent=2, sort_keys=True) + "\n")
    (out / "tests.log").write_text(log)
    summary = [
        "# Pryntor QA Workcell: executed source verification",
        "- Issue: PRY-309",
        "- Status: " + rec["status"],
        "- Unit tests observed: " + str(rec.get("test_count", 0)),
        "- Tests log SHA-256: " + rec.get("test_log_sha256", "UNKNOWN"),
        "- Model-backed agents activated: 0",
        "- Review: PENDING",
        "- Product acceptance: NOT ASSESSED",
        "- Release: HOLD",
        "",
        "This verifies a real offline QA execution, not a production AI-agent deployment.",
    ]
    (out / "summary.md").write_text("\n".join(summary) + "\n")
    print(json.dumps({"status": rec["status"], "test_count": rec.get("test_count", 0)}))
    return 0 if rec["status"] == "QA_EXECUTED_REVIEW_REQUIRED" else 2


if __name__ == "__main__":
    sys.exit(main())
