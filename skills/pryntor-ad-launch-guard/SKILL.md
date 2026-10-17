---
name: pryntor-ad-launch-guard
description: Offline fail-closed synthetic launch manifest preflight for Pryntor paid-media workflows before Blip/Meta vendor credentials or any ad publishing.
---

# Pryntor Ad Launch Guard (R1)

Original offline Python 3 standard-library skill and tests for synthetic ad launch metadata. Not Withblip MCP; not a Meta API client; no execution authority to launch or spend. Expected status PASS_OFFLINE_ONLY, never a production greenlight.

From this folder: python3 -m unittest discover -s tests -v ; python3 scripts/validate_manifest.py examples/synthetic.json ; python3 scripts/validate_manifest.py examples/rejected.json (must FAIL).

Reject unexpected fields, real ad account IDs, publish/live or nonzero budget, unapproved creative, unsafe media paths, missing UTMs, unauthorized enhancements and invalid URLs. Synthetic test_ account IDs only. All real Meta accounts, placement/pixel/catalog state, ad ownership, privacy permissions, campaigns and independent QA require external authenticated verification. Do not upload customer records, third-party employer data or credentials to tool inputs. Actual spend and vendor terms require separate approved evidence, even when this validator passes.

Owner: EVP Growth & Revenue + security gate; only relevant Pryntor ventures opt-in. Company runbook: https://docs.google.com/document/d/11WcMhEQWG5tFOpMEzdXforCnX55IskryPmLrXFeiPaQ/edit ; Linear: https://linear.app/pryntor/issue/PRY-212 .
