# LVL7 EXPLAINER LAB / PHY-01 — ideal Hookean spring

Original Pryntor SVG/isometric educational web prototype. This is a **designed demonstration that complements the Anatomy workflow**, not a claim that its geometry was produced by Anatomy `iso-kit` (see official upstream). It implements a deterministic pure equilibrium model, rendered mechanical animation and accessible browser controls. No external libraries, paid APIs, tracker, learner data or runtime GPU service.

## Proof

- `node --test tests/model.test.mjs` checks F=mg and F=kx over every selectable mass.
- `python -m http.server 8765 -d examples/lvl7-spring-lab` from the repository root; open `http://127.0.0.1:8765/`.
- Browser QA: readout/indicator synchronization, dark/light, arrow-key adjustment, ±100g buttons, reset, reduced-motion suppression, 390px mobile overflow, `prefers-reduced-motion` and contrast/readability.

At rest, vertical spring displacement `x=mg/k` with `g=9.81 m/s²`, `k=400 N/m`, mass 0–2000g. Pixel mapping is schematic and intentionally **not to physical scale**. This is a pedagogical simulation, not an experimentally calibrated apparatus; it does not validate material yield, actual spring behavior or classroom alignment without a teacher's review.

Roadmap: educator QA of explanatory language, semantic slider screen reader evaluation, source-pin security review, then any public release under product approval. Do not publish to Anatomy community gallery without separate approval.