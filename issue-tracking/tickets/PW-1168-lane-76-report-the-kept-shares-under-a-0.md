---
id: PW-1168
title: "Lane 76 report: the kept shares under a 0.5%/yr loss (humans 43%) disagree with its own r of ~4.3%/yr (94%)"
type: task
status: done
parent: null
milestone: v2
subsystem: docs
effort: xs
impact: low
found_by: lane-82
blocked_by: []
relates: [PW-917, PW-1148]
refs: [docs/review/peoples-demography/report.md, docs/review/peoples-counterpressures/design.md]
created: 2026-10-30
updated: 2026-10-30
---

## Description
docs/review/peoples-demography/report.md section 3, "Steady losses", gives N*/K = 1 - h/r at h = 0.5%/yr as humans about 43%, kobolds
and goblins 65-70%, and dwarves, gnomes and elves 0. Those figures imply r_human ~0.9%/yr. The same section's table gives r_max = 4.3%/yr
for human-likes, and lane 78's life tables give 4.40%/yr (forager schedule). Recomputing with lane 78's tables (scratch l82/kept.py,
war-weighted stages) gives humans 0.94, kobolds 0.98, dwarves 0.86 and elves 0.46. With the 0.5%/yr on every stage: humans 0.89,
kobolds 0.96, dwarves 0.71, elves 0.

Correct the report's bullets, or note which r they used, so later designs don't inherit the slip. The conclusion "slow peoples persist
only where little kills them" stands.

- [ ] fix or annotate report.md section 3 "Steady losses"

## Updates
- 2026-10-30: Status todo -> done. Fixed in report.md section 3 and on the owner's desk: 88% / 93-94% / ~55% / ~18% from the report's own r_max at h=0.005.
- 2026-10-30: Created from inbox draft draft-lane76-sustainable-loss-figures.md (found by lane-82).
