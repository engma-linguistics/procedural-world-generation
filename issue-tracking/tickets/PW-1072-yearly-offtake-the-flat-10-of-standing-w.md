---
id: PW-1072
title: "Yearly offtake: the flat 10% of standing wild biomass is about half of large herbivores' production (Coe 1976: median 0.20/yr; Farlow 1993: 0.14-0.26/yr); make it follow prey production"
type: task
status: needs-decision
parent: null
milestone: v2
subsystem: timezoom
effort: s
impact: med
found_by: dragon-density-r2
blocked_by: []
relates: [PW-991, PW-977]
refs: [planet/lineages/history/megafauna.py, docs/review/megafauna/dragon-density/sensitivity.py]
created: 2026-10-30
updated: 2026-10-30
---

## Description
**In plain words.** The model lets all the hunters together, people included, take a tenth of the wild herds each year. The papers on
file say large African herds produce about a fifth of their weight in new animals a year, and Farlow's formula gives a seventh to a
quarter depending on the size of the grazers. So the tenth is about half of what the herds make: not wrong, but a guess, and one that
ignores that small grazers breed faster than big ones. This may belong inside PW-991.

Evidence:
- megafauna.OFFTAKE = 0.1, unsourced (PW-991).
- Coe, Cumming & Phillipson 1976, Table 1 (pp. 344-345): production / biomass of 24 African wildlife areas 0.085 to 0.26 a year,
  median 0.20, pooled 0.16 (from assumed size-class P/B of 0.05 / 0.20 / 0.35, pp. 343-344).
- Farlow 1993, eq. 6 (p. 172): turnover 0.94 M^-0.28/yr: 0.26 / 0.165 / 0.136 / 0.11 at 100 / 500 / 1,000 / 2,000 kg. His best case lets
  predators take all of it (p. 171); real communities run 2 to 4 times above his best-case ratio (p. 176).
- McNaughton et al. 1989's NSP fit gives 0.5-1.1/yr, but counts insects (p. 143): too high a bound for big game.

Direction and size on dragons: linear. 5% halves density; taking all of Coe's median production doubles it; Farlow's 100 kg turnover x2.6.

Options:
- **A.** Keep 10% as "about half of production", documented.
- **B.** Offtake = a share of production, with production = biomass x Farlow's turnover at the local prey mass.
- [ ] decide A/B (fold into PW-991 if the coordinator prefers)

## Updates
- 2026-10-30: Created from inbox draft draft-offtake-from-prey-production.md (found by dragon-density-r2).
