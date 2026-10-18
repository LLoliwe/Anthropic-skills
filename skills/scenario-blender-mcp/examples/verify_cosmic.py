"""Fresh-process and fresh-runner technical QA for original Blender cosmic FX."""
import argparse
import hashlib
import json
from pathlib import Path
from PIL import Image, ImageStat


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(folder, size):
    root = Path(folder)
    evidence = json.loads((root / "cosmic_fx_evidence.json").read_text())
    assert evidence["status"] == "render-created-not-artist-approved"
    assert evidence["vendor_asset_loaded"] is False, "CI must not contain proprietary vendor assets"
    assert evidence["vendor_asset"] is None
    assert evidence["artistic_approval"] is False
    assert evidence["commercial_release_approved"] is False
    assert evidence["dimensions"] == [size, round(size * 9 / 16)]
    blend = root / "cosmic_fx_study.blend"
    assert blend.read_bytes()[:7] == b"BLENDER"
    picture = root / "cosmic_fx_study.png"
    with Image.open(picture) as im:
        im.verify()
    with Image.open(picture) as im:
        im.load()
        assert im.size == (size, round(size * 9 / 16))
        rgb = im.convert("RGB")
        std = ImageStat.Stat(rgb).stddev
        assert max(std) > 3, "Blank or too-dark rendered still"
        assert rgb.entropy() > 2, "Insufficient image variation"
    for name, expected in evidence["outputs"].items():
        assert sha256(root / name) == expected, "File hash mismatch: " + name
    return {"result": "TECHNICAL_QA_PASS", "vendor_product_tested": False,
            "artistic_review": False, "stddev": [round(x, 2) for x in std]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default="output")
    parser.add_argument("--size", type=int, default=384)
    options = parser.parse_args()
    print(json.dumps(verify(options.root, options.size)))
