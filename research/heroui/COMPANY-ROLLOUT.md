# Company applicability and rollout — HeroUI free (17 Oct 2026)

Status terms: SHARED SKILL DRAFT = instructions stored in PR; PILOT BUILT = compiled and browser-tested only after verified CI; PRODUCT INSTALLED = dependency + end-to-end tests verified in actual product repository; HOLD = absent fit or authorization. No venture is auto-installed by adopting this standard.

| Product/operating area | Real verified technical surface | Free HeroUI next action | Current evidence state |
| --- | --- | --- | --- |
| Pryntor Core Mission Control | Lovable unpublished app, React compatibility not yet proven; 5 unit failures and 16 lint failures at latest checkpoint | Resolve baseline; inspect exact dependency versions then isolated optional component | HOLD |
| Pryntor Web Studios | Shared source repo and static company site; owner mapping incomplete | Use isolated free React sandbox, design per brand; integrate only into eligible future project | SHARED SKILL DRAFT |
| LVL7 | Original HTML/CSS/JS interactive water v1, no verified React frontend | Do not rewrite accepted working water; teacher portal React proof later | HOLD |
| Show Your Working | Vercel proof projects, linked source and React stack unverified | Preserve grading/model and educator governance; prospective teacher console only | HOLD |
| Tirisano Travel | WordPress site not mapped to authorized writable source | No WordPress overwrite; evaluate future portal only | HOLD |
| BTWW / Studios | No authenticated React site identified | Admin/booking tools may benefit; preserve distinctive editorial identity | HOLD |
| Pryntor Robotics | Simulation and synthetic HTML/JS validation labs | No runtime/safety UI refactor, dashboards only when viable repo exists | HOLD |
| Pryntor Mobile | Native iOS/Android architecture and device QA unverified | React web package NOT native UI integration; separate native licensing/stack review | HOLD |
| Pryntor Kids & Games | Browser-based original mini-game source; interaction/game renderer separate | Avoid forced generic UI library and child data | NOT APPLICABLE |

Verified first pilot: `examples/heroui-free-pilot/` is designed to install actual `@heroui/react` and `@heroui/styles` with interaction checks in an isolated build. CI evidence must be inspected before changing status.

Legal: repository root Apache 2.0; inspected v3.2.6 package manifests MIT; must comply with package/source/tran­sitive licenses, and **no HeroUI Pro**. No claimed free Pro licenses or acquired marketplace accounts. No new spend.

Completion means 1) published exact installed artifact & CI log, 2) independently inspected live app on real target, 3) owner signoff and 4) every applicable product checked and recorded individually. Until then record **not deployed**.

Linear: https://linear.app/pryntor/issue/PRY-273
