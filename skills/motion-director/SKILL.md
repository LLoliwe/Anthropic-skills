---
name: motion-director
description: Direct, storyboard, render, critique, and finish original music-led product launch films from real brand assets using short deterministic UI micro-animations, editorial iteration, and human approval. Use when asked to make a product film, app launch trailer, UI motion graphics, storyboard, cinematic explainer, or an AI-assisted film production pipeline.
---

# Motion Director — an agentic launch-film production workflow

**Goal:** ship an actual original film and its editable shot plan, not an inspirational document or a fake rendered preview. Inspired by the publicly described three-phase TuYo production process by Owi, without reproducing TuYo creative assets. Source: https://x.com/owisixseven/status/2111127528211427601

## Contract

1. Ask or infer only the necessary brief: destination, aspect ratio, what changed, one thing the viewer should remember, target audience, available authentic product assets, references, rights-cleared music.
2. Produce a plain-language script **under 60 seconds**, preferably bullet-like. Each line must correspond to a visible event.
3. Produce a **timed storyboard** before rendering. Keep every shot to **two or three connected actions**. Use actual Figma frames or approved product screenshots when making product claims; otherwise visibly label synthetic demos.
4. Annotate each shot: start/end composition, action chain, easing, morph target, camera, transition, sound cue, and fallback.
5. Select tool **per shot**: code-based UI animation (Claude or equivalent), Ultramockup-style device work, After Effects manual compositing, Premiere final editorial. Never imply any named third-party tool was actually run without evidence.
6. Render the first **rough cut as soon as one shot is ready**. Review every new shot in sequence with the music; change order, timing, or delete weak shots. Do not polish an isolated clip while ignoring the edit.
7. For every revision: compare keyframes, review the transition at 100% speed, fix geometry/glitches **before** motion blur, record notes and version. Ask the creative director to approve each shot.
8. Add final motion blur, fisheye/optical character, subtle 35mm grain, and sound design **after** the cut works. Effects are optional and must be motivated; avoid overprocessing.
9. Export a real playable MP4 or explicitly report the missing renderer. Deliver contact sheet, editable JSON plan, cut/beat QA report, edit decision list, source and provenance. Never report a render as complete if no file exists.
10. Publishing, paid compute, music licensing, public-facing claims, and final client delivery require explicit approval.

## Operational sequence

**PHASE A — Direction**
- Intake brief and assets; verify rights, source URLs and product claims.
- Draft a simple 6-beat narrative: problem → transformation → proof → benefit → climax → CTA.
- Create 6 timed storyboard cards, aiming for 24–45 seconds. Put music BPM and transition notes in the same artifact.
- Run a human Figma composition pass: swap incorrect screens, fix hierarchy, add explicit motion annotations. If Figma isn't connected, work from screenshots and JSON without claiming a Figma edit.

**PHASE B — Motion**
- Build deterministic, reproducible short scenes. Keep a single timeline clock; each scene's render must support arbitrary seek(t), not rely on prior frames.
- Prioritize morphs over unrelated fades. Design state-to-state transformations with visible cause and effect. Ensure phone screens are legible.
- Route device shots to an optional mockup compositor; composite animated screen inside device. Keep the native code scene as a no-cost fallback.
- Inspect early/mid/late frames of each clip, especially blur, masks, text and transitions. Iterate the **shot**, not the whole video.

**PHASE C — Editorial**
- Assemble a rough cut from the first render; check it against actual or selected music BPM.
- Audit cuts, screen legibility, frozen holds, brand consistency, transition continuity, safe areas, audio rights and product truthfulness.
- Do a director pass that can reject, reorder, retime or delete any shot. Re-render and repeat.
- Only then finish in AE/Premiere if available; the built-in Python/FFmpeg path produces a standalone original MP4 without requiring either.

## Local deterministic runner

Requires Python 3.10+, Pillow and ffmpeg (only for MP4). See README.md.

```bash
python -m pip install -r skills/motion-director/requirements.txt
python skills/motion-director/scripts/motion_director.py plan skills/motion-director/examples/signal-demo.json
python skills/motion-director/scripts/motion_director.py qa skills/motion-director/examples/signal-demo.json
python skills/motion-director/scripts/motion_director.py render skills/motion-director/examples/signal-demo.json --seconds 6 --output /tmp/signal-preview.mp4
python skills/motion-director/scripts/motion_director.py handoff skills/motion-director/examples/signal-demo.json --outdir /tmp/signal-handoff
```

The demo is synthetic and does not claim to depict a live product. Before final output, revise shots, obtain human approval, and run `render ... --final` (all shots must be approved).

## Mandatory agent critique loop

After each preview:
- **Continuity:** what visual state exits shot N and enters N+1? Reject discontinuities that do not read as intentional cuts.
- **Pace:** are major actions on or near music beats? A beat grid is not the same as actual musical analysis. Use onset analysis only when implemented.
- **Legibility:** inspect first, midpoint and final frames, not just a hero still. Reject illegible UI text and overflowing titles.
- **Physics:** watch velocity continuity, overshoot, mask edge behavior and device screen perspective.
- **Truth:** verify product claims against authentic assets. Generated mockups are conceptual.
- **Creative judgment:** automated QA can flag measurable defects but cannot assert that a shot "feels right". Human director retains veto.

Log each revision and re-render. Do not fabricate approval or claim model-generated footage from this deterministic demo.

## Provider roles and honest boundaries

- **Hugging Face:** research/discover models and optional compute. Jobs require an explicit cost and licensing check. This skill works offline.
- **Figma:** storyboard screens and motion annotations. Connected Figma write permissions must be verified before editing.
- **Adobe:** Firefly assets, optional compositing, AE/Premiere handoff. An Adobe connector does not automatically provide full After Effects/Premiere timeline automation.
- **Lovable:** optional control-room UI; not required to run this skill.
- **Vercel:** optional deployed control room or authorized rendering worker; no deployed worker is implied.
- **Wolfram:** deterministic tempo/time/safe-area calculations when needed; basic arithmetic is implemented locally.
- **Undermind:** research evidence for visual perception and temporal continuity, not a renderer.
- **Linear:** project, shot and QA tracking; do not mark a film complete without the MP4 and review evidence.

## Deliverables and exit gate

A valid run must provide: source brief, original script, timed shot plan, actual preview or final file, contact sheet, QA report, provenance log, and a human review status. Distinguish **planned**, **rendered**, **reviewed**, **approved**, and **published**. A shot marked rendered is not automatically approved.
