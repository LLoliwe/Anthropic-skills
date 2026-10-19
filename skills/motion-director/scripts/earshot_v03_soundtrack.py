#!/usr/bin/env python3
"""Earshot 0.3 model-free sound kit -> frame-synchronised Motion Director WAV.

This is an optional private preview adapter, NOT a film release or model critique.
No weights, third-party recordings, uploaded data, paid APIs or external tools
other than the local Earshot CLI and (for muxing) FFmpeg are used.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys

EARSHOT_VERSION = "0.3.0"
BANK_VERSION = "forge_v2r6+fit1+pluck1"
SAMPLE_RATE = 48000
ROLE_BY_SHOT = {
    "hook": "tick",
    "toggle": "snap",
    "cards": "whoosh.short",
    "device": "click",
    "data": "pop",
    "cta": "hit",
}
# Deliberately small calm kit, not all 201 sounds. CC0 fitted source
# provenance lives in upstream docs/CREDITS_FIT.md, alongside MIT source.
SOUND_KIT = {
    "kit": 1,
    "name": "pryntor-motion-private-preview",
    "sr": SAMPLE_RATE,
    "roles": {
        "tick": {"sound": "fit/tick/domino", "takes": 1, "align": "onset", "level_db": -10.0},
        "snap": {"sound": "fit/snap/switch_flip", "takes": 1, "align": "onset", "level_db": -7.0},
        "whoosh.short": {"sound": "fit/whoosh.short/bamboo_swish", "takes": 1,
                         "align": "peak", "level_db": -12.0},
        "click": {"sound": "fit/click/floss_lid", "takes": 1, "align": "onset", "level_db": -8.0},
        "pop": {"sound": "fit/pop/mouth_plop", "takes": 1, "align": "onset", "level_db": -8.0},
        "hit": {"sound": "notify/m0", "takes": 1, "align": "onset", "level_db": -12.0},
    },
}

class SoundtrackError(ValueError):
    pass


def _positive_number(value, label):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
        raise SoundtrackError(f"{label} must be a positive finite number")
    return float(value)


def build_plan(film):
    """One real cue for each existing shot, anchored to its exact video frame."""
    if not isinstance(film, dict):
        raise SoundtrackError("film must be a JSON object")
    fps = _positive_number(film.get("fps"), "fps")
    if fps > 120 or fps != int(fps):
        raise SoundtrackError("fps must be an integer 1-120")
    shots = film.get("shots")
    if not isinstance(shots, list) or not shots or len(shots) > 100:
        raise SoundtrackError("expected 1-100 shots")
    cursor, seen, cues = 0, set(), []
    for shot in shots:
        if not isinstance(shot, dict):
            raise SoundtrackError("shot must be an object")
        shot_id = shot.get("id")
        if not isinstance(shot_id, str) or not shot_id or shot_id in seen:
            raise SoundtrackError("shot ids must be unique nonempty strings")
        seen.add(shot_id)
        kind = shot.get("type")
        if kind not in ROLE_BY_SHOT:
            raise SoundtrackError(f"{shot_id}: unsupported shot type {kind!r}; opt in with a reviewed mapping")
        frames_float = _positive_number(shot.get("duration"), f"{shot_id}.duration") * fps
        frames = round(frames_float)
        if frames < 3 or abs(frames - frames_float) > 1e-5:
            raise SoundtrackError(f"{shot_id}: duration must contain at least 3 whole frames")
        role = ROLE_BY_SHOT[kind]
        frame = cursor + min(frames - 1, max(1, frames // 2))
        cues.append({"shot": shot_id, "role": role, "frame": frame, "time_s": frame / fps})
        cursor += frames
    if cursor > fps * 180:
        raise SoundtrackError("maximum preview duration is 180 seconds")
    return {"fps": int(fps), "frames": cursor, "duration_s": cursor / fps, "cues": cues}


def _sha1(path):
    h = hashlib.sha1()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def checked_take(lock, role, outdir):
    """Do not play missing, modified, unaudited or ambiguously timed takes."""
    if lock.get("kit") != 1 or lock.get("earshot") != EARSHOT_VERSION or lock.get("bank") != BANK_VERSION:
        raise SoundtrackError("Earshot 0.3.0 / expected sound-bank lock required")
    if lock.get("sr") != SAMPLE_RATE:
        raise SoundtrackError("sound bank sample rate changed")
    roles = lock.get("roles")
    rec = roles.get(role) if isinstance(roles, dict) else None
    if not isinstance(rec, dict) or rec.get("sound") != SOUND_KIT["roles"][role]["sound"]:
        raise SoundtrackError(f"{role}: sound id differs from approved kit")
    if rec.get("align") != SOUND_KIT["roles"][role]["align"]:
        raise SoundtrackError(f"{role}: alignment changed")
    takes = rec.get("takes")
    if not isinstance(takes, list) or len(takes) != 1:
        raise SoundtrackError(f"{role}: exactly one audited take required")
    take = takes[0]
    fname = take.get("file")
    if not isinstance(fname, str) or fname != Path(fname).name or not fname.endswith(".wav"):
        raise SoundtrackError(f"{role}: unsafe sound filename")
    src = outdir / fname
    if src.is_symlink() or not src.is_file():
        raise SoundtrackError(f"{role}: take missing or a symlink")
    if not isinstance(take.get("sha1"), str) or _sha1(src) != take["sha1"]:
        raise SoundtrackError(f"{role}: take checksum mismatch")
    if take.get("checks") != []:
        raise SoundtrackError(f"{role}: upstream model-free audit warnings: {take.get('checks')}")
    if not math.isfinite(float(rec.get("level_db", float("nan")))) or rec["level_db"] > 0:
        raise SoundtrackError(f"{role}: unsafe gain")
    for field in ("onset_s", "peak_s", "end_s", "dur_s"):
        try:
            n = float(take[field])
        except (TypeError, ValueError, KeyError) as exc:
            raise SoundtrackError(f"{role}: missing/invalid {field}") from exc
        if not math.isfinite(n) or n < 0:
            raise SoundtrackError(f"{role}: invalid {field}")
    if not 0 <= take["onset_s"] <= take["peak_s"] <= take["dur_s"] + 0.005:
        raise SoundtrackError(f"{role}: impossible measured timing")
    return src, take, rec


def mix(plan, lock, takes_dir, output):
    """Sample-exact offline mix using the measured lockfile onset/peak."""
    import numpy as np
    import soundfile as sf

    frames = round(plan["frames"] * SAMPLE_RATE / plan["fps"])
    audio = np.zeros((frames, 2), dtype=np.float64)
    evidence = []
    for cue in plan["cues"]:
        src, take, spec = checked_take(lock, cue["role"], takes_dir)
        samples, sr = sf.read(src, always_2d=True, dtype="float32")
        if sr != SAMPLE_RATE or not 1 <= samples.shape[1] <= 2:
            raise SoundtrackError(f"{cue['role']}: sample rate or channel mismatch")
        if not np.isfinite(samples).all() or not np.max(np.abs(samples)) > 1e-5:
            raise SoundtrackError(f"{cue['role']}: silent/nonfinite take")
        if np.max(np.abs(samples)) > 1.00001:
            raise SoundtrackError(f"{cue['role']}: source samples clip")
        if samples.shape[1] == 1:
            samples = np.repeat(samples, 2, axis=1)
        align = take[spec["align"] + "_s"]
        expected = round(cue["frame"] * SAMPLE_RATE / plan["fps"])
        start = expected - round(align * SAMPLE_RATE)
        end = start + len(samples)
        if start < 0 or end > frames:
            raise SoundtrackError(f"{cue['role']}: sound overflows film; retime or change sound")
        audio[start:end] += samples * (10 ** (spec["level_db"] / 20))
        evidence.append({**cue, "sound": spec["sound"], "file": src.name,
                         "file_sha1": take["sha1"], "seed": take.get("seed"),
                         "align": spec["align"], "measured_align_s": align,
                         "offset_samples": start, "sync_error_ms": 0.0,
                         "source_audit_warnings": take["checks"]})
    peak = float(np.max(np.abs(audio)))
    if not math.isfinite(peak) or peak < 1e-5:
        raise SoundtrackError("rendered mix is silent")
    gain = min(1.0, (10 ** (-1.0 / 20)) / peak)
    audio *= gain
    output.parent.mkdir(parents=True, exist_ok=True)
    sf.write(output, audio, SAMPLE_RATE, subtype="PCM_24")
    return {"status": "rendered_technical_only", "earshot": EARSHOT_VERSION,
            "bank": BANK_VERSION, "sample_rate": SAMPLE_RATE, "frames": plan["frames"],
            "video_fps": plan["fps"], "duration_s": plan["duration_s"],
            "raw_mix_peak": peak, "safety_gain": gain, "cues": evidence,
            "wav_sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
            "rights": "Original synthetic film; Earshot MIT code; upstream CC0 fitted-sound sources tracked in docs/CREDITS_FIT.md",
            "human_audio_and_film_approval": False}


def _run(argv, env=None):
    p = subprocess.run(argv, capture_output=True, text=True, env=env, timeout=240, check=False)
    if p.returncode:
        raise SoundtrackError(f"{' '.join(map(str, argv[:5]))}: {p.stderr[-1400:] or p.stdout[-800:]}")
    return p


def render(film_path, outdir, video=None):
    """Generate actual bank WAV takes, frame-sync mix, optional review MP4."""
    film = json.loads(film_path.read_text(encoding="utf-8"))
    plan = build_plan(film)
    outdir.mkdir(parents=True, exist_ok=True)
    kit_path = outdir / "kit.json"
    takes = outdir / "takes"
    kit_path.write_text(json.dumps(SOUND_KIT, indent=2) + "\n", encoding="utf-8")
    env = dict(os.environ)
    env.update({"EARSHOT_OFFLINE": "1", "HF_HUB_OFFLINE": "1",
                "TRANSFORMERS_OFFLINE": "1", "HF_HUB_DISABLE_TELEMETRY": "1"})
    _run([sys.executable, "-m", "earshot", "kit", "render", str(kit_path),
          "--out", str(takes)], env)
    _run([sys.executable, "-m", "earshot", "kit", "check", str(kit_path),
          "--out", str(takes)], env)
    lock = json.loads((takes / "kit.lock.json").read_text(encoding="utf-8"))
    sound = outdir / "pryntor-motion-earshot-v03.wav"
    report = mix(plan, lock, takes, sound)
    if video:
        if not video.is_file():
            raise SoundtrackError(f"video missing: {video}")
        result = outdir / "pryntor-motion-earshot-v03-preview.mp4"
        _run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-nostdin", "-y",
              "-i", str(video), "-i", str(sound),
              "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy",
              "-c:a", "aac", "-b:a", "192k", "-shortest", str(result)])
        report["preview_mp4"] = str(result)
        report["preview_sha256"] = hashlib.sha256(result.read_bytes()).hexdigest()
    report["plan"] = plan
    (outdir / "soundtrack-evidence.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


def main():
    p = argparse.ArgumentParser(description="Pryntor Earshot 0.3 local sound-kit production, no models")
    p.add_argument("film", type=Path, help="existing Motion Director shot JSON")
    p.add_argument("--outdir", type=Path, default=Path("/tmp/pryntor-earshot-v03"))
    p.add_argument("--video", type=Path, help="optional existing local MP4, no external publishing")
    p.add_argument("--plan-only", action="store_true", help="dry-run exact frame times, no imports")
    args = p.parse_args()
    try:
        if args.plan_only:
            print(json.dumps(build_plan(json.loads(args.film.read_text(encoding="utf-8"))), indent=2))
        else:
            print(json.dumps(render(args.film, args.outdir, args.video), indent=2))
        return 0
    except (SoundtrackError, OSError, ValueError, subprocess.TimeoutExpired) as exc:
        print(f"earshot-v03: BLOCKED: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
