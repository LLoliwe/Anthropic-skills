---
name: scenario-blender-mcp
description: Evaluate and adopt the official Scenario Blender extension and its local MCP tools for original 3D work, with explicit security, rights, cost-approval and render-verification gates. Use when a user wants Blender 3D asset workflows or a Scenario MCP integration.
---

# Scenario Blender MCP — guarded pilot skill

**Status:** documentation + nonbilling procedural example only. Not installed or validated against a live Scenario account. This is an independent workflow guide, **not** an official Scenario skill.

## Canonical upstream

- Extension: https://github.com/scenario-labs/blender-plugin
- Local MCP: https://github.com/scenario-labs/blender-plugin/blob/main/docs/MCP.md
- Known limitations: https://github.com/scenario-labs/blender-plugin/blob/main/docs/KNOWN_LIMITATIONS.md
- Licence of upstream extension: GPL-3.0-or-later; review obligations before distributing derivatives. This skill is original text, not a copy of extension code.

## Rules before touching a real scene

1. Verify persistent host, actual Blender version (>=5.0), installed extension version, official release provenance and the operator's authorization.
2. Keep **Scenario API keys, secrets and local MCP bearer tokens** in a secrets vault. Never print them or add them to repositories, logs, screenshots or generated assets.
3. The local MCP URL is commonly `http://127.0.0.1:9876/mcp` but must be copied from **Scenario > Agents (MCP)** on the Blender host. Loopback on a remote computer is not the user's local Blender. Never expose MCP or arbitrary Python execution to the public internet.
4. **Zero new spend by default.** Free extension code does not grant free inference. Obtain an exact quote, eligible commercial-use terms, available balance, a per-job cap and explicit operator approval before any model generation or hosted compute. Tool descriptions alone do not enforce payment approval.
5. Treat Scene/mesh/camera inspection and native Blender procedural rendering as distinct from paid Scenario generation. Start with a nonbilling procedural sample: `examples/hero_still.py`.
6. Capture reproducible `.blend` file, render dimensions, time, Blender version, scene inputs, SHA-256 output, editable source and independent visual QA. Never call a static/source check a rendered demo.
7. Verify product images, third-party model weights, textures, fonts and generated outputs are licensed for the actual commercial use. Never upload client assets to public demos without written consent.
8. The Scenario extension is experimental. Check documented limitations and test the exact OS/Blender version/provider lane before promising production delivery.
9. Record durable job status and reconcile uncertain submissions before retrying; never automatically resubmit a potentially charged generation.
10. Do not claim an integration is installed, a render passed, a product was sold or any revenue collected without evidence.

## Safe native Blender baseline

```bash
blender --version
blender --background --python examples/hero_still.py -- --outdir ./output
```

This creates an original fictional product-like shape and a still using native Blender only. It does not invoke Scenario, Hugging Face, a GPU service or an API. It has not been run in a Blender runtime in this repository.

## Agent test gate

- Read-only local MCP discovery on the correct host, without exposing credentials.
- Quote one representative action without submitting; confirm units and user approval workflow.
- Submit only after explicit approval and commercial-use rights check.
- Validate final outputs, costs, scene integrity, render and rights ledger independently.
- If any gate is unknown, mark **BLOCKED** and return a concrete evidence request.

## Hugging Face alternatives

Do not confuse a public model or Space with a production-ready, commercially licensed, private inference environment. For any model/Space, verify its exact model-card licence, dependencies, security of uploads, hardware needs, commercial rights, and real pricing. Never silently launch a paid HF Job.

## Revenue discipline

For product-visual work, validate one repeatable small deliverable before building a full autonomous 3D department. Track actual labour time, revisions, direct generation/hosting costs, customer approval, invoicing and settled cash separately. Modelled margins are not earnings.
