# LVL7 liquid engine — secure iPhone test environment (17 Oct 2026)
**Purpose:** Fix the user's REAL iPhone recording where dragging the stage HEAT range left/right leaves 20.0°C unchanged. Proven reproducible in Chromium when JavaScript is OFF: standard HTML slider still moves but DOM and Canvas don't update. File attachment is opened in the native ChatGPT/iOS HTML file viewer. Not evidence of a defective Navier–Stokes solver. **Serve over HTTPS and tap Open in Safari.**

## Technical fixes
- Visible fail-safe banner by default, hidden only after actual JS/Canvas initialisation; no-script QuickLook presents a warning rather than a fake working UI.
- Visible engine status and render FPS/events counters on stage so actual Safari screenshots diagnose status.
- Real mobile heat range, canvas slosh, 34-base particles, physics-derived bubbles and steam, live vapour fraction and existing R4 theme selectors.
- iOS DeviceOrientation explicit grant via click, sensor event acknowledgment only after data; drag/touch fallback. Secure HTTPS origins necessary; request permission in Safari rather than ChatGPT file preview.
- No personal learner data, no device-motion telemetry transmission, no paid compute/API.
- Internal pilot; approved R4 visuals remain frozen at branch release/lvl7-r4-approved-20261017, commit 31dcfa3096be4f5b5492fe694fce21eec18737cb.
- iPhone hardware test still required, Chromium/mobile emulation isn't native Safari, and physics remains idealised illustrative not photoreal liquid CFD.

## Testing
Local JavaScript on: 100°C shows 100 and emits bubbles + gas; MAKE GAS increases vapour and emitted gas. JavaScript off: the slider moves while labels freeze at 20°C, matching user's exact video, and banner stays visible. Hosted CI uses real Playwright Chromium for 320/390/430/1440, plus JS-disabled regression.
