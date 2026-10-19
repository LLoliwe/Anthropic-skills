# LVL7 Water Lab — Gamified V1.1 / Founder review
Working, mobile-first green-and-cream learning game. New original hand-authored SVG mascot **Bloop**, live green mission bar, XP, local streaks, three unlocking badges, real phase-based water physics, science mini-graph, reasoning, heat/gas/tilt/touch controls. No use of Cash App branding or source.

**Source of physics:** preserves the original Pryntor, founder-verified Water V1 engine design from `release/lvl7-water-v1-working-20261017`, with small UI-binding change only for nested button text. Idealised 100g water at 1atm: heat from 20C to boiling 33.44kJ; total to vapour 259.04kJ. Illustrative 2D fluid, NOT CFD.

**Game integrity:** XP starts at zero (no fake preview scores). 50 XP at boiling, 70XP after >30% gas, 100XP at full vapour. Awards exactly once per locally saved browser session. No real child identity, telemetry, server storage, ads, payment or third-party AI. Local progress can be reset using the profile icon. Daily streak only after earning a real badge.
**Failure guard:** open via a real HTTPS site, not a ChatGPT iPhone HTML attachment; JS-disabled viewer shows a visible warning. Tilt sensor permission requires user gesture. Touch dragging remains available.
**Tests:** tests/browser.cjs for 320/390/430/768/1440 real Chromium, actual emitted bubbles/gas, 3 badge awards and rewards, game resets, first reasoning error, waves and JS-disabled fallback.
**Release:** V1.1 is new, separate and unapproved; existing V1 HTTPS demo + code snapshot must not be overwritten. Requires founder review and real iPhone/educator/accessibility QA before learner-facing launch. No paid tooling required.
## Learning atlas integration (PRY-254, 18 October 2026)
`curriculum.html` extends this existing app with original LVL7 styling, selectable graph nodes, accessible concept lists, search, subject/age filtering, prerequisite sequences, hard/helpful-link switching, reverse unlock links and navigation into the existing Water Lab. The banked V1 demo and physics engine are unchanged.

Starts with six original demonstration concepts and makes **no external requests** until the user chooses to load Marble's graph. Fetches only unchanged `topics.json` and `dependencies.json` from upstream commit `96a7933754af672e1bfdbf7ecb05c325860c6e0d`, verifies both official SHA-256 checksums and all graph integrity checks before replacing the starter graph. Errors preserve the current graph and allow retry. No upstream data is vendored, transformed, persisted or exported. No third-party standards text, assessment prompts, names or learner profiles are displayed or collected. Source notices and licence links are visible. Country-specific curriculum alignment is not asserted.

Only the specifically related states-of-matter / heating-and-cooling topics link to the available experiment. Other concepts explicitly say no playable lesson is available. This is an exploratory graph, **not 1,590 completed lessons**, mastery assessment or an adaptive AI tutor. Founder art approval, educator review, independent accessibility/privacy/licensing review and real iPhone testing remain open. No deployment or approval is implied.

Run from repository root, served over HTTP locally or an approved HTTPS preview:

```bash
node --test tools/learning-graph/tests/graph.test.mjs apps/lvl7-water-game-v1-1/tests/curriculum.test.mjs
NODE_PATH=/path/to/playwright/node_modules node apps/lvl7-water-game-v1-1/tests/curriculum-browser.cjs
```

Optional test configuration: `CHROMIUM_PATH` for an existing browser; `MARBLE_SOURCE_DIR` for a separately checked-out upstream `data/` folder (browser transport fixture uses the real unchanged, checksum-verified files); `SCREENSHOT_DIR` for captures. Data stays outside this repository. Browser tests with the fixture are not evidence of live CDN delivery.

Validation on 18 October: 17/17 Node tests; atlas browser flows at 320/390/768/1440 with the real dataset delivered via local transport fixture; source corruption/retry check; existing Water Game suite at 320/390/430/768/1440 plus JavaScript-disabled fallback. Used Playwright with separately installed Chromium 153.0.8010.0 after the standard browser CDN returned an invalid archive. No device Safari or hosted CI pass claimed.
