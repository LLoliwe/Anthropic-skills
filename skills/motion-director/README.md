# Motion Director (original agent-ready production skill)

A concrete production pipeline based on the **structure** of Owi's public TuYo making-of thread, not a copy of TuYo's imagery or footage. A deterministic original motion renderer is included so the agent can produce real frames and a real MP4 rather than just prompts.

## Quick start

Install Python 3.10+, Pillow and FFmpeg. From repository root:

```bash
python -m pip install -r skills/motion-director/requirements.txt
python skills/motion-director/scripts/motion_director.py plan skills/motion-director/examples/signal-demo.json
python skills/motion-director/scripts/motion_director.py qa skills/motion-director/examples/signal-demo.json
python skills/motion-director/scripts/motion_director.py render skills/motion-director/examples/signal-demo.json --seconds 6 --output preview.mp4
python skills/motion-director/scripts/motion_director.py handoff skills/motion-director/examples/signal-demo.json --outdir handoff
```

**Preview:** 6-second playable MP4, no approval required. **Final:** `render ... --final --output final.mp4` refuses until all shots have been explicitly approved with `approve`.


### Start from a new brief (not just the example)

```bash
python skills/motion-director/scripts/motion_director.py init \
  --output /tmp/my-launch.json \
  --name "Original Product Launch" \
  --brand "YOUR BRAND" \
  --message "See what matters" \
  --audience "operators" \
  --channel "social" \
  --aspect 1:1 \
  --bpm 120
python skills/motion-director/scripts/motion_director.py plan /tmp/my-launch.json
```

The `init` command creates a **deterministic editable template**, not an AI-authored script. A directing agent must rewrite the storyboard with authentic product facts before any commercial use. Edit `asset` on a device shot to point to a locally licensed PNG/JPEG screenshot; the renderer places it in the phone screen. Referenced assets must exist. For a changed sequence, use `reorder /tmp/my-launch.json --order S02,S01,S03,S04,S05,S06`. This invalidates prior approvals. Use an actual rights-cleared music file via the `music` field; the 120 BPM grid is not automatic beat detection.

### Revise and approve

```bash
cp skills/motion-director/examples/signal-demo.json /tmp/my-film.json
python skills/motion-director/scripts/motion_director.py revise /tmp/my-film.json --shot S03 --duration 4.5 --note "Tighten on beat"
python skills/motion-director/scripts/motion_director.py approve /tmp/my-film.json --shot S03
python skills/motion-director/scripts/motion_director.py approve /tmp/my-film.json --all
python skills/motion-director/scripts/motion_director.py render /tmp/my-film.json --final --output /tmp/my-film.mp4
```

Approval must come from an actual human director. The CLI records it but cannot authenticate who typed it; production teams should keep approvals in their review system.

### Files

- `SKILL.md`: agent contract, creative/editorial loop, human gate, tool routing
- `scripts/motion_director.py`: deterministic per-frame seek renderer, FFmpeg MP4, timeline QA, revisions, handoff
- `examples/signal-demo.json`: original 30-second six-shot synthetic UI demo, 120 BPM
- `tests/test_motion_director.py`: automated tests

### Constraints

This is a **functional local renderer and agent skill**, not a cloud video-generation service. It does not call Claude, Hugging Face, Adobe, Ultramockup, Premiere, Figma, Lovable, or Vercel. Real product screenshots and rights-cleared music may be added later. The sample animation is original illustrative UI; not a verified recording of any live Pryntor product.

Exports: MP4 if FFmpeg exists; PNG contact sheet; JSON QA/provenance; CSV edit decision list; markdown compositing handoff. Fail closed if FFmpeg is missing or a final film lacks approval. No public posting, cloud compute or paid generation is triggered.

## Earshot v0.2 / audio-technical quality gate

The optional audio QA is implemented in `scripts/audio_gate.py` and documented in [AUDIO_EARSHOT.md](AUDIO_EARSHOT.md). After a rough render, run `python skills/motion-director/scripts/audio_gate.py preview.mp4 --report audio_qa.json`. It decodes and checks audio locally using FFmpeg; an unintentionally muted sample **fails**. When intentional silence is approved, record the reason using `--intentional-mute` and preserve human signoff. `--earshot-review` requires separately installed and cached Earshot 0.2.0 and blocks without it. Neither this gate nor a model result proves creative approval, music licensing or company-wide installation.


## Earshot v0.3 real sound-kit preview (PRY-195, 19 October 2026)

The **optional, already implemented** `scripts/earshot_v03_soundtrack.py` is a distinct,
model-free v0.3 production adapter, not a claimed migration of the separately pinned v0.2
listening-model acceptance workflow. It generates real WAVs from Earshot's bank, validates
`kit.lock.json` (bank version, audited sound ID, SHA1, measured onset/peak, filename and
warnings), mixes six sounds to exact frame timestamps in our existing original 30-second
six-shot demo, and can mux a **private, not creatively approved** MP4. It generates receipts
(`soundtrack-evidence.json`) and preserves upstream credit and human-review gates.

