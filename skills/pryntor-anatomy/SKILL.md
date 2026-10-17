---
name: pryntor-anatomy
description: Source-pin and safely operate Anatomy interactive isometric SVG, WebGL and experimental 3D explainers in Pryntor projects. Use for technical mechanism explainers, machine visualization or editable educational demonstrations where static design is insufficient.
---

# Pryntor Anatomy integration (company resource)

Status: **pinned installation workflow on a proposed PR, not a blanket production deployment**. This guide is original Pryntor integration instructions, not a copy of the upstream Anatomy skill.

- Official MIT upstream: https://github.com/wheresryan22/anatomy
- Reviewed source pin: `e9488296a44211c42701ff71705b7901470ec78f` (15 October 2026).
- Project-local agent installation (from this repository root): `bash skills/pryntor-anatomy/install.sh /path/to/your/project`.
- Claude Code command: `/anatomy`; Codex: `$anatomy`. The real upstream `SKILL.md`, kit, references, examples, and tests are installed by the script, not bundled in this guide.
- No keys or paid model access required for the kit itself. Agent costs, generated image APIs, compute and hosted deployment can still cost money.
- Requires git and tar; for builds Node.js >=20.10; for automated screenshots Chrome/Chromium.
- Installation **refuses overwriting existing skill directories**. Inspect existing versions first.

## Approved use cases and prioritization

1. **LVL7 / Show Your Working:** original manipulable maths or physics instruments with verified mathematical models and accessible written explanations.
2. **Pryntor Robotics:** labelled kinematic teaching figures; never substitute the illustration for MuJoCo tests, safety analysis or physical evidence.
3. **Pryntor Studios / BTWW:** interactive technical editorial components and mechanism explainers, selectively alongside TasteSkill, Blender and HyperFrames.
4. **Pryntor Recover / Pryntor web, Tirisano:** demos of genuine process flow where physical metaphor helps comprehension; private client data cannot enter public galleries.
5. **Other ventures:** optional only after clear benefit, adequate loading/accessibility performance and zero-new-spend assessment.

## First proof / acceptance gate

- Verify the exact official commit after install and presence of `SKILL.md`, `kit/`, `examples/`, `scripts/`.
- Rebuild the pinned upstream dial indicator in both themes with `node examples/dial-indicator/build.mjs [--light]`.
- Use the upstream Chromium `scripts/capture.mjs` to check desktop + mobile and reduced motion, and inspect actual rendered screenshots. Record HTML and PNG artifacts and reviewer.
- First business-specific pilot: LVL7 source-backed physics/measurement instrument (simple dial gauge or ripple tank) with model values reviewed by an educator; not a claim of an automatically validated educational resource.
- Test keyboard interaction, semantic text alternatives, zoom, dark/light appearance, mobile frame rate, and motion-reduction behavior.
- Do not publish to the Anatomy community gallery or upload customer/learner data without explicit separate permission.
- Do not mark GA, production-ready, or deploy across apps until security, performance, accessibility, licensing and human visual QA pass.

## Independence and rollback

Version the upstream SHA, generated output, preview artifact and original model inputs. Pin upgrades in a separate PR; compare changes and rerun CI. To roll back, remove only the `anatomy` directories created by this installer after checking for local edits; revert the hosting app deployment independently.

Company owner: Engineering/Design Systems. Source-of-truth rollout task: Linear. Default spend: R0.
