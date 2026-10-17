# Earshot v0.2 in Motion Director (PRY-195)

## Status
**Included in draft PR #3:** an original offline audio-technical gate and generated-fixture tests.
**NOT installed / NOT independently evaluated:** full upstream Earshot package, CLAP/AST models, MCP server, forge v2, fit audio-to-code. Do not treat this document or a passed technical unit test as a production audio quality signoff.

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

## Future production install and signoff
1. Confirm the actual Pryntor-owned private motion/film repo and stable host; pin upstream commit and check dependencies and model licences.
2. Install in project-local environment, authorize model download only after disk, egress, and cost review; run `python -m earshot doctor --load`.
3. Produce with licensed assets: `earshot measure`, `timeline`, `critique`, `forge` and `fit` test evidence, plus objective A/B against reference and human review.
4. Verify MCP tool discovery in an authorized client; no secrets in repository and no `llm --yes-upload` without approval.
5. Save per-venture rights ledger, technical measurements, generated media, reviewer identity, approval and CI run. Never auto-merge or auto-publish.
6. Route applicable production flows: Studios, BTWW, AFTERLIGHT, LVL7 explainer media, Tirisano approved promos, Voice audio measurement and Game Studios SFX; unrelated services do not get an installation by default.

Aesthetic taste, speech transcription, license provenance and brand approval are not determined by Earshot. Source comparisons are hints and cannot substitute an independent human reviewer.
