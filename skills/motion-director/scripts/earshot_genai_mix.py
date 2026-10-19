#!/usr/bin/env python3
"""Combine ONE original GenAI sound with Earshot v0.3 frame-synchronised takes.

A private review-stage adapter, not GenAI model hosting or release approval.
Requires the proven Earshot v0.3 take kit, provenance evidence and an actual
licensed-in-workspace GenAI audio file. Never downloads or invokes any model.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys

RATE = 48000
MODEL_ROLE = "snap"
BANK_VERSION = "forge_v2r6+fit1+pluck1"


class BridgeError(ValueError):
    pass


def digest(path: Path, algo="sha256"):
    h = hashlib.new(algo)
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def checked_source(proof: Path):
    """Load exact proven source and reject tampering/wrong model/source versions."""
    evidence = json.loads((proof / "soundtrack-evidence.json").read_text())
    lock = json.loads((proof / "takes" / "kit.lock.json").read_text())
    video = proof / "pryntor-motion-earshot-v03-preview.mp4"
    wav = proof / "pryntor-motion-earshot-v03.wav"
    if (evidence.get("earshot"), lock.get("earshot")) != ("0.3.0", "0.3.0"):
        raise BridgeError("Earshot 0.3.0 receipts required")
    if evidence.get("bank") != BANK_VERSION or lock.get("bank") != BANK_VERSION:
        raise BridgeError("different or unknown Earshot sound bank")
    if evidence.get("sample_rate") != RATE or lock.get("sr") != RATE:
        raise BridgeError("unexpected sample rate")
    if digest(video) != evidence.get("preview_sha256") or digest(wav) != evidence.get("wav_sha256"):
        raise BridgeError("original verified MP4/WAV changed")
    if evidence.get("duration_s") != 30.0 or evidence.get("video_fps") != 24:
        raise BridgeError("this approved review fixture is 30s, 24fps")
    cues = evidence.get("cues")
    if not isinstance(cues, list) or len(cues) != 6:
        raise BridgeError("expected exactly six source cues")
    roles = [c.get("role") for c in cues]
    if len(set(roles)) != 6 or roles.count(MODEL_ROLE) != 1:
        raise BridgeError("invalid cue roles")
    return evidence, lock, video


def pcm(audio_file: Path, tmp_path: Path):
    """Decode to local 48kHz stereo float WAV (no upload)."""
    if not audio_file.is_file() or audio_file.is_symlink():
        raise BridgeError("generated audio missing or symlink")
    p = subprocess.run(["ffmpeg", "-nostdin", "-hide_banner", "-loglevel", "error", "-y",
                        "-i", str(audio_file), "-vn", "-ar", str(RATE),
                        "-ac", "2", "-c:a", "pcm_f32le", str(tmp_path)],
                       capture_output=True, text=True, timeout=90)
    if p.returncode or not tmp_path.is_file():
        raise BridgeError("GenAI audio decode failed: " + p.stderr[-300:])
    import soundfile as sf
    audio, sr = sf.read(tmp_path, always_2d=True, dtype="float64")
    if sr != RATE or audio.ndim != 2 or audio.shape[1] != 2:
        raise BridgeError("generated audio is not 48k stereo")
    return audio


def onset_samples(audio):
    """First 1ms RMS window within 30dB of maximum 1ms RMS."""
    import numpy as np
    if not 0.15 * RATE <= len(audio) <= 30 * RATE:
        raise BridgeError("generated effect must be between 0.15 and 30 seconds")
    if not np.isfinite(audio).all():
        raise BridgeError("generated effect contains nonfinite samples")
    pk = float(np.max(np.abs(audio)))
    if not 0.001 < pk < 1.2:
        raise BridgeError("generated effect silent or clipped")
    win = RATE // 1000
    env = np.sqrt(np.mean(np.square(audio[: len(audio) // win * win].reshape(-1, win, 2)),
                          axis=(1, 2)))
    if not len(env) or float(env.max()) < 0.0001:
        raise BridgeError("generated effect lacks measurable onset")
    ix = np.flatnonzero(env >= float(env.max()) * 10 ** (-30 / 20))
    if not len(ix):
        raise BridgeError("generated effect onset undetected")
    return int(ix[0]) * win, pk


def video_hash(video):
    """Checks compressed video packet stream identity, not just shape."""
    p = subprocess.run(["ffmpeg", "-nostdin", "-loglevel", "error",
                        "-i", str(video), "-map", "0:v:0", "-c:v", "copy",
                        "-f", "md5", "-"], capture_output=True, text=True, timeout=90)
    if p.returncode or not p.stdout.startswith("MD5="):
        raise BridgeError("could not verify video packet hash")
    return p.stdout.strip().split("=", 1)[1]


def create_mix(proof_root: Path, ai_file: Path, outdir: Path, *,
               model_name: str, task_id: str):
    """Preserve five vetted bank takes, replace S02 snap with GenAI foley."""
    if not model_name or not task_id or len(model_name) > 200 or len(task_id) > 200:
        raise BridgeError("model name and generation task ID are required")
    import numpy as np
    import soundfile as sf
    evidence, lock, video = checked_source(proof_root)
    outdir.mkdir(parents=True, exist_ok=True)
    generated = pcm(ai_file, outdir / "genai-resampled-48k.wav")
    onset, ai_pk = onset_samples(generated)
    # Fade edge boundaries without changing the source recording.
    fade = min(len(generated) // 2, round(0.005 * RATE))
    generated[:fade] *= np.linspace(0, 1, fade)[:, None]
    fadeout = min(len(generated) // 2, round(0.055 * RATE))
    generated[-fadeout:] *= np.linspace(1, 0, fadeout)[:, None]
    # The original snap kit uses -7 dB relative to normalized take; -9 for
    # generated foley allows the new organic sound to sit below the visuals.
    generated *= (10 ** (-9 / 20)) / ai_pk
    total = int(evidence["duration_s"] * RATE)
    mix = np.zeros((total, 2), dtype=np.float64)
    placed = []
    for cue in evidence["cues"]:
        role = cue["role"]
        target = round(cue["frame"] * RATE / evidence["video_fps"])
        if role == MODEL_ROLE:
            signal = generated
            sync_point = onset
            source = "genai"
            name = ai_file.name
            sha = digest(ai_file)
            if len(signal) > RATE * 4:
                raise BridgeError("AI toggle effect exceeds 4 seconds")
        else:
            rec = lock["roles"].get(role)
            if not isinstance(rec, dict) or len(rec.get("takes", [])) != 1:
                raise BridgeError(f"{role}: missing locked Earshot take")
            take = rec["takes"][0]
            if take.get("checks") != []:
                raise BridgeError(f"{role}: original Earshot audit warning")
            name = take["file"]
            if name != Path(name).name or not name.endswith(".wav"):
                raise BridgeError(f"{role}: unsafe take filename")
            path = proof_root / "takes" / name
            if path.is_symlink() or not path.is_file() or digest(path, "sha1") != take.get("sha1"):
                raise BridgeError(f"{role}: take missing or checksum changed")
            signal, sr = sf.read(path, always_2d=True, dtype="float64")
            if sr != RATE or not 1 <= signal.shape[1] <= 2 or not np.isfinite(signal).all():
                raise BridgeError(f"{role}: invalid take audio")
            if signal.shape[1] == 1:
                signal = np.repeat(signal, 2, axis=1)
            if not isinstance(rec.get("level_db"), (float, int)) or not math.isfinite(rec["level_db"]):
                raise BridgeError(f"{role}: invalid locked gain")
            signal *= 10 ** (rec["level_db"] / 20)
            sync_point = round(float(take[rec["align"] + "_s"]) * RATE)
            # Reproduce original sample-placement arithmetic exactly.
            if target - sync_point != cue["offset_samples"]:
                raise BridgeError(f"{role}: original timing was modified")
            source, sha = "earshot_0.3.0_bank", digest(path, "sha1")
        start = target - sync_point
        if start < 0 or start + len(signal) > total:
            raise BridgeError(f"{role}: audio extends outside the film")
        mix[start : start + len(signal)] += signal
        placed.append({"shot": cue["shot"], "role": role, "frame": cue["frame"],
                       "time_s": cue["time_s"], "sample": target,
                       "source": source, "file": name, "source_sha": sha,
                       "measured_onset_or_peak_s": round(sync_point / RATE, 5),
                       "sync_error_ms": 0.0})
    pk = float(np.max(np.abs(mix)))
    if not 0.00001 < pk < 20 or not math.isfinite(pk):
        raise BridgeError("mixed audio silent or nonfinite")
    safety_gain = min(1.0, 10 ** (-1 / 20) / pk)
    mix *= safety_gain
    out_wav = outdir / "pryntor-earshot-v03-plus-genai.wav"
    sf.write(out_wav, mix, RATE, subtype="PCM_24")
    out_mp4 = outdir / "pryntor-motion-earshot-v03-plus-genai.mp4"
    ff = subprocess.run(["ffmpeg", "-nostdin", "-hide_banner", "-loglevel", "error", "-y",
                         "-i", str(video), "-i", str(out_wav),
                         "-map", "0:v:0", "-map", "1:a:0",
                         "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                         "-shortest", "-movflags", "+faststart", str(out_mp4)],
                        capture_output=True, text=True, timeout=100)
    if ff.returncode:
        raise BridgeError("video mux failed: " + ff.stderr[-400:])
    original_video_md5 = video_hash(video)
    hybrid_video_md5 = video_hash(out_mp4)
    if original_video_md5 != hybrid_video_md5:
        raise BridgeError("visual pixels/codec stream changed unexpectedly")
    if digest(out_mp4) == digest(video):
        raise BridgeError("hybrid output did not change")
    qa = subprocess.run(["ffmpeg", "-nostdin", "-hide_banner", "-v", "info", "-xerror",
                         "-i", str(out_mp4), "-map", "0:a:0",
                         "-af", "volumedetect", "-f", "null", "-"],
                        capture_output=True, text=True, timeout=90)
    if qa.returncode or "max_volume:" not in qa.stderr:
        raise BridgeError("unable to decode/measure finished audio")
    report = {
        "status": "rendered_technical_only", "production_approved": False,
        "film_duration_s": evidence["duration_s"], "fps": evidence["video_fps"],
        "audio_sample_rate": RATE, "earshot_version": "0.3.0",
        "earshot_preserved_cues": 5, "genai_inserted_cues": 1,
        "genai_model": model_name, "genai_task_id": task_id,
        "genai_sha256": digest(ai_file), "genai_original_peak": ai_pk,
        "genai_measured_onset_s": onset / RATE,
        "genai_disposition": "original model-generated sound, locally decoded and framed to picture",
        "genai_license": "provider commercial-use terms and asset rights require human review",
        "source_video_sha256": digest(video), "video_packet_md5": original_video_md5,
        "video_stream_identical": True, "source_earshot_wav_sha256": evidence["wav_sha256"],
        "output_wav_sha256": digest(out_wav), "output_mp4_sha256": digest(out_mp4),
        "peak_pre_safety": pk, "mix_safety_gain": safety_gain,
        "cues": placed, "audio_technical_meter_tail": qa.stderr[-1250:],
        "human_creative_review": "required", "human_rights_review": "required",
        "no_new_ventures_or_publication": True,
    }
    (outdir / "hybrid-evidence.json").write_text(json.dumps(report, indent=2) + "\n")
    return report


def main():
    ap = argparse.ArgumentParser(description="Private Earshot 0.3 + GenAI original SFX merge")
    ap.add_argument("--proof-root", type=Path, required=True)
    ap.add_argument("--genai-audio", type=Path, required=True)
    ap.add_argument("--outdir", type=Path, required=True)
    ap.add_argument("--model", required=True)
    ap.add_argument("--task-id", required=True)
    a = ap.parse_args()
    try:
        print(json.dumps(create_mix(a.proof_root, a.genai_audio, a.outdir,
                                    model_name=a.model, task_id=a.task_id), indent=2))
        return 0
    except (BridgeError, OSError, ValueError, subprocess.TimeoutExpired) as exc:
        print(f"GenAI/Earshot audio bridge BLOCKED: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
