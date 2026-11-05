---
title: "How far may a scheduled invasion's expedition go? One more state's reach crosses ~150 km, too short for most rows"
type: task
status: needs-decision
parent: null
milestone: v3
subsystem: peoples
effort: s
impact: med
found_by: lane198
blocked_by: []
relates: [PW-1450, PW-1433]
refs: ["planet/lineages/polities.py::_expedition", "planet/lineages/invasions.py::expedition", "planet/lineages/invasions.py::mobility", docs/review/culture/polities/invasions_reach.md, docs/review/culture/polities/invasions_reach_score.py, "run a2b637", "run 3c1caf"]
---

## Description
In plain words: a strong invasion now sends an expedition when the invaders do not border the victims (PW-1450, D50 B). The
expedition may go as far as the state's own reach again, times the people's mobility (x2 for nomads and herders). On a2b637 and
3c1caf most states have 150 foot-km, so a settled people's expedition crosses only about 150 km. The strong rows that happen rose
only from 9 to 11 of 30 (a2b637) and from 8 to 11 of 42 (3c1caf). The rest still say "no state bordered them" (invasions_reach.md).

What misleads if never done: Daniel writes "the dwarves come down on the hobgoblins" and it still says "it didn't" whenever the
two are more than a day or two's march apart. D50 was meant to fix exactly that.

Options:
- A. Keep one more reach (now). Honest, but most rows still fail.
- B. A fixed campaign range (for example 1,000 km, like invasions.FROM_KM's "from that part of the continent"), times mobility.
  Simple: settled peoples reach their region, nomads twice as far.
- C. No limit over land a people could cross (any distance on the same continent; sea only with boats). A strong row then always
  finds the victims unless an ocean is in the way.
Lean: B. It keeps distance meaningful, and mobile peoples still stand out. The read-out already says how far the nearest victim
polity was, so a re-score is one constant and one run of invasions_reach_score.py.
