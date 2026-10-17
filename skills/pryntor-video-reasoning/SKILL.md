---
name: pryntor-video-reasoning
description: Pryntor-wide offline video evidence intake and timestamp-grounded reasoning protocol. Use when analysing submitted videos, motion, editing, continuity, screen content or audiovisual references while keeping third-party uploads disabled.
---

**Version:** 0.1.1 · **Scope:** Offline intake released; model video reasoning remains a restricted pilot (not production-verified).
# Pryntor Video Reasoning — company-wide skill

## Trigger
Invoke when the founder or a permitted team member provides a video, video reference or a question whose answer depends on event order, object motion, shot changes, causal interpretation, editing, or on-screen details.

## Protocol
1. Identify the exact submitted source, authorized purpose, owner, sharing rights and privacy tier; do not assume prior conversation uploads are locally present. Keep sensitive videos local and restrict access by venture. Do not copy a person's likeness, content, music or brand assets based on a reference.
2. Run deterministic local intake: `python video_intake.py intake /path/video.mp4 --out /private/work/output --owner 'Approved owner' --rights reference-only --privacy restricted --frames`. It uses ffprobe and optional OpenCV. Default: **zero third-party upload**. Review contact frames on local system and original clip for timing, audio, and context.
3. Describe a **timeline of visible events** with timestamps and direct frame/interval references; explicitly distinguish what is visible (OBSERVED) from inferred intent, physical forces, identity and reasons (HYPOTHESIS). Without video/frame access, report only technical metadata and abstain from scene descriptions. Screenshots of videos do not establish whole-video motion.
4. For motion or continuity assertions, replay surrounding intervals at denser frame intervals; track object identifiers through cuts and occlusions. Validate event direction and ordering. Compare footage with a static-frame-only baseline; contradictory evidence requires correcting or retracting the claim.
5. For physics questions, specify observed path, perspective, frame rate and potential edits. Qualitative mechanics are hypotheses unless measured physical signals/simulation establish them. **Never claim safety validation from visual appearance alone.**
6. Create separate records for observations, hypotheses, alternative explanations, uncertain or missing frames, rights, and reviewer disposition. Validate structural JSON with `python video_intake.py validate evidence.json`. Passing structural validation is NOT passing factual human review.
7. Produce one venture-specific actionable conclusion with a source-to-lesson link: original visual/camera/sound technique for Studios+BTWW, content authenticity for Tirisano, product CTA/compliance for commerce, educational method checks for LVL7, or experiment/sensor hypotheses for Robotics. Keep data minimized.
8. Sign-off: a human domain owner checks important claims, licensing, consent and safety. Do not mark a production release green until independent verification. Follow zero-new-spend-first.

## External model comparison
Elorian Glimpse: announced 16 Oct 2026, official https://elorian.ai/blog/introducing-glimpse . Vendor benchmark results are not independently validated; prior account access does not establish API entitlement, free quota or acceptable privacy conditions. Do not upload customer, student, unreleased or restricted footage before scoped authorization and review of data handling. Compare with an available model using the same ten rights-cleared clips, timestamps, temporal order and false-confident-claim rubric. No fixed vendor lock-in.

## Output fields
`source.sha256`, `source.owner`, `source.rights`, `source.privacy_tier`, `technical_metadata`, `sampling.frames`, `observations[] {kind:'observed', claim, time_seconds, evidence_frames}`, `hypotheses[] {kind:'hypothesis', claim, limitations}`, `human_review.status`.

## Linked workflows
- Linear: PRY-222. Related PRY-177 HyperFrames, PRY-191 Motion Director, PRY-195 Earshot, PRY-190 Visual Radar, PRY-122 LVL7.
- No automatic external sync, model calls, production installation or backfill of historic videos occurs just because this skill exists.
