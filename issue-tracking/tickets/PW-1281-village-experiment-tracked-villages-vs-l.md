---
id: PW-1281
title: "Village experiment: tracked villages vs last-200-years only vs generated on demand"
type: task
status: todo
parent: null
milestone: v2
subsystem: culture
effort: s
impact: med
found_by: coordinator
blocked_by: []
relates: []
refs: []
created: 2026-11-01
updated: 2026-11-01
---

## Description
**In plain words.** Daniel worries tracking every village on the 100-year step is too granular. Test three arms on one L6 world (then one L7): A villages tracked throughout; B villages only in the last 200 years; C as B plus villages generated on demand from town data. Measure towns and cities (counts, sizes, founding steps), culture sizes and minorities in the ledger, polity seeds, generated vs tracked villages, and ledger size and wall time. Pass if B and C stay within the run-to-run noise of a re-seeded A. Design: docs/review/cultures-proposal/proposal-r2.md section 2.3. Needs Daniel's go (open decision O3).

## Updates
- 2026-11-01: Daniel 11-01: go (O3).
- 2026-11-01: Created.
