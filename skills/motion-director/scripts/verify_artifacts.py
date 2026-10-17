#!/usr/bin/env python3
"""Strict structural checks for original preview artifacts (not creative approval).

Renders can pass this gate while still needing music, rights and director review.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path


def checked_output(argv: list[str]) -> str:
    result = subprocess.run(argv, capture_output=True, text=True, check=False)
    if result.returncode:
        raise RuntimeError(f"{argv[0]} failed ({result.returncode}): {result.stderr[-1200:]}")
    return result.stdout


def verify_video(path: Path, duration: float, frames: int) -> dict:
    if not path.is_file() or path.stat().st_size < 1024:
        raise ValueError(f"Missing or undersized video: {path}")
    report = json.loads(checked_output([
        "ffprobe", "-v", "error", "-count_frames",
        "-show_entries", "format=duration:stream=codec_type,codec_name,width,height,nb_read_frames",
        "-of", "json", str(path)
    ]))
    videos = [s for s in report.get("streams", []) if s.get("codec_type") == "video"]
    if len(videos) != 1:
        raise ValueError(f"{path}: expected exactly one video stream")
    stream = videos[0]
    actual_seconds = float(report["format"]["duration"])
    if abs(actual_seconds - duration) > 0.05:
        raise ValueError(f"{path}: duration {actual_seconds}, expected {duration}")
    if int(stream.get("nb_read_frames") or 0) != frames:
        raise ValueError(f"{path}: frames {stream.get('nb_read_frames')}, expected {frames}")
    if (stream.get("codec_name"), stream.get("width"), stream.get("height")) != ("h264", 720, 720):
        raise ValueError(f"{path}: unexpected codec or dimensions: {stream}")
    # Real full-stream decoding is required; checking the MP4's size is insufficient.
    checked_output(["ffmpeg", "-nostdin", "-v", "error", "-xerror",
                    "-i", str(path), "-f", "null", "-"])
    return {"file": path.name, "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "bytes": path.stat().st_size, "codec": "h264", "width": 720,
            "height": 720, "frames": frames, "seconds": actual_seconds,
            "full_decode": "pass"}


def verify_handoff(directory: Path) -> dict:
    required = ("contact_sheet.png", "qa.json", "frame_qa.json", "storyboard.json",
                "edit_decision_list.csv", "editor_handoff.md", "provenance.json")
    for filename in required:
        path = directory / filename
        if not path.is_file() or path.stat().st_size == 0:
            raise ValueError(f"Missing handoff file: {path}")
    qa = json.loads((directory / "qa.json").read_text())
    frame_qa = json.loads((directory / "frame_qa.json").read_text())
    storyboard = json.loads((directory / "storyboard.json").read_text())
    provenance = json.loads((directory / "provenance.json").read_text())
    if qa["errors"] or qa["duration_seconds"] != 30:
        raise ValueError("Handoff QA has errors or incorrect duration")
    if len(frame_qa["shot_metrics"]) != 6 or len(storyboard["shots"]) != 6:
        raise ValueError("Unexpected shot count")
    if not storyboard.get("synthetic_demo") or not storyboard.get("rights"):
        raise ValueError("Synthetic origin or rights declaration missing")
    if any(s.get("approved") for s in storyboard["shots"]):
        raise ValueError("CI may not assign director approval to synthetic demo")
    if provenance.get("render_verified") is not False:
        raise ValueError("Handoff provenance must not assert renderer completion")
    return {"files": list(required), "timeline_qa": qa["status"],
            "timing_warnings": qa["warnings"], "frame_qa_warnings": frame_qa["warnings"],
            "director_approval": "not_given"}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rough", type=Path, required=True)
    parser.add_argument("--micro", type=Path, required=True)
    parser.add_argument("--handoff", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    summary = {
        "status": "verified_structural_preview_only",
        "videos": [verify_video(args.rough, 30.0, 720),
                   verify_video(args.micro, 5.0, 120)],
        "handoff": verify_handoff(args.handoff),
        "remaining_gates": [
            "Human visual and transition review",
            "Music selection and sound/rights verification",
            "Authentic product assets and claim verification",
            "Recorded director approval; no publication or automatic merge"
        ]
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
