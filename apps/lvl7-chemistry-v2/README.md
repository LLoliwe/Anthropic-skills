# LVL7 Chemistry Club V2 — Internal review candidate

A wholly original educational game expansion adjacent to the approved LVL7 Water V1/V1.1. This directory is additive and **does not modify** Water V1, Water V1.1, approved R4 visuals, or any live learner system.

## Real navigation and worlds

Hash-routed separate views: Home, Chemistry Trail, five self-contained worlds, Collection, My Progress. Functional iPhone bottom navigation and desktop sidebar. Worlds: Matter Lab (idealised water energy), Atom Forge (isotopes and ions), Reaction Room (atom-conserving balanced chemical equations), Bond Bench (simplest charge-neutral ionic ratios), Element Sprint (periodic-family identification).

Each world contains **five successive challenges**, for 25 deterministic levels total. All worlds are discoverable immediately, but level N+1 unlocks only after level N in that world. Three-heart perfect-solve track, hints, attempt-sensitive 1–3 stars, earned XP (not fake counts), offline local progress, profile reset; accessible keyboard/aria labels and reduced-motion CSS. No ads, purchases, accounts, external network API calls, child identifiers, analytics, telemetry or server-side storage.

## Scientific constraints

- Matter at 1 atm is an idealised educational water heat-energy model, **not** fluid computational dynamics. q = m × 4.18 J/g°C × (100 − initial) / 1000 + mass × 2.256 kJ/g × vapour fraction. Meter feedback shows computed temperature and vapour fraction. Source V1.1 fluid simulator remains accessible by explicit link, not silently replaced.
- Isotope: proton count = atomic number; neutrons = mass number − atomic number; electrons = atomic number − ionic charge.
- Reaction checker validates both sides' **element atom counts** using formula parsing including parenthesized groups, and rejects non-primitive proportional coefficient sets.
- Ionic compounds: total electric charge must equal zero and the cation/anion ratio must be in lowest whole numbers.
- Periodic-family classifications are explicitly authored and testable.

## Gate

This is a playable synthetic/local review build. Chemistry correctness checks should be independently teacher-reviewed against age appropriate curriculum; mobile Safari and screen reader verification, child-safety review and founder UI acceptance remain necessary. Do not claim this merged source equals a live product or publish it as learner-ready.

## Local review

Open `index.html` in a browser, or serve directory on a free local static server (`python3 -m http.server 8000` from the directory). With any installed Chromium, run `python tests/qa.py`. Test has no paid dependencies other than already installed Playwright and Chromium.