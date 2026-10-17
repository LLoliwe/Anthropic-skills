# CURRENT POLICY (17 OCT 2026): AUTOMATED FORUM ACCESS DISABLED

The published forum Terms of Service, https://labautomation.io/tos, section Acceptable Use paragraph 5, explicitly prohibits automated access/monitoring except a public-search-engine indexing exception. Public JSON response success does NOT convey permission. The historical example `public_forum.py` now fails closed before network access unless written operator permission has been obtained *and* the local `LABAUTOMATION_FORUM_WRITTEN_PERMISSION=YES` gate is deliberately activated. It is **NOT** run by GitHub Actions. Do not use credentials or automate the forum based on this note.

**Active implementation (after merge):** `github_oss_radar.py`, `test_github_oss_radar.py`, and the scoped `lab-oss-radar.yml` workflow use *GitHub public repository metadata* only. On merge to default branch, GitHub will attempt a weekly scheduled scan each Monday near 08:17 SAST and store a short-lived artifact. PR runs execute offline tests only. A successful GitHub-hosted run and permission/security review must precede 'production-ready' language. No forum scraping, private messages or posts.

# Lab Automation Forums — free/OSS opportunity register (2026-10-17)

**Status:** original research notes only. NOT an installation, deployment, independent QA, or endorsement.  
**Canonical record:** [Pryntor Google Doc](https://docs.google.com/document/d/1DFmu7OX8C_isSZDvtbKGcdxHHVNxMw3TL6tRjW_bPbk/edit)  
**Tracking:** [PRY-231](https://linear.app/pryntor/issue/PRY-231/lab-auto-001-free-lab-automation-oss-intake-no-hardware-evidence-pilot)  
**Spend:** R0 new, no physical instruments. The screenshot proves account-confirmation UI only, not authenticated forum access for Pryntor agents.

## Source catalogue

| Project | Source | License evidence as of 2026-10-17 | Proposed use | Gate |
|---|---|---|---|---|
| PyLabRobot | https://github.com/PyLabRobot/pylabrobot | MIT; upstream LICENSE checked | Mock/no-hardware liquid-handler simulation and task abstraction | Pin commit, isolated install, security review |
| MADSci | https://github.com/AD-SDL/MADSci | MIT; upstream LICENSE checked | Experiment workflow, resource tracking and observability | Beta upstream; mock-node evaluation only |
| BayBE | https://github.com/emdgroup/baybe | Apache-2.0 | Offline bounded design-of-experiments pilot | Compare held-out synthetic objective to random baseline |
| Poseidon | https://github.com/pachterlab/poseidon | BSD-2-Clause | Read CAD, controller, BOM and assembly ideas | No physical fluid handling/safety claims |
| OpenLIMS | https://github.com/Mokey2002/OpenLIMS | Apache-2.0; upstream LICENSE checked | Laboratory record and audit-logging design reference | Not regulated-production validated |
| Argonne WEI | https://github.com/AD-SDL/wei | MIT; upstream LICENSE checked | Workflows comparison | Check maintenance, dependencies |
| Opentrons | https://github.com/Opentrons/opentrons | Apache-2.0 root LICENSE checked | Open robot API study | Subpackages, hardware licences separate |
| Plateo | https://github.com/Edinburgh-Genome-Foundry/Plateo | MIT; upstream LICENSE checked | Labware data modeling, picklists and reports | Dependency and API audit |
| Orca (new) | https://github.com/Cheshire-Labs/orca | **SSPL-1.0, source-available**, not standard OSS; versions <=1.0.0 AGPL-3.0 | Architecture study only | Legal/security HOLD; local daemon unauthenticated, installs PyLabRobot fork |
| OpenDrop | https://github.com/GaudiLabs/OpenDrop | Unverified | Digital microfluidics designs | License/HW review before any reuse |
| Platechain | https://labautomation.io/t/platechain-from-sphinx-bio-llm-ai/2394 | Unverified | AI workflow ideas | No code assumption |
| Industrial USB-C camera | https://labautomation.io/t/opensource-usb-c-industrial-camera/861 | Unverified | Machine vision references | No dependency on unverified hardware |
| OpenFlexure / pyuscope | https://labautomation.io/t/opensource-pyuscope-controlling-opensource-openflexure-scopes-at-supercon/2399 | Unverified here | Microscopy educational design | Verify actual source+license |
| Opentrons REST extension | https://labautomation.io/t/open-source-rest-api/2369 | Unverified current maintenance/licence | Command orchestration reading | Treat forum-era GitHub link as historic |

## Free learning/community entry points

- https://labautomation.io/c/open-source/12
- https://labautomation.io/c/diy/24
- https://labautomation.io/c/schedulers/22
- https://labautomation.io/c/robotic-arms/21
- https://labautomation.io/c/3d-printing/5
- https://labautomation.io/t/low-cost-automation-engineering-resources/5099
- https://labautomation.io/t/primer-guide-to-everything-robotic-microscopy-open-to-feedback/3702
- https://github.com/topics/lab-automation (DISCOVERY ONLY; not a vetted list)

## First safe pilot

1. No network/hardware/credentials. Read exact upstream commit and its transitive licenses; prepare isolated venv.
2. Choose **one** of PyLabRobot no-hardware visualization or MADSci mock-node execution.
3. Freeze a synthetic ten-fixture corpus with explicit expected outputs, safety and non-claims.
4. Log actual test commands, stdout/stderr, artefact hashes, failures and untested coverage.
5. Independently review before promotion; no green status without real tests.
6. Optionally benchmark BayBE against pre-registered random-search baseline with held-out repetitions; no self-selected best-case metrics.

No agent should import or launch these projects automatically. Do not conflate a robotics lab prototype with Pryntor's outstanding MuJoCo 10ms delay failure (historical 0/5). No cash/customer claim.

## Legal/quality notes

The forum is public community content, not a blanket software/data licence. Attribution and creator links are required. Treat Onshape/Rider free plans as potentially restricted to noncommercial use unless current terms are checked. Current Orca has an unauthenticated local daemon and a PyLabRobot fork; do not expose it on the internet or co-install it with upstream PyLabRobot. No legal, safety or independent testing approval is implied.

## Alternative connection: public Discourse feed, no TinyFish login (implemented 17 October 2026)

**Verified by a live public API read (not an authenticated user session):**

- `https://labautomation.io/categories.json` — returned category metadata.
- `https://labautomation.io/latest.json` — returned topic metadata including current activity.
- `https://labautomation.io/c/open-source/12.json` — returned public Open-Source category topics.
- `https://labautomation.io/latest.rss` — returned RSS XML.

Discourse describes public JSON endpoints: https://docs.discourse.org/ . Public access may change; respect site terms, rate limiting and source attribution.

**Read-only CLI code:** [public_forum.py](./public_forum.py) (Python standard library; no dependencies, no API key, no cookies, no POSTs). Fetches at most two allowed endpoints once per invocation, times out after 15 seconds each, limits response size and refuses redirects outside the forum. Outputs attributed topic metadata only, not personal profiles, post bodies or private messages.

```bash
python3 research/labautomation/public_forum.py --category open-source --limit 10 --format markdown
python3 research/labautomation/public_forum.py --keyword robot --limit 12 --format json
cd research/labautomation && python3 -m unittest -v test_public_forum.py
```

**Validation scope:** original equivalent CLI and its offline suite passed 12/12 local unit tests on 2026-10-17; production/scheduled runtime and GitHub-hosted CI are NOT certified by that. Live API endpoints were read separately in the assistant's read-only fetch tool. The committed adapter has not been proven to run from a GitHub Actions runner. This is a company reference integration, **not** a logged-in ChatGPT connector, agent installation, forum posting permission or autonomous continuous sync. Never upload forum session cookies or API keys into code/PRs.
