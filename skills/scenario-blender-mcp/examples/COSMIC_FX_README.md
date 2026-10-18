# Pryntor Studios | Nebulapunk Free local intake + original cosmic FX R0

This is **a guarded pilot in the existing Blender stack**, tracked in [PRY-184](https://linear.app/pryntor/issue/PRY-184) and [PRY-330](https://linear.app/pryntor/issue/PRY-330). Do not create new departments, projects or other repos.

## Reality check

- The publisher offers a **$0 Nebulapunk Free Light Nebula Construct** for Blender 5.0–5.2 at https://superhivemarket.com/products/nebulapunk .
- **We have not acquired the publisher asset.** No Nebulapunk shader, node group, file or code is copied into the public repository.
- The code here can generate an **original native Blender procedural cosmic preview** without any vendor asset, API calls or approved spend.
- The optional vendor-import route is *implemented in source but has not been run on the licensed Nebulapunk Free file*. It needs a private, local, owner-acquired .blend, exact collection name, SHA256 and human-review record. If the supplied free package has a different file format, **STOP** and adapt after inspecting it, do not fake a successful import.
- The supplied original preview is not the same as Nebulapunk's proprietary raymarching shader and must not be described as such.

## Native R0 render (no proprietary assets)

```bash
blender -b --disable-autoexec -t 2 --python skills/scenario-blender-mcp/examples/cosmic_fx_pilot.py -- --outdir output --size 384 --samples 8
python skills/scenario-blender-mcp/examples/verify_cosmic.py --root output --size 384
```

Outputs: real Blender scene `cosmic_fx_study.blend`, rendered PNG `cosmic_fx_study.png`, hashed `cosmic_fx_evidence.json`. A new PR-triggered GitHub Action downloads pinned Blender 5.0.1, performs a render and independently verifies the artifact in another runner. The authoring container cannot run Blender natively, so wait for CI evidence before claiming a functioning preview.

## Optional authorised vendor import, when acquired

1. From a company-controlled account, claim the **$0** edition on the official website, only if no spend, renewal or unknown terms arise. Keep source, licence and invoice/claim evidence privately.
2. Review exact licence for internal production use and any commercial distribution limitations. Inspect package offline and record the exact .blend and actual collection identifier. Do not upload proprietary vendor file into GitHub or a public runner. Disable Blender autoexec.
3. Create private local `approval.json` with `product: "Nebulapunk Free"`, `source: "https://superhivemarket.com/products/nebulapunk"`, `cost_usd: 0`, `approved_for_internal_test: true`, `commercial_use_review: "internal-only"` (or independently `"cleared"`), `owner_reviewer` and exact `sha256`.
4. On the authorised Blender host:

```bash
blender -b --disable-autoexec -t 2 --python skills/scenario-blender-mcp/examples/cosmic_fx_pilot.py -- \
  --outdir private-output --size 384 --samples 8 \
  --vendor-file /private/nebulapunk-free.blend \
  --vendor-receipt /private/approval.json \
  --vendor-sha256 REAL_64_HEX_SHA256 \
  --vendor-collection 'COLLECTION_NAME_FROM_VENDOR_FILE'
```

The asset stays local. Missing rights, wrong product, SHA mismatch, unapproved spend or unknown collection causes a hard failure. The asset is appended only by exact known collection name, and may still require manual spatial/material adjustments after visual inspection.

## Not yet done

Official free-edition claim, asset and node/collection inspection, official vendor render, GPU performance comparison, human art direction, license review, ZOWIBO mobile integration, AFTERLIGHT compositing, and release approval are all **pending**. The native CI render, if it succeeds, does **not** prove the Nebulapunk edition works. Nothing is merged or production-released without independent review.

No client assets, trademarks, secrets, vendor source distribution or unapproved spending.
