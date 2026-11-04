---
id: PW-1154
title: Techtree deposit test still reads ore as ore-bearing country (reach good at 0.5), not a deposit
type: task
status: needs-decision
parent: PW-856
milestone: later
subsystem: culture
effort: s
impact: low
found_by: fun-lane-74
blocked_by: []
relates: [PW-1146]
refs: [planet/lineages/techtree.py, planet/lineages/samples/techtree.toml, planet/lineages/mining.py, "run 488d7e"]
created: 2026-10-30
updated: 2026-11-03
---

## Description
In plain words. PW-1146 made mines count only rich, raw ore cells (0.75, ~8% of land on world 4360a3). The tech tree's
"does this people have a deposit" test (techtree `deposit_min` = 0.5 on the goods, which carry a one-ring reach) was left
as it was, so a people can still smelt copper or iron wherever the broader ore country (46% of land) reaches. I tried
moving it (run 488d7e, in memory, nothing written):
- raw ore at 0.75 (the mines' own rule): no people has iron at all (32 lines knew it before, 0 after), copper falls from
  33 to 26 lines, copper's first moves from aarakocra 5.9 kyr to human_farmer 5.2 kyr, bronze's first from kobold 3.9 to
  aarakocra 2.3 kyr, steel and carburised steel vanish. 2,966 of 15,662 (line, tech) records are lost. Not acceptable.
- raw ore at 0.5 (no reach, same threshold): copper, bronze, iron and carburised steel firsts and dates unchanged; steel's
  first people changes (human_nomad to human_farmer, same date); 107 of 518 first dates differ and 313 records are lost
  (mostly later techs of sea peoples such as tortle and lizardfolk).
So the tech tree needs a looser ore test than the mines do. Not changed in PW-1146.

Options: A. keep as is (ore-bearing country; smelting needs the metal in reach, not a worked seam). B. raw ore at 0.5 for
ores only (small knock-on, needs a golden/scorecard look). C. a middle threshold, e.g. raw 0.6.
Lean: A until the next history re-run, then B with the scorecard.
- [ ] Owner: A, B or C

## Updates
- 2026-11-03: Milestones 11-03: v2 -> later: tech-tree deposit test; not a must-have
- 2026-10-30: Created from inbox draft draft-techtree-deposit-test-on-raw-ore.md (found by fun-lane-74).
