# Pryntor Launch Desk R3 — Adobe Fonts × motion design

17 October 2026. Applies to the real Void/Node app at https://pryntor-launch-desk.onrender.com, not a static design mockup.

## Adobe work performed
- Adobe Creative Cloud searched for existing Pryntor assets; existing brand-lock folder was found but contains Tirisano evidence and is **not** a source of approved Pryntor artwork.
- Adobe Fonts recommendation/catalog searched. A real published Adobe Fonts **web kit `zss4psu`** was created specifically for `pryntor-launch-desk.onrender.com` and `localhost`.
- Licensed web-embed family data returned by Adobe: **Neue Haas Grotesk Display** (600, 900) and **Adobe Caslon Pro** (italic 400). Embedded via Adobe's own https://use.typekit.net/zss4psu.css stylesheet; never distribute or commit font binaries. CSS uses explicit system fallbacks so expired Adobe access does not break the product.
- Adobe Express animation attempt of an existing creative exploration did **not return a confirmed outcome**. Do not claim its output was created, licensed, or inserted into the deployed site.

## Motion that actually ships
- CSS-painted original geometric hero, slow orbit of concentric rings, subtle sculptural drift and tiny depth motes. No video streaming, stock art, WebGL, MP4 or proprietary runtime.
- Editorial intro sequencing for type, targeted scroll reveal via IntersectionObserver, question-state entrance and score-state emphasis. Pointer parallax limited to fine/hover input and requestAnimationFrame; no parallax on coarse touch.
- Accessible **Pause / Play animation** control, persisted as `pryntor.motion.paused.v1` in the same browser; native `prefers-reduced-motion` wins, disables all motion even when the toggle was previously enabled.
- Animation is presentation only; the underlying six release gates, evidence notes, browser-local save, JSON export and API behavior remain unchanged.
- No background polling, autoplay audio, tracking, analytics, new Cloudflare infrastructure, customer data or new hosting service.

## Privacy and font-service limitations
Adobe-hosted fonts request content from the Adobe CDN and therefore expose network metadata such as visitors' IP addresses to Adobe. This is **explicitly disclosed in the on-page copy**, not marketed as an all-local/no-third-party site. Review applicable privacy notice before advertising a business product. Content users type in release notes stays in localStorage on their browser and is not sent to Pryntor or Adobe by this application.

The fonts kit depends on the caller's current Adobe Fonts web embedding entitlement; if a trial is cancelled or expires, the font rendering may revert to system fonts. This must not alter functionality. It does **not** mean a new subscription was purchased or authorized. If account access lapses, disable the kit after checking usage and keep design fallbacks.

## Release QA and performance
- Node24 pinned, `npm ci`, production Void SSR build, real dev and compiled-server HTTP smoke, static Adobe/motion contract test.
- Browser QA on target responsive widths 360/390/768/1440, zero horizontal overflow, manual motion toggle, reduced-motion rendering, no console exceptions, no failed critical requests. Verify fallback with Adobe Fonts blocked in browser.
- Check CSS external font CSS loads with Content-Security-Policy: `style-src` limited to own inline + `use.typekit.net` and `p.typekit.net`; `font-src` allows `use.typekit.net`; no Adobe scripts.
- Keep animations transform/opacity-driven and especially economical on iPhone. Avoid long page-blocking transitions and never block click/touch/scroll.
- Same **Render Free** service, `autoDeploy=no`; deploy manually only after PR latest-head CI & browser tests.
- **Commercial prod sign-off remains HOLD** pending independent expert assessment, five moderate npm advisories, monitoring and tested rollback in PRY-233.

Reference production design radar: [DESIGN_RADAR_R2.md](./DESIGN_RADAR_R2.md).
