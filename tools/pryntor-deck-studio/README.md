# Pryntor premium deck stack

Three MIT licensed sources are verified at fixed upstream commits and can be installed selectively into a writable local working copy using:

    python3 tools/pryntor-deck-studio/install.py --dest .
    python3 -m unittest discover -s tools/pryntor-deck-studio -p 'test_*.py' -v

Installs to skills/_external, .agents/skills and .claude/skills, with SKILL.md and MIT license notices, after source validation. Does not execute downloaded scripts, install dependencies, modify a user's global environment, grant model/tool entitlements, or prove live persistent Claude/Codex installations. Restart clients as applicable and confirm capabilities.

Frontend Slides: 9906a34d640d2111f724544cbc50f7f130569ae1.
Baoyu Slide Deck: 1567581c26ec29f4216c6e6835415bf30343b0e3.
Knowledge Cat: 889c3dc00b356607fa9af935eb807056c3394886.

Figma official guidance is an external link only. Anthropic PPTX has a restrictive proprietary license, so may not be copied into Pryntor: use within authorized Anthropic services under their agreement. Any future image generation, live publishing, child data collection or paid API use requires separate approval. Existing ZOWIBO artwork is preserved as the founder's visual reference; earlier alternative directions were rejected.
