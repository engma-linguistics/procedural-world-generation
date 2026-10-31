---
id: PW-1071
title: "Guild split: the size classes are weighted by M^0.75 while the dragons eat at M^0.889, and young dragons (79% of them, under 1 t) still eat only from the apex class's share"
type: task
status: done
parent: null
milestone: v2
subsystem: timezoom
effort: s
impact: med
found_by: dragon-density-r2
blocked_by: []
relates: [PW-1019, PW-977, PW-958]
refs: [planet/lineages/history/megafauna.py, docs/review/megafauna/dragon-density/sensitivity.py]
created: 2026-10-30
updated: 2026-10-31
---

## Description
**In plain words.** The model shares the hunters' food between small, middling and dragon-sized hunters by a rule of how much an animal
of each size eats. It uses one rule (the mammal one) for that split and another (the reptile one) for the dragons' own appetite. Using
the reptile rule for both would give the dragons about half as much food again. Separately, most dragons are young and small (wolf- to
bear-sized), yet all of them feed only from the share for animals over a tonne; the paper the size classes come from argues that young
tyrannosaurs hunted in the smaller classes.

Evidence:
- megafauna.GUILD_KLEIBER = 0.75; Carbone, Turvey & Bielby 2011 give abundances, not food (Table 1, p. 2683). The weighting itself has a
  source: Carbone & Gittleman 2002 expect M^-0.75 per unit prey production and fit -0.66 (CI -0.48 to -0.85; p. 2274; note 10, p. 2275).
  Carbone, Teacher & Rowcliffe 2007: intake ~M^0.79 across carnivores but ~M^0.6 within large-prey hunters (Table 1; p. 364).
- Apex share (sensitivity.py): b = 0.6 9.9%; 0.66 12.3%; 0.75 16.8%; 0.79 19.2%; 0.85 23.3%; 0.889 (Nagy's reptile slope) 26.2%.
- Young dragons: under the "younger" schedule wyrmlings are 24% of dragons (mean 17 kg) and young 54% (mean 262 kg), eating 16% of the
  dragons' food. Carbone et al. 2011's thesis: juvenile T. rex competed in the smaller classes; the classes are built from adult masses
  and juvenile and sub-adult T. rex "may have been relatively abundant compared with adults" (p. 2683).

Direction and size on dragons: the exponent x0.59 to x1.56; letting wyrmlings and young eat from the smaller classes' share about +19%.
- [ ] owner: one exponent for both (which?), and whether young dragons draw on the smaller classes

## Updates
- 2026-10-31: Status needs-decision -> done. Lane 90: GUILD_EXP = the intake law's 0.734; dragon_share counts the young dragons' food inside the smaller classes (Carbone 2011 p. 2683): ~21% of the guild's food. docs/review/dragon-food-chain/report.md
- 2026-10-30: Created from inbox draft draft-guild-weighting-exponent-and-young-dragons.md (found by dragon-density-r2).
