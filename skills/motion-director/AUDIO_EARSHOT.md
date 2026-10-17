# Earshot v0.2 in Motion Director (PRY-195)

## Status
Pinned upstream installation, stdio initialization, enumeration of 13 tools, `measure(path)`, synthetic recording-to-code/rerender, CLAP/AST loading and non-fast critique passed hosted acceptance [39007126097](https://github.com/LLoliwe/Anthropic-skills/actions/runs/39007126097) at head `46206f1`. Downloaded evidence ZIP SHA256: `b81ef207b6c80dd0b121d9984f6888335ef319f3947bd4a92bb092bde998a922`.

This verifies those capabilities on original synthetic fixtures. The critique returned **not launch-grade** (0.345), so a successful integration test is not film release approval. Forge, the offline bridge, a persistent production host, final soundtrack rights and human creative review need their own evidence. Preserve the final-head CI result with any merge decision.

## Primary source and license
Upstream: https://github.com/Leonxlnx/earshot
Inspected revision: `972132643583fc0b9a60c6c50983ed7dc1aa55bf` (2026-10-17 read).
Upstream `pyproject.toml` version 0.2.0; `LICENSE`: MIT (Copyright 2026 Leon Lin).
Upstream uses Python >=3.10, FFmpeg/FFprobe, CPU models. CLAP and AST weights have their own licences. Model cold starts and ~1.4 GB cache demand a persistent authorized runner.
Limitations: https://github.com/Leonxlnx/earshot/blob/main/docs/LIMITS.md

## Running the actual included gate

```bash
python skills/motion-director/scripts/audio_gate.py /path/to/render.mp4 --report /path/to/audio_qc.json
python -m unittest discover -s skills/motion-director/tests -p 'test_audio_gate.py' -v
```

The script uses stdlib + ffmpeg/ffprobe, decodes the first audio stream, reports duration and SHA256, and checks sample peak, mean volume, missing audio and broken audio streams. Default thresholds: mean >= -45 dBFS, max sample peak <= -0.5 dBFS. These values are initial technical defaults, not mastering standards for all use cases; calibrate by distribution platform. A movie with no audio fails unless a meaningful `--intentional-mute 'reason'` is recorded; the exception still requires human signoff.

To request opt-in **local-only** model review after a verified installation:
```bash
python skills/motion-director/scripts/audio_gate.py /path/to/render.mp4 --earshot-review --report /path/to/audio_model_qc.json
```
This sets `EARSHOT_OFFLINE=1`; absence of Earshot or cached models returns BLOCKED/FAIL. It does not make external LLM calls. `--earshot-review` has not yet been validated against real upstream 0.2.0 weights. No code here installs the package or downloads weights.

## Production install and signoff
1. Confirm the actual Pryntor-owned private motion/film repo and stable host; pin upstream commit and check dependencies and model licences.
2. Install in project-local environment, authorize model download only after disk, egress, and cost review; run `python -m earshot doctor --load`.
3. Produce with licensed assets: `earshot measure`, `timeline`, `critique`, `forge` and `fit` test evidence, plus objective A/B against reference and human review.
4. Replay `.github/workflows/earshot-upstream-acceptance.yml` on the target host; inspect `mcp-validation.json`, `doctor.json`, `critique-validation.json` and `dependencies.log`. The test pins MCP SDK 2.3.0 and times out the stdio phase after 180 seconds. Register the stdio process in an authorized local client, keeping its filesystem private; do not expose it as a public unauthenticated service; no secrets in repository and no `llm --yes-upload` without approval.
5. Save per-venture rights ledger, technical measurements, generated media, reviewer identity, approval and CI run. A software merge does not grant film approval or permission to publish.
6. Route applicable production flows: Studios, BTWW, AFTERLIGHT, LVL7 explainer media, Tirisano approved promos, Voice audio measurement and Game Studios SFX; unrelated services do not get an installation by default.

Aesthetic taste, speech transcription, license provenance and brand approval are not determined by Earshot. Source comparisons are hints and cannot substitute an independent human reviewer.
