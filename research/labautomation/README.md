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
