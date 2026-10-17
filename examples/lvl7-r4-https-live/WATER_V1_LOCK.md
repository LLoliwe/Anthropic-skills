# LVL7 WATER V1 — USER-VERIFIED WORKING BASELINE

**Status:** V1 WORKING, user-verified on an iPhone; archived as a technical/interaction baseline, **not** a production learner release or a scientific validation.

## Acceptance and provenance

- **Date:** 17 October 2026 (South Africa local date).
- **Founder first-hand confirmation:** "This is fucking dope. The water worked. Bank it for us as a v1 working water."
- **Exact verified running service:** https://lvl7-liquid-iphone-live-preview.onrender.com
- **Hosting:** Pryntor Render static-site ID `srv-db9q9qjbc2fs73crl9dg`, deploy ID `dep-db9q9r3bc2fs73crlbag`, **LIVE**, autoDeploy **OFF**.
- **Exact rendered application code:** `examples/lvl7-r4-https-live/index.html`, Git blob `9c574c3d2f14a1ce219d6d3858fcfba0be9d74e0`.
- **Live deploy commit:** `af143a0efde30c8000d1e4337af3940dfe373b75`.
- **Merged shared-main implementation:** PR [#42](https://github.com/LLoliwe/Anthropic-skills/pull/42), squash commit `fe0312e2fdb0bd172da8c25f296696c51138c965`. The main-branch application file has the **exact same Git blob** as the LIVE deployed file.
- **Frozen source snapshot:** `release/lvl7-water-v1-working-20261017` pointing to `fe0312e2fdb0bd172da8c25f296696c51138c965`. Keep it as a stable reference, not a rolling development branch.
- **Latest-head CI evidence:** [GitHub Actions 39050786296](https://github.com/LLoliwe/Anthropic-skills/actions/runs/39050786296) SUCCESS on `fac7fb1e2627af32c1da672204acfa7ad0fda98a`, with four viewport smoke tests and no-JS failure-mode test. The only intervening change between `af143a0` and `fac7fb1` was the desktop-visible-control test selector; the HTML blob was unchanged.

## Verified operational behaviour

- Direct iPhone user confirmation: the **water worked** on the hosted version, unlike the frozen 20°C HTML attachment.
- Independent remote mobile browser showed actual `LIQUID ENGINE RUNNING`, Heat input reaching **100.0°C**, approximately **34 FPS** during the sample and **20% vapour at 77.90 kJ** after Make Gas.
- Live water stage includes user-directed finger slosh, idealised waves/viscous damping, rising boil bubbles, vapour plume, progressively reduced water level and stage-adjacent mobile heat control.
- The preceding attachment failure was reproducible with JavaScript disabled: the browser could move a native range control while the app temperature remained 20°C. In that case the HTTPS app now displays a clear engine-guard message.
- **Not yet independently verified on the physical iPhone:** sensor/tilt permission and fidelity, long-run framerate/battery use and all WebKit accessibility behaviours. The founder's general "water worked" confirmation is NOT fabricated into an explicit motion-sensor approval.

## What V1 means, and what it does not

**Banked:** founder-approved *R4 visual language* and a separate, working, browser-executed *Water V1 motion/boiling/gas engine*. Future iterations should build from this baseline or a new feature branch, with a clear rollback route and before/after comparison.

**Not approved:** native iOS deviceorientation pass, physical fluid CFD accuracy, boiling/gas science curriculum signoff, child privacy/safeguarding/AA accessibility certification, public learner product release or commercial revenue.

**Release policy:** keep Render autoDeploy OFF and stable source snapshot intact; verify HTML blob before future deployments. For V1.1 or V2 create a new branch and preview URL, do not overwrite V1 without explicit approval. Zero-new-spend-first.

**Company tracking:** [LVL7 PRY-254](https://linear.app/pryntor/issue/PRY-254); [design governance PRY-252](https://linear.app/pryntor/issue/PRY-252). This document records the user-verified technical milestone independently of future pedagogical validation.
