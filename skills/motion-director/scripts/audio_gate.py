#!/usr/bin/env python3
"""Motion Director audio QA gate. Offline, stdlib-only; ffmpeg/ffprobe required.

Optional Earshot 0.2.0 model review is explicit and offline-only; never calls a
paid API or installs/downloads packages. Measures audio existence, decode,
sample peak and mean volume. It cannot judge aesthetic quality or rights.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys


def command(argv: list[str], env: dict | None = None) -> subprocess.CompletedProcess:
    try:
        p = subprocess.run(argv, capture_output=True, text=True, timeout=120, env=env, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise RuntimeError(f"Cannot run {argv[0]}: {exc}") from exc
    return p


def inspect_audio(media: Path, *, min_mean_dbfs: float = -45.0,
                  max_peak_dbfs: float = -0.5, intentional_mute: str = "") -> dict:
    if not media.is_file() or media.stat().st_size <= 0:
        raise ValueError(f"Missing or empty media file: {media}")
    probe = command(["ffprobe", "-v", "error", "-show_entries",
                     "stream=codec_type,codec_name:format=duration", "-of", "json", str(media)])
    if probe.returncode:
        raise RuntimeError("ffprobe failed: " + probe.stderr[-600:])
    metadata = json.loads(probe.stdout)
    streams = [s for s in metadata.get("streams", []) if s.get("codec_type") == "audio"]
    problems = []
    warnings = []
    duration = float(metadata.get("format", {}).get("duration", 0))
    if duration <= 0:
        problems.append("no_positive_duration")
    digest = hashlib.sha256()
    with media.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    sha256 = digest.hexdigest()
    info = {"file": str(media), "sha256": sha256, "duration_seconds": duration,
            "audio_streams": len(streams), "audio_codec": streams[0].get("codec_name") if streams else None,
            "mean_dbfs": None, "max_sample_peak_dbfs": None, "failures": problems,
            "warnings": warnings, "intentional_mute_note": intentional_mute or None,
            "earshot": {"status": "not_requested"}}
    if not streams:
        if intentional_mute.strip():
            warnings.append("audio_absent_intentionally: director_must_approve")
        else:
            problems.append("audio_stream_missing")
        info["status"] = "fail" if problems else "pass_with_warnings"
        return info
    check = command(["ffmpeg", "-hide_banner", "-nostdin", "-v", "info", "-xerror",
                     "-i", str(media), "-map", "0:a:0", "-af", "volumedetect",
                     "-f", "null", "-"])
    if check.returncode:
        problems.append("audio_decode_failed")
        warnings.append(check.stderr[-300:])
    else:
        mean = re.findall(r"mean_volume:\s*([-+\w.]+)\s*dB", check.stderr)
        peak = re.findall(r"max_volume:\s*([-+\w.]+)\s*dB", check.stderr)
        if not mean or not peak:
            problems.append("audio_metrics_missing")
        else:
            def parse_db(v: str) -> float:
                return -999.0 if v == "-inf" else float(v)
            info["mean_dbfs"] = parse_db(mean[-1])
            info["max_sample_peak_dbfs"] = parse_db(peak[-1])
            if info["mean_dbfs"] < min_mean_dbfs:
                if intentional_mute.strip():
                    warnings.append("very_quiet_audio_intentional: director_must_approve")
                else:
                    problems.append("audio_too_quiet")
            if info["max_sample_peak_dbfs"] > max_peak_dbfs:
                problems.append("sample_peak_exceeds_limit")
    info["status"] = "fail" if problems else "pass_with_warnings" if warnings else "pass_technical_only"
    return info


def earshot_review(media: Path) -> dict:
    """Explicit opt-in, offline, no automatic package/model fetch."""
    if importlib.util.find_spec("earshot") is None:
        return {"status": "blocked", "reason": "earshot_not_installed"}
    env = dict(os.environ)
    env["EARSHOT_OFFLINE"] = "1"
    env["HF_HUB_OFFLINE"] = "1"
    env["TRANSFORMERS_OFFLINE"] = "1"
    p = command([sys.executable, "-m", "earshot", "critique", str(media), "--json"], env=env)
    if p.returncode:
        return {"status": "blocked", "reason": "offline_model_run_failed",
                "stderr_tail": p.stderr[-500:]}
    try:
        data = json.loads(p.stdout)
    except json.JSONDecodeError:
        return {"status": "blocked", "reason": "invalid_earshot_json"}
    if (not isinstance(data, dict) or not data.get("metrics") or data.get("partial") != []
            or data.get("verdict") not in {"launch-grade", "close", "needs work", "not launch-grade"}):
        return {"status": "blocked", "reason": "incomplete_earshot_critique"}
    return {"status": "completed_model_assist_only", "data": data,
            "production_ready": False,
            "limitations": "Unverified subjective taste, licensing, reference fit and director approval"}


def main() -> int:
    parser = argparse.ArgumentParser(description="Pryntor Studios offline audio technical QA")
    parser.add_argument("media", type=Path)
    parser.add_argument("--report", type=Path, help="Write JSON evidence report")
    parser.add_argument("--min-mean-dbfs", type=float, default=-45.0)
    parser.add_argument("--max-peak-dbfs", type=float, default=-0.5)
    parser.add_argument("--intentional-mute", default="", help="Reason for intentionally silent work")
    parser.add_argument("--earshot-review", action="store_true", help="Opt-in installed model review, offline only")
    args = parser.parse_args()
    try:
        report = inspect_audio(args.media, min_mean_dbfs=args.min_mean_dbfs,
                               max_peak_dbfs=args.max_peak_dbfs,
                               intentional_mute=args.intentional_mute)
        if args.earshot_review:
            report["earshot"] = earshot_review(args.media)
            if report["earshot"]["status"] != "completed_model_assist_only":
                report["failures"].append("earshot_review_requested_but_unavailable")
                report["status"] = "fail"
        if args.report:
            args.report.parent.mkdir(parents=True, exist_ok=True)
            args.report.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
        print(json.dumps(report, indent=2, allow_nan=False))
        return 0 if not report["failures"] else 1
    except Exception as exc:
        print(json.dumps({"status": "fail", "error": str(exc)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
