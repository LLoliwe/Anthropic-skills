"""PRY-309: read-only MLX-LoRA training-intake gate.

Uses only the Python standard library, never imports MLX, invokes MCP tools,
opens network sockets, installs packages, or starts training. Positive status
means a reviewed proposal, not permission to train or ship adapters.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import re
from pathlib import Path

UPSTREAM_REPO = "Goekdeniz-Guelmez/mlx-lm-lora"
UPSTREAM_TAG = "v5.10.1"
UPSTREAM_COMMIT = "4fa3c5148b17a5833b3074e4e58c6299baec1018"
HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
HF_ID = re.compile(r"^[A-Za-z0-9._-]+/[A-Za-z0-9._-]+$")


class DuplicateKeyError(ValueError):
    """Reject ambiguous JSON used to bypass review policy."""


def _unique_object(pairs: list[tuple[str, object]]) -> dict:
    data = {}
    for key, value in pairs:
        if key in data:
            raise DuplicateKeyError("duplicate JSON key: " + key)
        data[key] = value
    return data


def _read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_unique_object)


def _checked_file(root: Path, name: object) -> Path:
    if not isinstance(name, str) or not name or Path(name).is_absolute():
        raise ValueError("dataset file path must be relative")
    # Reject paths that go through a symlink, even if the target is inside root.
    p = root / name
    if any(part == ".." for part in Path(name).parts):
        raise ValueError("dataset path traversal rejected")
    actual_root = root.resolve(strict=True)
    actual = p.resolve(strict=True)
    if not actual.is_relative_to(actual_root) or not actual.is_file():
        raise ValueError("dataset path escapes root or is not a regular file")
    candidate = actual_root
    for part in Path(name).parts:
        candidate /= part
        if candidate.is_symlink():
            raise ValueError("symlinks are not allowed in dataset paths")
    if p.stat().st_size > 256_000:
        raise ValueError("R0 smoke fixture exceeds 256 KB")
    return actual


def _verify_split(root: Path, item: object, kind: str) -> tuple[set[str], list[str]]:
    errors = []
    if not isinstance(item, dict):
        return set(), [kind + ": missing split entry"]
    try:
        file_path = _checked_file(root, item.get("path"))
        blob = file_path.read_bytes()
        wanted_hash = item.get("sha256")
        if not isinstance(wanted_hash, str) or not HEX64.fullmatch(wanted_hash):
            raise ValueError("SHA256 required")
        if hashlib.sha256(blob).hexdigest() != wanted_hash:
            raise ValueError("SHA256 mismatch")
        prompts = set()
        lines = blob.decode("utf-8").splitlines()
        if len(lines) < 2:
            raise ValueError("at least two synthetic samples per split are required")
        for index, line in enumerate(lines, 1):
            row = json.loads(line, object_pairs_hook=_unique_object)
            if not isinstance(row, dict) or set(row) != {"messages"}:
                raise ValueError(f"line {index}: expected only messages")
            msgs = row["messages"]
            if not isinstance(msgs, list) or len(msgs) != 2:
                raise ValueError(f"line {index}: expected one user and one assistant")
            if [m.get("role") for m in msgs if isinstance(m, dict)] != ["user", "assistant"]:
                raise ValueError(f"line {index}: invalid roles")
            for m in msgs:
                if not isinstance(m, dict) or set(m) != {"role", "content"}:
                    raise ValueError(f"line {index}: invalid message")
                if not isinstance(m["content"], str) or not m["content"].strip():
                    raise ValueError(f"line {index}: empty/non-string content")
                if len(m["content"]) > 800:
                    raise ValueError(f"line {index}: oversized sample")
            prompt = msgs[0]["content"].strip().casefold()
            if prompt in prompts:
                raise ValueError(f"line {index}: duplicate prompt")
            prompts.add(prompt)
        return prompts, errors
    except (ValueError, UnicodeError, OSError, json.JSONDecodeError) as ex:
        errors.append(f"{kind}: {ex}")
    return set(), errors


def assess(manifest: object, root: Path, host: tuple[str, str] | None = None) -> dict:
    """Return testable evidence of policy fit, never training authorisation."""
    failures = []
    pending = []
    if not isinstance(manifest, dict):
        return {"status": "BLOCKED_POLICY", "failures": ["manifest must be object"],
                "training_started": False, "release_authorized": False}

    if manifest.get("schema_version") != 1 or manifest.get("tracking_issue") != "PRY-309":
        failures.append("use PRY-309 and schema_version 1")
    src = manifest.get("upstream", {})
    if not isinstance(src, dict) or any(src.get(k) != v for k, v in {
        "repo": UPSTREAM_REPO, "tag": UPSTREAM_TAG, "commit": UPSTREAM_COMMIT}.items()):
        failures.append("upstream must be the independently pinned v5.10.1 release")

    constraints = manifest.get("controls", {})
    required = {"new_spend_zar": 0, "data_class": "synthetic-only",
                "contains_personal_or_client_data": False, "contains_child_data": False,
                "external_upload_approved": False, "training_enabled": False,
                "automatic_promotion": False, "mcp_transport": "stdio"}
    if not isinstance(constraints, dict) or any(type(constraints.get(k)) is not type(v)
            or constraints.get(k) != v for k, v in required.items()):
        failures.append("R0/clean-room/stdio/no-training controls must all be explicitly fixed")

    model = manifest.get("model", {})
    if not isinstance(model, dict) or not isinstance(model.get("id"), str) or not HF_ID.fullmatch(model["id"]):
        failures.append("valid Hugging Face model ID required")
    else:
        if model.get("license") != "apache-2.0":
            failures.append("model licence has not been verified as Apache-2.0")
        revision = model.get("revision")
        if not isinstance(revision, str) or not HEX40.fullmatch(revision):
            pending.append("resolve and independently review immutable HF model revision")

    evaluation = manifest.get("evaluation", {})
    if not isinstance(evaluation, dict) or evaluation.get("metric") != "held_out_accuracy" or evaluation.get("minimum_gain_pp") != 5:
        failures.append("predeclared held_out_accuracy with +5pp criterion required")
    if not isinstance(evaluation, dict) or evaluation.get("independent_reviewer") != "PENDING":
        failures.append("pilot must remain pending independent review")

    data = manifest.get("data", {})
    if not isinstance(data, dict):
        failures.append("data splits required")
    else:
        train, terr = _verify_split(root, data.get("train"), "train")
        test, verr = _verify_split(root, data.get("test"), "held-out")
        failures += terr + verr
        if train and test and train.intersection(test):
            failures.append("train and held-out prompts overlap")
        if train and test and data["train"].get("sha256") == data["test"].get("sha256"):
            failures.append("train and test must be independent files")

    actual_os, actual_arch = host if host is not None else (platform.system(), platform.machine())
    if (actual_os, actual_arch) != ("Darwin", "arm64"):
        pending.append(f"Mac Apple Silicon host required; this host is {actual_os}/{actual_arch}")
    # Static manifest can never prove runtime preflight or reviewer approval.
    pending.append("on Mac: validate_model_support, inspect_dataset, check_training_config sequentially")
    pending.append("independent hold-out owner and security review before any training")
    return {
        "status": "BLOCKED_POLICY" if failures else "REVIEW_ONLY_VALIDATED",
        "failures": failures,
        "pending_for_training": pending,
        "training_started": False,
        "mcp_connected": False,
        "adapter_created": False,
        "release_authorized": False,
        "model_quality_improved": "NOT_MEASURED",
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--manifest", type=Path, required=True)
    args = ap.parse_args()
    try:
        obj = _read_json(args.manifest)
        report = assess(obj, args.manifest.resolve().parent)
    except (ValueError, OSError, UnicodeError, json.JSONDecodeError) as ex:
        report = {"status": "BLOCKED_POLICY", "failures": [str(ex)],
                  "training_started": False, "release_authorized": False}
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "REVIEW_ONLY_VALIDATED" else 2


if __name__ == "__main__":
    raise SystemExit(main())
