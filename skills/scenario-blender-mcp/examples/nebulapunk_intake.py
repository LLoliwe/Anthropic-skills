"""Fail-closed local intake for owner-acquired Nebulapunk Free asset.

No source files, vendor shaders, paid APIs or download actions are bundled.
An operator-authored receipt alone is not a substitute for legal review.
"""
import hashlib
import json
import re
from pathlib import Path

OFFICIAL_URL = "https://superhivemarket.com/products/nebulapunk"


def sha256_file(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_vendor_asset(asset_path, receipt_path, expected_sha256, collection_name):
    if not all((asset_path, receipt_path, expected_sha256, collection_name)):
        raise ValueError("Missing vendor file, receipt, SHA-256, or collection")
    raw = Path(asset_path).expanduser()
    if raw.is_symlink():
        raise ValueError("Symlinked vendor assets forbidden")
    path = raw.resolve(strict=True)
    if not path.is_file() or path.suffix.lower() != ".blend":
        raise ValueError("Vendor asset must be a .blend file")
    if not 0 < path.stat().st_size <= 512 * 1024 * 1024:
        raise ValueError("Vendor file size outside R0 cap")
    if not re.fullmatch(r"[0-9a-fA-F]{64}", expected_sha256):
        raise ValueError("Expected hash must be SHA-256")
    actual = sha256_file(path)
    if actual.lower() != expected_sha256.lower():
        raise ValueError("Vendor asset SHA-256 mismatch")
    if not isinstance(collection_name, str) or not 0 < len(collection_name) <= 120:
        raise ValueError("Collection name required")
    receipt_raw = Path(receipt_path).expanduser()
    if receipt_raw.is_symlink():
        raise ValueError("Symlinked licence receipt forbidden")
    receipt = json.loads(receipt_raw.resolve(strict=True).read_text(encoding="utf-8"))
    if not isinstance(receipt, dict):
        raise ValueError("Receipt must be a JSON object")
    if receipt.get("product") != "Nebulapunk Free" or receipt.get("source") != OFFICIAL_URL:
        raise ValueError("Not the official free-edition asset")
    if receipt.get("cost_usd") != 0 or receipt.get("approved_for_internal_test") is not True:
        raise ValueError("Unapproved spend or test")
    if receipt.get("commercial_use_review") not in ("internal-only", "cleared"):
        raise ValueError("Commercial rights assessment required")
    if not str(receipt.get("owner_reviewer") or "").strip():
        raise ValueError("Independent owner reviewer required")
    if receipt.get("sha256", "").lower() != actual:
        raise ValueError("Approval hash mismatch")
    return {
        "product": "Nebulapunk Free",
        "source": OFFICIAL_URL,
        "sha256": actual,
        "bytes": path.stat().st_size,
        "collection": collection_name,
        "owner_reviewer": receipt["owner_reviewer"],
        "commercial_use_review": receipt["commercial_use_review"],
        "approval_status": "local-only-reviewed-by-operator"
    }
