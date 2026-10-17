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

## V5 motion-native rebuild — no cropped raster hero or guide card (17 Oct)

User explicitly rejected static image cutouts in V4 iPhone review. This new, independently deployed V5 candidate keeps reference-faithful calm dashboard composition but eliminates ALL screenshot/raster image layers. Main Ari figure, the separate foreground cat and the guide-card portrait are inline, hand-authored SVG vector drawings; there are no concept-hero.webp or concept-portrait.webp assets in this branch.

- True interactive hero graph: actual local relative-import relationships rendered as SVG curves and keyboard/touch-operable HTML nodes. Sample preview labelled SAMPLE and replaced by real source report. Clicking nodes loads the real fixture or inspects selected files.
- Animated Ari and cat: pupils track pointer, figure breathes slowly, tail reacts to hover, character click opens deterministic local guide, separate vector foreground cat visible on mobile. Respects prefers-reduced-motion. No remotely rendered models, external scripts, or false AI claims.
- Actual coded editor microdemo: HTML code lines, syntax accent colours, graph lines/target chips, play/pause and step buttons. Play loads the original three-file fixture and stages authentic counts rather than fake telemetry.
- Responsive original design: desktop 1536, tablet 1024, mobile 390 and compact 360 tested; zero raster hero/card images and no external requests. Browser native vector rendering at arbitrary resolution, no WebGL dependency.

Verification: 38/38 local Node tests; Chromium interactions for nodes, file rows, Ari modal, source demo and playback on four breakpoints; axe automated six A/AA states 0 violations after line-number contrast fix. Hosted CI, independent expert review, consented user testing and brand clearance separate gates. Banked V2 https://asko-v2-preview.onrender.com , V3 https://asko-v3-lab-preview.onrender.com and V4 https://asko-concept-preview.onrender.com remain untouched, no spend or automatic merge.

## V6 — responsive illustrated interaction repair

Trigger: user iPhone screenshot of V5 with feedback that character was squashed and static/boring. V6 is a **new isolated preview**, not an overwrite of V5 or founder-frozen V2.

- Re-authored BOTH inline SVG representations of Ari with genuine seated 3/4 composition, layered curly hair, facial expression and blink, carefully outlined cream cap, original striped sweatshirt, dimensional folded trousers and separate detailed sneakers. Unique SVG IDs for each instance, so gradients never cross between hero and guide card. No raster assets, Lottie license dependencies, external fonts, images, network or paid APIs.
- Fixed verified intrinsic SVG grid sizing regression at desktop breakpoints: hero art previously rendered 517.9px inside 431px stage and clipped, whereas V6 grid row/visual match stage exactly. On mobile art has a fixed un-squashed 380/390px section; Ari is offset left to keep her face **unobstructed** by the actual graph. Original cat now has its own keyboard/touch-activatable live tip bubble.
- Live graph file buttons use 44px+ touch targets at phone sizes, selected file is accurately preserved through sample event reset, and their chosen filename appears in actual source detail. Actual relative-import paths power moving CSS offset-path indicators; no fake customer counts. Uses CSS path motion rather than screenshot-problematic SVG SMIL.
- Natural animations: hair and loose curl sway, eye blink and pointer gaze, a subtle sneaker movement, quiet background shape drift, graph nodes float and status pulses, accessible cat reaction, interactive first-run sample/code editor. All CSS motion honours prefers-reduced-motion and pauses visually hidden graph particles; no flashy neon.
- Full V1-V5 source scanner, actual import graph, transitive impact, local-only guide, demo, JSON export and file navigation retained.
- 43/43 local Node tests. Real Chromium on small phone 360, iPhone 390, large phone 430, tablet 768, laptop 1024 and desktop 1536 confirmed 2 Ari SVGs + separate cat, 0 hero/card raster cutouts, all graph nodes tappable, selection navigates correct real file, cat gives tip, Ari guide opens, 3-step demo plays and advances, 0 browser errors or external requests and 0 horizontal overflow. Additional normal-motion browser verified 2 CSS-offset traveller dots on real graph edges and animation-safe screenshots; reduced-motion disables hair animation. axe automated WCAG A/AA six home/results/guide states 0 violations (manual expert checks pending).

Founder-banked V2, V3, V4 and V5 remain unchanged. PR stays unmerged pending independent review, legal name clearance and user approval of final art direction.
