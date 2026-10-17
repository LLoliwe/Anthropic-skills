---
name: pryntor-heroui-free
description: Pryntor Group's optional, rights-safe HeroUI v3 FREE adoption skill for eligible React or HTML visual workflows. Only apply after stack verification and independent product QA.
---

# Pryntor HeroUI FREE — governed company-wide capability (PRY-273)

**Scope: applicable products only.** This shared skill allows Pryntor teams and agents to **evaluate and install free HeroUI** when a verified app needs React UI or isolated framework-agnostic styling. It is not a universal dependency or global visual brand. The skill's presence does **not** prove installation in any product.

## Upstream, version and rights

- Canonical upstream: https://github.com/heroui-inc/heroui pinned research reference `ce90ea3ab49d58f6c428f71bfd6fe8ae2a87b960` (v3 branch on 17 Oct 2026).
- Inspected package manifests: `@heroui/react@3.2.6` and `@heroui/styles@3.2.6`, both declare **MIT**. Repository root contains an **Apache-2.0** LICENSE. Verify NOTICE/package attribution and transitive dependencies in the exact installed release; do not conflate these scopes.
- Official open-source skill (read-only reference, not copied): https://github.com/heroui-inc/heroui/tree/v3/skills/heroui-react
- Official docs: https://heroui.com/en/docs/react/getting-started/quick-start
- **NOT PERMITTED under this free-first mandate:** HeroUI Pro premium components, licensed Pro Figma/templates, shared license credentials, paid purchases, bypassing paid restrictions or creating a resale of proprietary Pro components. Pro restrictions https://heroui.pro/terms

## Decision tree

1. Verify a real, writable repository and live product owner, current baseline test results and active brand master.
2. React 19+ AND Tailwind 4: optionally install exact free `@heroui/react@3.2.6 @heroui/styles@3.2.6` with necessary peers. Use no v2 HeroUIProvider; import Tailwind before HeroUI styles.
3. Non-React web: evaluate ONLY `@heroui/styles` with independent semantics, focus, keyboard and accessibility. It is not a React behavior library.
4. Existing legacy React 18, Tailwind 3, native mobile, games, pure backends, audio, film/video, hardware: **SKIP**, unless a separately justified migration or native suitability review is approved.
5. Never replace approved brand typography, color, art direction or licenses with a generic component theme.

## Release gate

For EACH accepted venture project collect: original art-direction delta, actual source path/commit, `npm ci` or reproducible install log, typecheck/build, working interaction and browser E2E, 360/390/768/1440 responsive screenshots, contrast and screen-reader spot check, reduced-motion/focus, accessibility evidence, security/supply chain inspection and explicit human approval. A playground pass is not a venture pass.

**PRY-218 Mission Control currently has known failing tests/lint. Do not land HeroUI in that working tree until the baseline is repaired.** No touch to runtime secrets, authentications, payment or private data. R0 incremental spend and no public deployment without approval.

## Venture fit map

- Core / Mission Control: conditional React fit; blocked by current baseline issues.
- Web Studios: reusable component patterns and source-safe client templates; only actual React projects.
- LVL7 / Show Your Working: teacher workflows after independent educator and child-safety review, never scoring logic replacement.
- Tirisano: WordPress/Gutenberg site is not a React rewrite; only prospective React TMC portal if approved.
- BTWW / Studios: selectively admin and booking/editorial tools, not replacement of custom music/film identity.
- Robotics: internal dashboards only; measured provenance and safety stays independent.
- Kids / Games / Mobile: generally NOT APPLICABLE to interactive gameplay or native apps; evaluate native components under separate licenses and device tests.

## First working pilot

Source is `examples/heroui-free-pilot/` on a draft branch. It is a synthetic interaction laboratory, not any released Pryntor service. Open its `README.md`, inspect build/CI results, then use the result as a *pattern*, not a forced runtime dependency.

Evidence register: https://linear.app/pryntor/issue/PRY-273
Design authority: https://docs.google.com/document/d/1As0hfHqrsXxcO9D_tHnEjVMGEu-EqspcBQjYJNrSBvE/edit