**Verified 19 Oct:** existing PR #3 head `0032384d39c80a79b0b8f6695cda39c9853be0ab`,
[actual v0.3 rendering CI run 39181878462](https://github.com/LLoliwe/Anthropic-skills/actions/runs/39181878462)
**PASS** (5/5 new tests, 6/6 sound takes without upstream audit warnings,
30.000-second H.264+AAC synthetic-preview render, existing offline audio gate technical PASS,
zero CLAP/AST model downloads or paid APIs). CI artifact:
[real 30-second review MP4, standalone PCM WAV, six takes, lock and audit receipts](https://github.com/LLoliwe/Anthropic-skills/actions/runs/39181878462/artifacts/12156646821).
The prior v0.2 upstream acceptance remains separate.

For authorized use with the exact checked source revision
`Leonxlnx/earshot@925ebe56a1b755e5d354ab642bb8f344440cfa9c`,
Python >=3.10, FFmpeg, and NumPy / SciPy / soundfile / soxr / pyloudnorm:

```bash
# From repo root, after installing the exact pinned upstream Earshot v0.3 source locally
export EARSHOT_OFFLINE=1 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
python skills/motion-director/scripts/earshot_v03_soundtrack.py \
  skills/motion-director/examples/signal-demo.json --plan-only
python skills/motion-director/scripts/motion_director.py render \
  skills/motion-director/examples/signal-demo.json --output /tmp/pryntor-demo.mp4
python skills/motion-director/scripts/earshot_v03_soundtrack.py \
  skills/motion-director/examples/signal-demo.json \
  --video /tmp/pryntor-demo.mp4 --outdir /tmp/earshot-v03-preview
```

`earshot kit render/check` is a DSP-only path, so no listening-model download is
needed. This adapter intentionally uses only six fit/forge bank choices, not all
201. Upstream source MIT licence and bundled fitted CC0 recordings have separate
provenance in upstream `docs/CREDITS_FIT.md`; preserve notices if distributing.
The simple preview is *not* proof of polished sound, a licensed music bed, an
approved aesthetic, a persistent Earshot host, an installed company-wide runtime,
or production release. **No merge, external outreach, paid spend, or publication
is authorized by this technical success.** Directors and venture owners must
review genuine output and assets before per-venture adoption.


## Original GenAI Foley + Earshot 0.3 (PRY-195, 19 October 2026)

**Implemented, private review only.** The optional
`scripts/earshot_genai_mix.py` accepts a locally saved **genuinely generated**
external model sound effect, an already generated Earshot 0.3 kit, five
verified sound-bank takes, and the original Motion Director MP4 with JSON
receipts. It replaces only the S02 `snap` effect and leaves the video stream
untouched. It does **not** pretend Earshot is a generative model.

**Actual GenAI provider call:** The existing-credit Runway "Lebohang"
workspace produced an original two-second organic toggle foley through its
Sound Effects generative model. Provider task
`9c711ef8-7d11-4c12-9935-68e4abab403d`. Original MP3 SHA-256:
`26cdd2cfa7af5e1b56a3630e377bd280e193224c719b180eb4fc73261da79b6c`.
Cost: **two existing Runway credits; R0 new cash.** The model audio attack
was measured at 0.352 seconds into the recording and aligned to
**video frame 156, t=6.500 seconds at 24fps**. Earshot's other five sound
effects retain their verified take hashes and onset/peak alignment.

**Actual hybrid output proof:** 30.000-second H.264/AAC MP4 with SHA-256
`b8bfb7891cee71104ae0935fcff1ea656471d57e410474b5609270e9799decde`,
48kHz stereo WAV, and `hybrid-evidence.json`. The compressed-video packet
MD5 remained exactly `6c5506dc7c824060c5a0067f0ec1ee80` from the original
film. Max decoded audio level -9.0 dBFS, no digital clipping. Human sound
aesthetics, licensing, music/soundscape choices and commercial use still
require independent review. The external audio itself is not committed.

Reproduce privately on source artifacts and a licensed-in-workspace
generated audio file, with FFmpeg + NumPy + soundfile:

```bash
python skills/motion-director/scripts/earshot_genai_mix.py \
  --proof-root /path/to/pryntor-earshot-v03 \
  --genai-audio /private/source/original-effect.mp3 \
  --outdir /private/review \
  --model 'verified provider/model' \
  --task-id 'actual immutable task id'
```

The bridge validates original MP4/WAV and locked Earshot take hashes, refuses
unaudited or modified bank sounds, decodes local source audio, measures its
first perceptible onset, sample-aligns to the exact video frame, mixes with
peak safety, muxes without video re-encoding, verifies video packet identity,
and records SHA-256/technical receipt. No cloud upload or model call is made
by the bridge. A new provider generation requires its own explicitly
approved, cost-controlled request.

**CI scope:** `tests/test_earshot_genai_mix.py` and
`earshot-v03-soundtrack.yml` use an obvious synthetic sine fixture to
test interface/codec/QA only, **not** to impersonate live model output.

**Video model limitation:** Krea image-to-video was attempted on the user's
existing account, and returned 402 ("higher plan required") without generating
any video or charging credits. The connected Runway workspace has no eligible
video-generation model. Visuals therefore remain the prior original
synthetic 30-second film, not a new generative video. This proves a
**GenAI-sound plus procedural-Earshot workflow**, not a polished animated
film, installed company-wide runtime, approved campaign, published product,
commercial licence, merged source or paid upgrade.
