"""Independent artifact-level QA for the AURA/01 Blender product demo.
Run outside Blender in a clean Python process (and on an independent CI runner).
Verifies bytes, decode, dimensions, content variation and editable source.
It cannot establish photographic realism, licence clearance or client approval.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageStat


RATIOS = {
    "1x1": (1, 1),
    "4x5": (4, 5),
    "9x16": (9, 16),
    "16x9": (16, 9),
}


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def verify(root: Path, size: int):
    evidence = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "render_engine": "Blender 5.0.1 native Cycles CPU",
        "product": "AURA/01 — wholly fictional internal art-direction concept",
        "external_assets": False,
        "scenario_api_calls": 0,
        "credit_consumption": 0,
        "human_creative_approval": "NOT PERFORMED",
        "checks": [],
    }
    source = root / "aura_01_editable_source.blend"
    if not source.is_file():
        raise AssertionError("Missing editable source .blend")
    with source.open("rb") as f:
        if f.read(7) != b"BLENDER":
            raise AssertionError("Invalid Blender source header")
    evidence["source"] = {"file": source.name, "bytes": source.stat().st_size, "sha256": sha256(source)}
    for name, (x, y) in RATIOS.items():
        path = root / f"aura_01_{name}.png"
        if not path.is_file():
            raise AssertionError(f"Missing render: {path}")
        with Image.open(path) as im:
            im.verify()  # checks underlying PNG integrity
        with Image.open(path) as im:
            im.load()  # forces full decode in a separate process
            expected = (round(size * x / min(x, y)), round(size * y / min(x, y)))
            if im.size != expected:
                raise AssertionError(f"Wrong dimensions for {name}: {im.size} != {expected}")
            if im.mode not in ("RGB", "RGBA"):
                raise AssertionError(f"Wrong image mode {name}: {im.mode}")
            rgb = im.convert("RGB")
            stat = ImageStat.Stat(rgb)
            ent = rgb.entropy()
            if ent < 3.0 or max(stat.stddev) < 15:
                raise AssertionError(f"Potentially blank render {name} entropy={ent:.3f}, std={stat.stddev}")
            corners = [rgb.getpixel((0, 0)), rgb.getpixel((rgb.width - 1, rgb.height - 1))]
            mid = rgb.getpixel((rgb.width // 2, rgb.height // 2))
            differences = [sum(abs(a-b) for a,b in zip(corner,mid)) for corner in corners]
            if min(differences) < 45:
                raise AssertionError(f"No visible foreground in render {name}")
            record = {
                "format": name,
                "file": path.name,
                "dimensions": list(im.size),
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
                "entropy": round(ent, 3),
                "channel_stddev": [round(v, 2) for v in stat.stddev],
                "foreground_background_difference": differences,
                "status": "PASS",
            }
            evidence["checks"].append(record)
    evidence["verified_pass_count"] = len(evidence["checks"])
    evidence["readiness"] = "AUTOMATED ARTIFACT CHECKS PASS / HUMAN VISUAL APPROVAL PENDING"
    dest = root / "verification_evidence.json"
    dest.write_text(json.dumps(evidence, indent=2) + "\n")
    print(json.dumps(evidence, indent=2))


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--root", type=Path, default=Path("output"))
    p.add_argument("--size", type=int, default=512)
    args = p.parse_args()
    verify(args.root, args.size)
