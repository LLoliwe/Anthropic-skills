# RED HOUR / OBJECT 01 — Pryntor Studios R1 cinematic commercial gallery

This is an **original fictional architectural and product CGI environment**, not a real client campaign. Native Blender 5.0.1, authored procedural mesh, in-engine textures/lighting and perspective camera movement. No external stock textures or AI-video model calls. Files form a technical *candidate*, not a commercially cleared/artistically accepted creative.

## Creative brief
One architecture-led RED HOUR luxury lighting-object gallery: a monumental oxblood arched recess, light-filled plaster/travertine hall, layered bronze jewellery-detail, double-orbit sculptural luminaire, authentic scene depth and a restrained right-to-left dolly. Own authorship: original shapes and typography, fictional product.

## Reproduction

```bash
blender -b -t 2 --python red_hour_gallery.py -- --outdir output --mode still --width 960 --samples 24
python -m pip install pillow
python verify_gallery.py --output output --width 960
# After viewing and approving stills, render the real animated 3D camera movement:
blender -b -t 2 --python red_hour_gallery.py -- --outdir output --mode video --width 640 --samples 8
ffmpeg -framerate 16 -i output/motion_%03d.png -c:v libx264 -pix_fmt yuv420p -crf 18 output/red_hour_camera_test.mp4
```

For no-charge public GitHub Actions, a pinned SHA-256 official Blender 5.0.1 binary is downloaded and its checksum validated. The public CI workflow renders three source-grounded stills, checks hashes/decode/visual variation twice on independent jobs, then exports retained artifacts. `video` mode is not called automatically to conserve resources. An actual movie must be exported and QA'd separately, not approximated with a pan/zoom slideshow.

## Required release gates
- **Tech:** CI source + genuine Blender render + fresh-runner independent decode and editable .blend verification.
- **Image review:** human reviews 3 full-resolution frames for material realism, lighting, architecture, proportions, typography, and composition, with founder veto.
- **Temporal:** only then run all continuous frames and inspect camera/motion/geometry continuity, no hidden cut.
- **Rights:** source provenance, typography, licenses, logo and client approvals.
- **Commercial:** actual buyer willingness to pay and approved rate card; cannot call this "commercial ready" solely because output opens.
- **Provider bridge:** generative video conditioning via first/last frame, camera/depth etc only with capability, rights and *zero new money* verified; do not claim model connection if not actually executed.

## Downstream hold
No ZOWIBO children content, BTWW video, AFTERLIGHT, Tirisano or game rollouts until Studios proves R1 quality and animation motion. Future creative adaptations must be wholly new and age/safety/brand appropriate; no shared unlicensed assets or vendor inference assumptions.
