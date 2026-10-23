# PRY-309 | MLX-LM-LoRA MCP R0 evaluation plan

**Status on 23 October 2026: candidate captured, private R0 lab verified, no MLX backend installed and no actual model training.** This is an addition to existing PRY-309 draft PR #58, not a new product, dispatch service, auto-trainer, installed MCP or company-wide deployment.

## Upstream verification

- Official source: https://github.com/Goekdeniz-Guelmez/mlx-lm-lora (Apache-2.0).
- The screenshot described v5.9.0. The upstream 23 October release is v5.10.1 at source commit 4fa3c5148b17a5833b3074e4e58c6299baec1018 (annotated tag SHA 79adf853ae8728b8a4fe9a8ba635afb3e49161d3). Recheck exact pin before installation.
- Upstream training is designed for Apple Silicon. Current authoring runtime is Linux x86_64, so genuine MLX fine-tuning is blocked.
- The upstream MCP server starts local processes and exposes start_training / training_status / training_log / stop_training. It has no tenant isolation. Prefer project-local stdio, not network HTTP.
- The official skill requires sequential validate_model_support, inspect_dataset, check_training_config before start_training. An explicit "Config looks good." is needed but not sufficient to declare compatibility.

## R0 work actually performed

- Built a pure-standard-library read-only training-intake gate and original synthetic SFT data.
- Proposed Pryntor Core release-evidence classification as a narrow pilot, with six synthetic training rows and four isolated synthetic held-out rows. Four evaluation examples are only a schema smoke test, **not enough to assert accuracy or a 5 percentage-point improvement**.
- On a local Linux x86_64 authoring environment: 20 of 20 safety/negative/positive unit tests passed, including nonzero spend, confidential/child-data flags, HTTP exposure, source pin errors, SHA mismatches, split overlap, traversal/symlink attempts and auto-promotion.
- Static gate returned REVIEW_ONLY_VALIDATED and correctly recorded training_started=false, mcp_connected=false, adapter_created=false, release_authorized=false, model_quality_improved=NOT_MEASURED.
- Founder conversation contains downloadable zip Pryntor_MLX_LoRA_R0_Pilot.zip with the code, tests, synthetic fixture, Mac runbook and local evidence. The gate, 20 tests, manifest and synthetic JSONL splits are now also SHA-matched and staged on this same draft PR branch. They are NOT installed in any company training runtime.

## Before any live training

1. Obtain an explicitly authorised, existing Apple Silicon Mac with a no-new-spend entitlement and confirm version, RAM, disk, Python and license rights. No cloud GPU or Mac procurement.
2. Inspect the exact upstream source, dependencies, installation hashes, executable entrypoints and tool permissions; isolate local operator data. Restrict model/dataset to separately licensed, safe original/synthetic material. No client or user personal data.
3. Resolve an immutable Hugging Face model revision; candidate is mlx-community/SmolLM2-135M-Instruct, Apache-2.0 model card, but compatibility and hardware fit are unverified. Validate dataset schema/rights against **actual** live server. No blind global npx skill install.
4. Capture authorised configs and logs for sequential model/dataset/config preflights. Missing tool, warnings, failed validation or unavailable local rights => stop.
5. Only after explicit approval, run a bounded LoRA SFT experiment and preserve all run receipts, model/dataset hashes, training time and true incremental cost.
6. Compare the baseline and candidate on a protected sufficiently sized held-out suite with negative cases, independently approved metrics and human expert review. Fixed outcome contract: prefer >=5 pp held-out accuracy improvement, with zero safety regression, but preregister and power the real experiment separately. No automatic merge, adapter publication, production release or self-grading.

## Fit across Pryntor

First pilot: Core internal release-evidence classification. Potential next uses, all **separate gated research**: Recover sandbox operations classification (no PII), SYW explanation assessment (educator integrity), Tirisano public institutional travel FAQ intake (no sensitive client or tender data), ZOWIBO age-safe synthetic evaluation (never train on children's data), Robotics simulator-log classification (no physical actuation). Try prompting, retrieval and deterministic code first. Keep PRY-309, PRY-199 and all domain/agent integrity rules authoritative.

## Release gate

No training run; no adapter; no performance improvement claim; no new spend; no active Codex/Claude/Hermes/Grok connections; no new schedules or agents. Exact-head hosted CI and independent review are outstanding. Keep the PR draft, never self-merge.
