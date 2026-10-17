# Asko V2 — illustrated, genuinely interactive local-first code explorer

Product brand: Asko (provisional pending a trademark/domain clearance); built by Pryntor. The public-facing UI is not named Pryntor.

## Real working product
- Original saturated lilac/blue/mint/pink responsive editorial landing page, hand-authored editable SVG of Ari (human guide) with her black cat. No proprietary third-party mascot pixels copied.
- Ari's pointer gaze, hover animation respecting reduced motion, click/keyboard opens an accessible local guide with keyboard-operated quick questions, typed prompts and close control.
- Ari is deliberately honest: an in-browser deterministic guide, NOT an LLM or remote agent. Reads the existing scanner's report metadata and explains real file counts, relative import relationships and heuristic notes. No fabricated live answers, no data transmitted or message persistence.
- Existing V1 capabilities preserved: local JS/TS/JSON/HTML/CSS scanner, import graph, file/finding filters, Cmd/Ctrl+K palette and local JSON export. Raw source never appears in exported report. CSP blocks external connections.
- Hero mini-graph is clearly marked SAMPLE. Buttons actually open local files, run the sample, navigate graph, invoke shortcuts or open guide.

## Release and compliance boundaries
V0 remains https://pryntor-inspect.onrender.com . V1 remains https://pryntor-inspect-v1.onrender.com . Build V2 on feature/asko-v2-illustrated-interactive-20261017 and deploy to its own free Render static service, auto-deploy off. No changes to existing deployments. Public preview does NOT expose REA server tools or support arbitrary confidential third-party source without permission. No formal SAST audit or independent human security approval claimed.

## Verification
Run Node tests: node --test apps/pryntor-inspect/test.mjs apps/pryntor-inspect/v1-test.mjs apps/pryntor-inspect/asko-test.mjs
Browser QA: desktop and mobile mascot/guide, guide before and after source scan, graph and filters, export, keyboard, no JS errors/overflow/cross-origin requests; axe automated and manual accessibility gates. Real external testers and qualified independent review remain separate.

Reference art direction: user-provided Gakku / HyperFrames cartoon and mascot examples, Krea illustrations, BRRRANDING editorial design and approved Asko concepts. Original implementation without vendor logo or proprietary artwork copying.

## V3 isolated competitor-benchmark workbench (not the approved V2)

Competitor feature references (research only, no copied UI/code): GitHub code search, Cursor's codebase context and Sourcegraph's navigation/dependency features. Sources: https://cursor.com/docs , https://sourcegraph.com/docs/code-search , https://sourcegraph.com/docs/getting-started .

**Implemented original features** in new V3 separate preview: transitive reverse-import impact tracing with cycle-safe traversal, direct vs indirect labels, explicit import paths, file-jump buttons, metadata-only project search (filenames, extension, finding titles/help), and downloadable impact JSON excluding source text. All local-only; no model/network, no unsupported symbol-level, repository-wide or compiler-accurate claims.

Verified 29/29 local Node tests; browser desktop/mobile with original sample and 3-file synthetic TS chain, transitive impact, search jump, download, no JS exceptions, external requests or horizontal overflow. Awaiting hosted CI and separate Render deployment and independent review. V2 approved frozen branch release/asko-v2-approved-baseline-20261017 must not change.

## V4 / concept-fidelity visual preview (separate from all banked previous releases)

Input: user's exact shared ChatGPT concept image https://chatgpt.com/s/m_6ad38258030c81919c3b62e48fda441a — OG image retrieved directly in research, generated previously for this user's Asko project. Two cropped user-provided concept art images, concept-hero.webp and concept-portrait.webp, are source-controlled separately and clearly marked illustrative. The rest of the responsive UI is actual semantic HTML/CSS and JavaScript, not a screenshot pasted into the page.

Implemented visual fidelity: reference grid proportions, asko BETA top search/nav, sticky left sections, large left-aligned three-line bold headline, soft lilac/pink/yellow/mint editorial art, no neon/glow overload, three pastel feature cards, three functioning example project buttons, interactive CSS quick demo and Ari partner card. Calm hover/pointer parallax with reduced-motion support. Three demo projects use true sample 3/2/2-file structures with authentic import graph; no fabricated customer history, fake AI assistant, fictitious pricing plans or nonexistent videos. Section links, search palette, Ari assistant, upload and demo buttons all genuinely work; V3 local impact lab untouched.

Current released baselines remain separate: founder-banked V2 release/asko-v2-approved-baseline-20261017 / https://asko-v2-preview.onrender.com; V3 code intelligence lab https://asko-v3-lab-preview.onrender.com; V0/V1 independent. This preview is a visual fidelity V4 candidate, not founder-accepted release nor human security-approved production deployment. User's original concept screenshot is design reference; no outside vendor branded assets included.

QA: node --test apps/pryntor-inspect/test.mjs apps/pryntor-inspect/v1-test.mjs apps/pryntor-inspect/asko-test.mjs apps/pryntor-inspect/v3-test.mjs apps/pryntor-inspect/concept-test.mjs
Real desktop 1536, tablet 1024 and mobile 390 browser interactions; six axe automated WCAG A/AA states zero violations (manual accessibility still required); source text stays local with CSP connect-src none.
