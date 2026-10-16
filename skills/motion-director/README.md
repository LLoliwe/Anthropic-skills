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
