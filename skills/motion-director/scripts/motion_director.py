#!/usr/bin/env python3
"""Motion Director: deterministic seek(t) motion, real MP4, storyboard and QA.

No external model calls. Original illustrative UI only.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageChops, ImageStat

IVORY = "#F4F1E8"
INK = "#171C1A"
LIME = "#C5F241"
MUTED = "#767D76"
PANEL = "#E6E8DF"
WHITE = "#FFFFFF"
KINDS = {"hook", "toggle", "cards", "device", "data", "cta"}


def clamp(x: float, a: float = 0, b: float = 1) -> float:
    return max(a, min(b, x))


def ease(x: float) -> float:
    x = clamp(x)
    return 1 - (1 - x) ** 3


def mix(a: float, b: float, x: float) -> float:
    return a + (b - a) * x


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load(path: Path) -> dict:
    p = json.loads(path.read_text(encoding="utf-8"))
    if not p.get("shots"):
        raise ValueError("Project must contain at least one shot")
    if not 1 <= int(p.get("fps", 24)) <= 60:
        raise ValueError("FPS must be 1–60")
    if not 1 <= int(p.get("width", 720)) <= 3840 or not 1 <= int(p.get("height", 720)) <= 3840:
        raise ValueError("Invalid dimensions")
    if not 40 <= float(p.get("bpm", 120)) <= 240:
        raise ValueError("BPM must be 40–240")
    if any(float(s.get("duration", 0)) <= 0 for s in p["shots"]):
        raise ValueError("Every shot requires positive duration")
    if any(s.get("type") not in KINDS for s in p["shots"]):
        raise ValueError("Unknown shot type")
    if len({s["id"] for s in p["shots"]}) != len(p["shots"]):
        raise ValueError("Duplicate shot IDs")
    if duration(p) > 60:
        raise ValueError("Script must remain under 60 seconds")
    return p


def duration(p: dict) -> float:
    return sum(float(s["duration"]) for s in p["shots"])


def timeline(p: dict) -> list[dict]:
    cursor = 0.0
    result = []
    for s in p["shots"]:
        end = cursor + float(s["duration"])
        result.append({"shot": s, "start": cursor, "end": end})
        cursor = end
    return result


def shot_at(p: dict, seconds: float) -> tuple[dict, float]:
    seconds = clamp(seconds, 0, max(0, duration(p) - 0.00001))
    for row in timeline(p):
        if seconds < row["end"]:
            return row["shot"], (seconds - row["start"]) / float(row["shot"]["duration"])
    return p["shots"][-1], 1.0


def inspect(p: dict, require_approval: bool = False) -> dict:
    errors, warnings, measurements = [], [], []
    bpm = float(p.get("bpm", 120))
    beat = 60 / bpm
    for row in timeline(p):
        s = row["shot"]
        sid = s["id"]
        d = float(s["duration"])
        if not 2 <= d <= 9:
            warnings.append(f"{sid}: duration {d:g}s outside 2–9s editorial guide")
        if not 2 <= len(s.get("actions", [])) <= 3:
            warnings.append(f"{sid}: use 2–3 connected actions")
        if not s.get("annotation", "").strip():
            warnings.append(f"{sid}: missing motion annotation")
        if len(s.get("headline", "")) > 52:
            warnings.append(f"{sid}: headline may exceed safe area")
        offset = abs(row["end"] / beat - round(row["end"] / beat)) * beat
        measurements.append({"id": sid, "start": round(row["start"], 3),
                             "end": round(row["end"], 3), "duration": d,
                             "beat_offset_seconds": round(offset, 4),
                             "approved": bool(s.get("approved", False))})
        if offset > 0.14:
            warnings.append(f"{sid}: cut {offset:.2f}s from nearest {bpm:g} BPM beat")
        if require_approval and not s.get("approved", False):
            errors.append(f"{sid}: not approved by director")
    if p["shots"][-1]["type"] != "cta":
        warnings.append("Final shot should resolve into an explicit CTA")
    if not p.get("music"):
        warnings.append("No music supplied: beat grid is a tempo guide, not audio onset analysis")
    for s in p["shots"]:
        if s.get("asset") and not Path(s["asset"]).exists():
            errors.append(f"{s['id']}: referenced screenshot does not exist")
    if not p.get("rights"):
        errors.append("Missing asset/music rights declaration")
    return {"status": "fail" if errors else "pass_with_warnings" if warnings else "pass",
            "duration_seconds": round(duration(p), 3), "bpm": bpm,
            "errors": errors, "warnings": warnings, "measurements": measurements,
            "qa_type": "deterministic timing and metadata only; human visual judgment required"}


def font(size: int, bold: bool = False):
    paths = (
        ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
         "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf"] if bold else
        ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
         "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf"]
    )
    for path in paths:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def label(draw, xy, text, size=30, fill=INK, bold=False, anchor=None):
    draw.text((int(xy[0]), int(xy[1])), str(text), font=font(size, bold), fill=fill, anchor=anchor)


def rect(draw, xy, fill, r=22, outline=None, width=1):
    draw.rounded_rectangle(tuple(int(z) for z in xy), radius=int(r), fill=fill,
                           outline=outline, width=width)


def chrome(draw, shot: dict, progress: float, brand: str):
    label(draw, (70, 62), (brand.upper() + "   /   MOTION LAB")[:44], 22, INK, True)
    draw.line([(70, 102), (930, 102)], fill="#B9BEB5", width=2)
    label(draw, (70, 918), "ORIGINAL / SYNTHETIC UI DEMONSTRATION", 17, MUTED)
    label(draw, (930, 918), shot["id"], 19, INK, True, anchor="ra")
    draw.line([(70, 953), (70 + 860 * progress, 953)], fill=LIME, width=9)


def title(draw, shot: dict, sub=True):
    label(draw, (80, 170), shot.get("headline", ""), 58, INK, True)
    if sub:
        label(draw, (82, 247), shot.get("subhead", ""), 26, MUTED)


def scene_hook(draw, shot, u):
    # A crowded field collapses into one bright signal.
    dots = 8 + int(56 * (1 - ease((u - 0.36) / 0.42)))
    for i in range(dots):
        x = 100 + ((i * 149 + 73) % 800)
        y = 315 + ((i * 83 + 11) % 425)
        r = 3 + (i % 4)
        draw.ellipse((x-r, y-r, x+r, y+r), fill="#C3C8BF")
    a = ease(u / 0.30)
    label(draw, (80, int(mix(500, 390, a))), "TOO MUCH", 93, INK, True)
    label(draw, (80, int(mix(615, 510, a))), "NOISE.", 122, INK, True)
    line = ease((u - 0.54) / 0.36)
    rect(draw, (80, 745, 80 + 840 * line, 761), LIME, 8)
    if line > 0.85:
        label(draw, (80, 805), "Not enough signal.", 35, INK)


def scene_toggle(draw, shot, u):
    title(draw, shot)
    a = ease(u / 0.42)
    b = ease((u - 0.36) / 0.34)
    x1, x2 = mix(295, 220, b), mix(705, 780, b)
    y1, y2 = mix(445, 420, b), mix(605, 635, b)
    rect(draw, (x1, y1, x2, y2), LIME if a > 0.5 else "#D4D9D0", 75)
    knob_x = mix(375, 620, a)
    if b < 0.88:
        draw.ellipse((knob_x-55, 468, knob_x+55, 578), fill=WHITE)
    else:
        label(draw, (500, 520), "OPEN SIGNAL  →", 37, INK, True, anchor="mm")
    c = ease((u - 0.78) / 0.18)
    if c > 0:
        draw.line([(220, 680), (220 + 560*c, 680)], fill=INK, width=5)


def scene_cards(draw, shot, u):
    title(draw, shot)
    colors = ["#DCE3D9", "#D2DBD0", "#FDFDF8"]
    texts = [("01", "Activity"), ("02", "Priorities"), ("03", "Signal")]
    for i in range(3):
        a = ease((u - i * 0.16) / 0.43)
        x = 70 + i * 35
        y = int(mix(960, 375 + i * 112, a))
        rect(draw, (x, y, 930-i*35, y+230), colors[i], 30, outline="#C5CCC2", width=2)
        label(draw, (x+40, y+34), texts[i][0], 26, MUTED, True)
        label(draw, (x+40, y+88), texts[i][1], 45, INK, True)
        if i == 2:
            w = 480 * ease((u - 0.6) / 0.3)
            rect(draw, (x+40, y+170, x+40+w, y+183), LIME, 6)


def scene_device(draw, shot, u):
    title(draw, shot)
    a = ease(u / 0.3)
    cx = int(mix(1120, 500, a))
    rect(draw, (cx-242, 318, cx+242, 890), INK, 60)
    rect(draw, (cx-225, 335, cx+225, 872), "#F8F9F3", 47)
    rect(draw, (cx-65, 348, cx+65, 372), INK, 14)
    label(draw, (cx-175, 398), "OVERVIEW", 21, MUTED, True)
    label(draw, (cx-175, 445), "Good morning.", 34, INK, True)
    rect(draw, (cx-180, 525, cx+180, 652), LIME, 22)
    label(draw, (cx-152, 545), "YOUR SIGNAL", 21, INK, True)
    label(draw, (cx-152, 590), "Ready to move", 28, INK, True)
    for i in range(3):
        yy = int(696 + i*52 - 60*ease((u-0.35)/0.35))
        rect(draw, (cx-180, yy, cx+180, yy+40), PANEL, 12)
        draw.ellipse((cx-160, yy+12, cx-143, yy+29), fill=LIME)
        label(draw, (cx-130, yy+7), ["Decisions", "Priorities", "Momentum"][i], 18, INK)
    if u > 0.82:
        rect(draw, (cx+75, 780, cx+190, 830), INK, 18)
        label(draw, (cx+132, 806), "✓", 30, LIME, True, anchor="mm")


def scene_data(draw, shot, u):
    title(draw, shot)
    rect(draw, (80, 345, 920, 825), WHITE, 32, outline="#D7DBD1", width=2)
    label(draw, (126, 388), "MOMENTUM", 24, MUTED, True)
    heights = [155, 200, 175, 280, 235, 350, 305]
    for i, height in enumerate(heights):
        a = ease((u - i * 0.07) / 0.45)
        x = 150 + i * 104
        h = height * a
        rect(draw, (x, 768-h, x+58, 768), LIME if i == 5 else "#AAB4A8", 12)
    a = ease((u - 0.58) / 0.25)
    if a > 0:
        rect(draw, (600, 383, 875, 465), INK, 20)
        label(draw, (737, 424), "FOCUS  ↑", 30, LIME, True, anchor="mm")


def scene_cta(draw, shot, u):
    a = ease(u / 0.26)
    b = ease((u - 0.35) / 0.35)
    w = mix(570, 700, b)
    x = 500 - w / 2
    y = mix(540, 495, b)
    rect(draw, (x, y, x+w, y+118), LIME if b > 0.7 else WHITE, 55,
         outline=None if b > 0.7 else "#D0D7C9", width=3)
    if b < 0.70:
        letters = int(mix(0, 10, ease((u - 0.15) / 0.35)))
        label(draw, (x+50, y+35), "see signal"[:letters], 35, INK)
    else:
        label(draw, (500, y+59), "SEE THE SIGNAL  →", 37, INK, True, anchor="mm")
    if u > 0.72:
        label(draw, (500, 315), "PRYNTOR", 80, INK, True, anchor="mm")
        label(draw, (500, 744), "A better way to move.", 32, MUTED, anchor="mm")
    draw.line([(80, 855), (80+840*a, 855)], fill=INK, width=4)


SCENES = {
    "hook": scene_hook, "toggle": scene_toggle, "cards": scene_cards,
    "device": scene_device, "data": scene_data, "cta": scene_cta,
}


def seek(p: dict, seconds: float) -> Image.Image:
    """Stateless renderer: identical input time produces identical frame."""
    shot, u = shot_at(p, seconds)
    base = Image.new("RGB", (1000, 1000), IVORY)
    draw = ImageDraw.Draw(base)
    SCENES[shot["type"]](draw, shot, u)
    if shot["type"] == "device" and shot.get("asset"):
        asset = Path(shot["asset"])
        if asset.exists():
            cx = int(mix(1120, 500, ease(u / 0.3)))
            with Image.open(asset) as original:
                image = ImageOps.contain(original.convert("RGB"), (350, 250))
                base.paste(image, (cx - image.width // 2, 520))
    chrome(draw, shot, u, p.get("brand", "PRYNTOR"))
    w, h = int(p.get("width", 720)), int(p.get("height", 720))
    side = min(w, h)
    if (w, h) == (1000, 1000):
        return base
    # Preserve square composition and legibility for 1:1, 16:9 and 9:16 exports.
    frame = Image.new("RGB", (w, h), IVORY)
    tile = base.resize((side, side), Image.Resampling.LANCZOS)
    frame.paste(tile, ((w-side)//2, (h-side)//2))
    return frame


def render(p: dict, output: Path, seconds: float | None, final: bool, blur: bool, shot_id: str | None = None):
    report = inspect(p, require_approval=final)
    if report["errors"]:
        raise ValueError("Render blocked: " + "; ".join(report["errors"]))
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("ffmpeg not installed; no MP4 was created")
    start = 0.0
    full_length = duration(p)
    if shot_id:
        match = next((row for row in timeline(p) if row["shot"]["id"] == shot_id), None)
        if match is None:
            raise ValueError(f"Unknown shot: {shot_id}")
        start, full_length = match["start"], float(match["shot"]["duration"])
    length = full_length if seconds is None else min(float(seconds), full_length)
    if length <= 0:
        raise ValueError("Render length must be positive")
    fps = int(p.get("fps", 24))
    w, h = int(p.get("width", 720)), int(p.get("height", 720))
    nframes = math.ceil(length * fps)
    output.parent.mkdir(parents=True, exist_ok=True)
    cmd = [ffmpeg, "-y", "-loglevel", "error", "-f", "rawvideo",
           "-vcodec", "rawvideo", "-pix_fmt", "rgb24",
           "-s", f"{w}x{h}", "-r", str(fps), "-i", "pipe:0"]
    music = p.get("music")
    if music:
        music_path = Path(music)
        if not music_path.exists():
            raise FileNotFoundError(f"Music not found: {music}")
        cmd += ["-stream_loop", "-1", "-i", str(music_path),
                "-map", "0:v", "-map", "1:a", "-c:a", "aac", "-b:a", "160k"]
    cmd += ["-t", str(length), "-c:v", "libx264", "-preset", "veryfast",
            "-crf", "20", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(output)]
    previous = None
    process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        for i in range(nframes):
            img = seek(p, start + i / fps)
            if blur and previous is not None:
                img = Image.blend(previous, img, 0.78)
            previous = img
            process.stdin.write(img.tobytes())
    except (BrokenPipeError, OSError):
        process.kill()
        raise RuntimeError("ffmpeg terminated during frame streaming")
    finally:
        if process.stdin:
            process.stdin.close()
    error = process.stderr.read().decode("utf-8", "replace")
    if process.wait() != 0 or not output.exists() or output.stat().st_size == 0:
        raise RuntimeError("ffmpeg render failed: " + error[-1500:])
    print(json.dumps({"status": "rendered_not_published", "path": str(output),
                      "bytes": output.stat().st_size, "frames": nframes,
                      "seconds": length, "shot": shot_id,
                      "final_approved": final}, indent=2))



def frame_qa(p: dict, sample_fps: int = 4) -> dict:
    """Computed pixel-motion inspection; NOT a perceptual or creative score."""
    if not 1 <= sample_fps <= 24:
        raise ValueError("sample_fps must be 1–24")
    metrics, warnings = [], []
    for row in timeline(p):
        s = row["shot"]
        n = max(2, int(math.ceil(float(s["duration"]) * sample_fps)))
        prev = None
        static = 0
        max_static = 0
        diffs = []
        for i in range(n):
            t = row["start"] + min((i + 0.5) / sample_fps, float(s["duration"]) - 0.01)
            frame = seek(p, t).convert("L").resize((120, 120))
            if prev is not None:
                difference = ImageChops.difference(prev, frame)
                mean_diff = ImageStat.Stat(difference).mean[0]
                diffs.append(round(mean_diff, 4))
                static = static + 1 if mean_diff < 0.45 else 0
                max_static = max(max_static, static)
            prev = frame
        hold = round(max_static / sample_fps, 2)
        metrics.append({"id": s["id"], "samples": n, "max_near_static_seconds": hold,
                        "mean_frame_difference": round(sum(diffs)/max(1,len(diffs)), 3),
                        "computed_only": True})
        if hold > 1.25:
            warnings.append(f"{s['id']}: >1.25s near-static hold; inspect against music")
    return {"sample_fps": sample_fps, "shot_metrics": metrics, "warnings": warnings,
            "limitation": "Pixel difference cannot determine artistic quality, legibility or transition intent"}


def contact_sheet(p: dict, output: Path):
    rows = timeline(p)
    size, cols = 330, 3
    count_rows = math.ceil(len(rows) / cols)
    sheet = Image.new("RGB", (cols * size, count_rows * (size + 45)), WHITE)
    draw = ImageDraw.Draw(sheet)
    for i, row in enumerate(rows):
        middle = (row["start"] + row["end"]) / 2
        frame = seek(p, middle)
        frame.thumbnail((size-14, size-14))
        x, y = (i % cols) * size, (i // cols) * (size+45)
        sheet.paste(frame, (x+7, y+7))
        label(draw, (x+10, y+size+3), row["shot"]["id"]+" / "+row["shot"]["type"], 20)
    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output)


def handoff(p: dict, outdir: Path):
    outdir.mkdir(parents=True, exist_ok=True)
    report = inspect(p)
    (outdir/"qa.json").write_text(json.dumps(report, indent=2)+"\n")
    (outdir/"storyboard.json").write_text(json.dumps(p, indent=2)+"\n")
    with (outdir/"edit_decision_list.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["shot", "start_s", "end_s", "duration_s", "headline", "tool", "approved"])
        for row in timeline(p):
            s = row["shot"]
            w.writerow([s["id"], round(row["start"], 3), round(row["end"], 3),
                        s["duration"], s.get("headline"), s.get("tool", "code"), bool(s.get("approved"))])
    contact_sheet(p, outdir/"contact_sheet.png")
    notes = ["# Motion Director — AE/Premiere handoff", "",
             f"Project: {p.get('name')}", f"Duration: {duration(p):g}s", f"Tempo: {p.get('bpm',120)} BPM",
             "", "No Adobe, Premiere or Ultramockup automation was executed by this exporter.", ""]
    for row in timeline(p):
        s = row["shot"]
        notes += [f"## {s['id']} | {row['start']:g}–{row['end']:g}s | {s['type']}",
                  f"**Headline:** {s.get('headline','')}",
                  f"**Actions:** {' → '.join(s.get('actions',[]))}",
                  f"**Motion annotation:** {s.get('annotation','')}",
                  f"**Route:** {s.get('tool','code')}", ""]
    (outdir/"editor_handoff.md").write_text("\n".join(notes), encoding="utf-8")
    (outdir/"provenance.json").write_text(json.dumps({
        "generated_at": now(), "source": "original deterministic Pillow renderer",
        "external_models_called": [], "synthetic_demo": bool(p.get("synthetic_demo", False)),
        "rights_declaration": p.get("rights"), "render_verified": False,
        "human_approval": {s["id"]: bool(s.get("approved")) for s in p["shots"]},
        "note": "Handoff artifacts generated; this does not prove a final MP4 was rendered."
    }, indent=2)+"\n")
    print(json.dumps({"status": "handoff_created", "directory": str(outdir),
                      "files": [x.name for x in sorted(outdir.iterdir())]}, indent=2))


def save(p: dict, path: Path):
    path.write_text(json.dumps(p, indent=2, ensure_ascii=False)+"\n", encoding="utf-8")


def revise(p: dict, path: Path, shot_id: str, shot_duration, headline, note):
    target = next((s for s in p["shots"] if s["id"] == shot_id), None)
    if target is None:
        raise ValueError(f"No such shot: {shot_id}")
    before = {"duration": target["duration"], "headline": target.get("headline")}
    if shot_duration is not None:
        target["duration"] = float(shot_duration)
    if headline is not None:
        target["headline"] = headline
    if duration(p) > 60:
        target.update(before)
        raise ValueError("Revision exceeds 60-second limit")
    target["approved"] = False
    target.setdefault("notes", []).append({"at": now(), "note": note or "Director revision"})
    p.setdefault("history", []).append({"at": now(), "action": "revise",
                                       "shot": shot_id, "before": before,
                                       "after": {"duration": target["duration"], "headline": target.get("headline")}})
    save(p, path)


def approve(p: dict, path: Path, shot_id: str | None, all_shots: bool):
    if not all_shots and not shot_id:
        raise ValueError("Choose --shot ID or --all for explicit human approval")
    targets = p["shots"] if all_shots else [s for s in p["shots"] if s["id"] == shot_id]
    if not targets:
        raise ValueError(f"No such shot: {shot_id}")
    for s in targets:
        s["approved"] = True
    p.setdefault("history", []).append({"at": now(), "action": "manual_cli_approval",
                                       "shots": [s["id"] for s in targets],
                                       "caveat": "CLI cannot verify human identity"})
    save(p, path)



def create_project(output: Path, name: str, brand: str, message: str, audience: str,
                   channel: str, aspect: str, bpm: float):
    """Deterministic brief -> editable six-shot storyboard; no LLM invoked."""
    formats = {"1:1": (720, 720), "16:9": (1280, 720), "9:16": (720, 1280)}
    if aspect not in formats:
        raise ValueError("Aspect must be 1:1, 16:9 or 9:16")
    if not 40 <= bpm <= 240:
        raise ValueError("BPM must be 40–240")
    width, height = formats[aspect]
    specs = [
        ("hook", 4, "Too much noise.", "A clearer way starts here.",
         ["problem appears", "noise collapses"], "Compression into a signal line."),
        ("toggle", 5, "Turn clarity on.", "One action changes the view.",
         ["toggle engages", "switch morphs into CTA", "CTA expands"], "Maintain geometry across morph."),
        ("cards", 5, "Bring it together.", "One place for what matters.",
         ["cards enter", "priority expands", "secondary cards recede"], "Half-beat stagger; preserve hierarchy."),
        ("device", 6, "Made for decisions.", "The experience, in your hands.",
         ["device enters", "interface moves", "action confirms"], "Authentic screenshot optional; synthetic UI by default."),
        ("data", 5, "Spot what matters.", "Turn activity into action.",
         ["metrics rise", "chart resolves", "focus locks"], "Synthetic data; do not imply product metrics."),
        ("cta", 5, message.upper()[:42] or "SEE THE SIGNAL.", "A better way to move.",
         ["search field appears", "search morphs to CTA", "brand locks"], "Clear CTA and final 0.4s hold.")
    ]
    shots = [{"id": f"S{i:02d}", "type": kind, "duration": sec, "headline": head,
              "subhead": sub, "actions": actions, "annotation": annotation,
              "tool": "device" if kind == "device" else "code",
              "approved": False, "notes": []}
             for i, (kind, sec, head, sub, actions, annotation) in enumerate(specs, 1)]
    p = {"name": name, "brand": brand, "message": message, "audience": audience,
         "channel": channel, "aspect_ratio": aspect, "width": width, "height": height,
         "fps": 24, "bpm": bpm, "music": None, "synthetic_demo": True,
         "rights": "Original illustrative vectors; add verified licenses before commercial use",
         "shots": shots, "history": [{"at": now(), "action": "deterministic_init",
                                     "note": "Not AI-generated; director must rewrite for product truth"}]}
    output.parent.mkdir(parents=True, exist_ok=True)
    save(p, output)
    print(json.dumps({"status": "storyboard_created", "path": str(output),
                      "duration_seconds": duration(p), "shots": len(shots),
                      "requires_director_review": True}, indent=2))


def reorder(p: dict, path: Path, ids: str):
    wanted = [x.strip() for x in ids.split(",") if x.strip()]
    existing = [s["id"] for s in p["shots"]]
    if len(wanted) != len(existing) or set(wanted) != set(existing):
        raise ValueError("Order must contain each existing shot ID exactly once")
    mapping = {s["id"]: s for s in p["shots"]}
    p["shots"] = [mapping[sid] for sid in wanted]
    for s in p["shots"]:
        s["approved"] = False
    p.setdefault("history", []).append({"at": now(), "action": "reorder",
                                       "before": existing, "after": wanted})
    save(p, path)

def main():
    parser = argparse.ArgumentParser(description="Original music-led motion director / renderer")
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("plan", "qa", "render", "handoff", "revise", "approve"):
        sub.add_parser(name).add_argument("project", type=Path)
    initp = sub.add_parser("init")
    initp.add_argument("--output", type=Path, required=True)
    initp.add_argument("--name", required=True)
    initp.add_argument("--brand", default="ORIGINAL")
    initp.add_argument("--message", required=True)
    initp.add_argument("--audience", default="general")
    initp.add_argument("--channel", default="social")
    initp.add_argument("--aspect", choices=["1:1", "16:9", "9:16"], default="1:1")
    initp.add_argument("--bpm", type=float, default=120)
    sub.add_parser("reorder").add_argument("project", type=Path)
    sub.choices["reorder"].add_argument("--order", required=True)
    sub.choices["render"].add_argument("--output", type=Path, default=Path("preview.mp4"))
    sub.choices["render"].add_argument("--seconds", type=float)
    sub.choices["render"].add_argument("--final", action="store_true")
    sub.choices["render"].add_argument("--blur", action="store_true")
    sub.choices["render"].add_argument("--shot")
    sub.add_parser("qa-frames").add_argument("project", type=Path)
    sub.choices["qa-frames"].add_argument("--output", type=Path)
    sub.choices["handoff"].add_argument("--outdir", type=Path, default=Path("handoff"))
    sub.choices["revise"].add_argument("--shot", required=True)
    sub.choices["revise"].add_argument("--duration", type=float)
    sub.choices["revise"].add_argument("--headline")
    sub.choices["revise"].add_argument("--note", default="")
    sub.choices["approve"].add_argument("--shot")
    sub.choices["approve"].add_argument("--all", action="store_true")
    args = parser.parse_args()
    if args.command == "init":
        create_project(args.output, args.name, args.brand, args.message,
                       args.audience, args.channel, args.aspect, args.bpm)
        return
    p = load(args.project)
    if args.command == "plan":
        print(json.dumps({"project": p.get("name"), "duration": duration(p),
                          "script": [s.get("headline") for s in p["shots"]],
                          "timeline": timeline(p)}, indent=2))
    elif args.command == "qa":
        print(json.dumps(inspect(p), indent=2))
    elif args.command == "render":
        render(p, args.output, args.seconds, args.final, args.blur, args.shot)
    elif args.command == "qa-frames":
        report = frame_qa(p)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps(report, indent=2)+"\n")
        print(json.dumps(report, indent=2))
    elif args.command == "handoff":
        handoff(p, args.outdir)
    elif args.command == "revise":
        revise(p, args.project, args.shot, args.duration, args.headline, args.note)
        print("Revision saved; shot approval invalidated.")
    elif args.command == "reorder":
        reorder(p, args.project, args.order)
        print("Order saved; shot approvals invalidated.")
    elif args.command == "approve":
        approve(p, args.project, args.shot, args.all)
        print("Manual CLI approval recorded; verify director identity separately.")


if __name__ == "__main__":
    main()
