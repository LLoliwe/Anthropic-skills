#!/usr/bin/env python3
"""One-shot *public free* ZeroGPU experiment. Does not create a paid job.

Safeguards:
- no Hugging Face token or billed account connection; anonymous public Space only
- no API key, credit top-up, recurring retry or vendor GPU invocation
- no confidential/private Pryntor source; all-original generic fictional subject
- failure reported as BLOCKED, not falsely labeled a rendered film
- requires manual director's review of movement and visual quality
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

SPACE = "Lightricks/LTX-2.5"
PROMPT = (
    "Single unbroken four-second cinematic 3D animated shot, no cuts, no still-image montage. "
    "An ORIGINAL little moon-blue felt-and-mohair creature, entirely fictional, with warm cream face, "
    "soft tufts, small articulated hands and feet, on a richly detailed nocturnal theatre rehearsal stage. "
    "At first it stands on its right foot, eyes tracking an off-screen sound, brows lifted with curiosity. "
    "The creature blinks and rotates its head toward the left, shoulders anticipate its next move, "
    "then takes a deliberate little sidestep, lifting and planting the left foot with visible weight transfer, "
    "then gives a small satisfied wave with its right arm. "
    "Camera smoothly trucks left through a foreground curtain and arcs around the character approximately 35 degrees "
    "while staying at child-eye level. Real dimensional parallax, crisp ground contact shadows, "
    "beautiful amber practicals and soft blue rim light, tactile individually lit soft fibers, premium film grade. "
    "Believable acting, independently animated limbs and cloth/fur dynamics, no character deformation, "
    "no changing identity, no logos, no typography, no other characters."
)


def safe_result(status: str, reason: str = "", **details) -> dict:
    return {"status": status, "reason": reason, "provider": SPACE,
            "target": "original continuous character acting and real spatial camera path",
            "cash_spend_authorized": False, "paid_api_invoked": False,
            "independent_visual_approval": False, **details}


def output_video_path(value) -> Path:
    if isinstance(value, str):
        return Path(value)
    if isinstance(value, dict):
        item = value.get("video") or value.get("path") or value.get("name")
        if isinstance(item, str):
            return Path(item)
        if isinstance(item, dict):
            return output_video_path(item)
    raise ValueError(f"Unexpected Gradio video result type: {type(value).__name__}")


def main() -> int:
    folder = Path(os.environ.get("OUTPUT_DIR", "output_lt25"))
    folder.mkdir(parents=True, exist_ok=True)
    evidence = folder / "status.json"
    start = time.monotonic()

    # Refuse any identity/billing keys. This is only a public, anonymous, quota-capped Space.
    prohibited = [k for k in ("HF_TOKEN", "HUGGING_FACE_HUB_TOKEN", "HUGGINGFACEHUB_API_TOKEN",
                              "OPENAI_API_KEY", "RUNWAY_API_KEY") if os.getenv(k)]
    if prohibited:
        evidence.write_text(json.dumps(safe_result("BLOCKED", "Env has credentials; public anonymous only",
                                                   credential_keys_present=prohibited), indent=2))
        print("BLOCKED: refusing to run public proof with auth/paid credentials in environment")
        return 0

    try:
        from gradio_client import Client
        print("Connecting to official free ZeroGPU demo anonymously; one attempt, no retries", flush=True)
        client = Client(SPACE, verbose=False, httpx_kwargs={"timeout":90.0})
        # Official app.py go.click(run, inputs=[prompt,image,height,width,duration,seed,decoder,
        # auto_len,randomize_seed,enhance_toggle]); default exported API name is /run.
        result = client.predict(PROMPT, None, 512, 768, 4.0, 42,
                                "conv", False, False, False, api_name="/run")
        if not isinstance(result, (list, tuple)) or len(result) < 1:
            raise RuntimeError("Unexpected public Space response shape")
        video_path = output_video_path(result[0])
        if not video_path.is_file() or video_path.stat().st_size < 25_000:
            raise RuntimeError("Returned file absent or too small for generated video")
        output = folder / "original_character_motion_PROOF_ONLY.mp4"
        shutil.copyfile(video_path, output)
        probe = subprocess.run(["ffprobe", "-v", "error", "-show_format", "-show_streams",
                                "-of", "json", str(output)], check=True,
                               text=True, capture_output=True)
        data = json.loads(probe.stdout)
        dur = float(data["format"].get("duration", 0.0))
        vid = next((s for s in data["streams"] if s.get("codec_type") == "video"), None)
        if not vid or not (2.5 <= dur <= 5.5):
            raise RuntimeError("Returned video failed duration/stream acceptance")
        record = safe_result("RENDERED_UNREVIEWED", "Free provider returned a playable video; human and motion QA pending",
                             duration_seconds=dur, width=vid.get("width"), height=vid.get("height"),
                             video=output.name, bytes=output.stat().st_size,
                             elapsed_seconds=round(time.monotonic()-start, 1))
        evidence.write_text(json.dumps(record, indent=2))
        print("RENDERED_UNREVIEWED", json.dumps(record), flush=True)
        return 0
    except Exception as exc:
        reason = f"{type(exc).__name__}: {str(exc)[:380]}"
        record = safe_result("BLOCKED", reason, elapsed_seconds=round(time.monotonic()-start, 1))
        evidence.write_text(json.dumps(record, indent=2))
        print("BLOCKED: free demo did not deliver an asset:", reason, flush=True)
        return 0  # quota/provider-blocked is not a fake pass; status.json is authoritative

if __name__ == "__main__":
    sys.exit(main())