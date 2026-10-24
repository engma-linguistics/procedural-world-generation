---
id: PW-788
title: Showcase README for 067778, a12762, 6909cb still describes dairy as fresh-only (written before PW-784)
type: task
status: todo
parent: PW-692
milestone: v2
subsystem: docs
effort: xs
impact: low
found_by: fun20
blocked_by: []
relates: [PW-784]
refs: [docs/review/lineages/showcase-peoples/README.md]
created: 2026-10-24
updated: 2026-10-24
---

## Description
Only 6fbc2c was re-run (run eaf863) after PW-784, so the README's notes and the comparison table row "dairy | fresh only" for
the other three worlds (a703b0, e06714, 7fd2b7) are the old numbers. If those worlds are kept as showcases, re-run
`planet lineages WORLD --tree seven_meals --tries 1` on them and update their lines and the table; otherwise mark the notes as pre-PW-784.
- [ ] README rows for the three worlds match a run made with the dairy rule.

## Updates
- 2026-10-24: Created from inbox draft draft-showcase-worlds-rerun-for-dairy.md (found by fun20).
- 2026-10-24: fun21: re-ran seven_meals on 067778, a12762, 6909cb (runs b36648, 1184cc, b4e3c2), deleted a703b0/e06714/7fd2b7, README notes, table and the 104de8 section refreshed.
