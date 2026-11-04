---
id: PW-1281
title: "Village experiment: tracked villages vs last-200-years only vs generated on demand"
type: task
status: wontdo
parent: null
milestone: v3
subsystem: culture
effort: s
impact: med
found_by: coordinator
blocked_by: []
relates: []
refs: [planet/lineages/polities.py::_confederations, planet/lineages/polities.py::_site_tables, "run 3c1caf", "run a2b637", docs/review/culture/polities/round5.md]
created: 2026-11-01
updated: 2026-11-04
---

## Description
**In plain words.** Daniel worries tracking every village on the 100-year step is too granular. Test three arms on one L6 world (then one L7): A villages tracked throughout; B villages only in the last 200 years; C as B plus villages generated on demand from town data. Measure towns and cities (counts, sizes, founding steps), culture sizes and minorities in the ledger, polity seeds, generated vs tracked villages, and ledger size and wall time. Pass if B and C stay within the run-to-run noise of a re-seeded A. Design: docs/review/cultures-proposal/proposal-r2.md section 2.3. Needs Daniel's go (open decision O3).

## Updates
- 2026-11-04: Status todo -> wontdo. Lane 180: closed with evidence, not run. Cost was the worry, and it does not bite: the ledger takes 25 s of a 1,534 s L7 run on 3c1caf (21 of 1,117 on a2b637) and 47 MB. And polities now need the villages every century: on 3c1caf villages hold 82% of settled people 1,000 years ago (68% at 5,000), and they are the heads of confederations (6 of the 8 giants at the present) and most of each polity's war strength. Arm B (villages only in the last 200 years) would empty confederations and war before that; arm C would have to regenerate the same numbers. docs/review/culture/polities/round5.md
- 2026-11-03: Milestones 11-03: later -> v3: v3 must-have: village experiment, which the polities proposal runs before polities v0 reads the ledger
- 2026-11-03: Triage 11-03: v2 -> later: languages, polities, religion and owner's-world empires wait until food is done (fresh-eyes review, D44)
- 2026-11-01: Daniel 11-01: go (O3).
- 2026-11-01: Created.
