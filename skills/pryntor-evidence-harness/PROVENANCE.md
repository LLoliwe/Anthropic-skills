# Provenance and optional suppliers

- Pryntor harness, fixtures and tests: original prototype, Python standard library, no upstream source copied.
- Graphify official CLI: https://github.com/Graphify-Labs/graphify , Apache-2.0; installable name `graphifyy`, executable `graphify`. Local source parsing and hosted SaaS have different data-boundary implications. No Graphify binary was installed or invoked in this R0 package.
- Graphify hosted free tier: https://graphify.com/pricing . No paid plan, trial card or repo connection was authorized or activated here.
- Jev TypeSafe decision model: https://typesafe.ai/ (verify live product terms and privacy contract). The architecture is inspired by https://github.com/Archive228/jev-harness-engineering , but no upstream source was copied. No Jev calls or billing are active.
- REA is for binaries and packages, not an automatic substitute for source-code Graphify mapping. Prior company REA skill remains separately governed.

Install any third-party component only on a specific, reviewed version. Verify license, hash, dependencies, network behavior and target-data rights first. Do not treat links or package names as proof of installation.

## Reviewed Graphify candidate (not yet production installed)

Official published candidate: graphifyy 0.9.92, released 16 Oct 2026 from Graphify-Labs/graphify commit 86c57be8204673c2a1b9849a3292a7dd3ab373d8. PyPI attested wheel sha256: `9722846e627a369150107dd792145c3e3a53e3d3da46f7a7bff9f96b75da857c`. Source license Apache-2.0. The optional code-only CLI path is `graphify extract . --code-only`, `graphify cluster-only . --no-label`, `graphify export html`. This is a candidate pin, not a full transitive dependency audit.