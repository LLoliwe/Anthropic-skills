# Existing LVL7 science playground
Expands PRY-254 and PR #60 from one Water Lab into eight experiment areas and 24 challenges. This is the same LVL7 product, not a new venture or repository. Hosted review URL: https://lvl7-learning-atlas.lebololiwe.chatgpt.site . Hosting source commit f00f187260832c5534cd791c46b18c48791cbe4a.

Water, atoms/ions/isotopes, molecule composition, reaction balancing, DC resistor circuits, Earth/Moon/Mars gravity, toy food webs and sound waves. Original diagrams, working controls, local anonymous notebook, subject navigation and related paths. Six chemical element types in the composition tray, seven molecule targets, four balancing equations, first 20 elements in atom builder. No AI tutor, measured mastery, scientific curriculum approval or competitor parity claimed.

From this directory: `node build.mjs`, then `node --test tests/science.test.mjs`. With jsdom 26.1.0 on NODE_PATH: `node --test tests/science-dom.test.cjs`. Serve built `dist/` as the static web root. Build copies canonical existing Water Lab and shared graph, with no upstream Marble data vendored. All eight areas are available without loading Marble data.

Validation: 10 model/integrity tests plus eight DOM interaction suites passed, including correct/incorrect answers, idempotent rewards, ecosystem model time, actual ballistic landing, switches, reset, safe notes, filters and water reward bridging. DOM checks are not browser rendering or physical-device tests. New browser QA unavailable in the Sites environment; scientific/educator, independent accessibility/privacy/licensing, visual and iPhone review remain open.

Reference mechanisms: Marble connected exploration, PhET interactive science breadth, Toca Boca Jr playful multiple experiences. No competitor app code, branding or artwork reused. Optional Marble atlas retains source pin, licence attribution and checksum checks.
