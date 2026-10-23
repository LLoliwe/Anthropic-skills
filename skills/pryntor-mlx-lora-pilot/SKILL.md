---
name: pryntor-mlx-lora-pilot
description: Review-only, zero-spend evaluation of MLX-LM-LoRA MCP fine-tuning inside existing Pryntor PRY-309. Training needs separately verified Apple Silicon Mac and approval.
---

# Pryntor MLX-LM-LoRA | PRY-309 experimental skill

STATUS: PROPOSED / NOT INSTALLED / NOT TRAINED. This skill is a controlled extension of existing PRY-309, not a new agent, runner, automatic retraining service, or claim of recursive self-improvement.

## Pinned official sources

- Apache-2.0 source: https://github.com/Goekdeniz-Guelmez/mlx-lm-lora
- Approved research pin for this review: release v5.10.1, annotated tag 79adf853ae8728b8a4fe9a8ba635afb3e49161d3, source commit 4fa3c5148b17a5833b3074e4e58c6299baec1018 (23 October 2026).
- Official skill: https://github.com/Goekdeniz-Guelmez/mlx-lm-lora/blob/v5.10.1/skills/mlx-lm-lora/SKILL.md
- Official server: https://github.com/Goekdeniz-Guelmez/mlx-lm-lora/blob/v5.10.1/mlx_lm_lora/mcp_server.py
- Upstream release: https://github.com/Goekdeniz-Guelmez/mlx-lm-lora/releases/tag/v5.10.1

## Evaluation-first operator contract

1. Choose one existing and authorised Pryntor task with owner, exact objective, baseline, genuinely held-out examples and an independent reviewer. PRY-309 remains the canonical improvement loop. Check whether better prompting, retrieval or deterministic code is sufficient before training.
2. Keep the first proposed pilot on synthetic-only Pryntor Core release-evidence classification. Do not import Jellyfish/client materials, secrets, merchant PII, children's data, employer-owned code or private customer records into public artifacts or Hugging Face.
3. Allow zero unapproved spend. Do not buy hardware, rent GPU, enable metered providers, publish an adapter, modify production, execute background training or activate agents as a side effect of reading this file. No cross-company rollout without separate domain gates and reviewer sign-off.
4. A real experiment is possible only on an explicitly authorised Apple Silicon Mac with verified free/local compute, package/license security review, sufficient resources and a project-scoped installation. Use the upstream release by exact tag/commit in an isolated Python environment. Prefer stdio MCP only, not LAN HTTP. The upstream MCP server is not tenant-isolated.
5. Discover live tool schemas and call validate_model_support, then inspect_dataset, then check_training_config SEQUENTIALLY. If any tool is missing, errors, or check_training_config does not explicitly state “Config looks good.”, stop. These checks alone are not proof of safe GPU fit, valid data, or learning success.
6. A separate founder-approved bounded run may use start_training with exact model and immutable revision, legally vetted dataset splits, capped steps/batch/time, and run logging. Never self-approve or self-merge. Preserve all source hashes, run ID, logs, adapters and true cost.
7. Compare real baseline vs candidate on untouched held-out examples and negative regression cases; score only with independent outcome criteria and domain expert review. No claim of improvement without actual measured evidence and appropriate sample size. Report BLOCKED, REVIEW_ONLY or RELEASE_CANDIDATE, never SHIPPED from a static fixture.
8. Report exactly: runtime/hardware, source revision, model/data rights, what genuinely ran, held-out delta and negatives, remaining blockers, named reviewer, cost, and whether anything was actually installed. Follow PRY-AIG-001, PRY-GOV-001/002 and PRY-199.

First candidate model for *future* validation: https://huggingface.co/mlx-community/SmolLM2-135M-Instruct (model page declares Apache-2.0; its immutable revision and actual training compatibility must be checked before running). Synthetic gate/test fixture and read-only Mac runbook were delivered privately in the original founder conversation; they are not proof of production installation.
