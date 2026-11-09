---
id: PW-1616
title: Live polities and the settlement ledger ignore the war era dials and the times of troubles
type: task
status: todo
parent: PW-917
milestone: v4
subsystem: peoples
effort: m
impact: med
found_by: lane259
blocked_by: []
relates: [PW-1172, PW-1243, PW-1434, PW-1108, PW-661]
refs: ["planet/lineages/history/counter.py::CounterMixin._troubles", "planet/lineages/history/counter.py::CounterMixin._war_era", "planet/lineages/history/polity_live.py::LivePolities._risings", "planet/lineages/history/polity_live.py::LivePolities.pacification", planet/lineages/settlements.py, planet/lineages/history/params.py, docs/review/peoples-counterpressures/design.md, "Turchin 2009 Ann. N.Y. Acad. Sci. 1162:1, Table 1"]
created: 2026-11-09
updated: 2026-11-09
---

## Description
**In plain words.** Lane 259 gave the history "times of troubles": a crowded people now and then has a troubled century in which its
wars flare and people flee (a 'troubles' event in the history). But the states the history builds (live polities, PW-1434) and the
towns the settlement ledger sacks never hear of it. So a people can be in its troubles while its kingdom carries on untouched, and its
towns are sacked no more often than in a calm century. The two new "how warlike are the peoples" dials for the early and late eras
also move only the history's war-torn land, not the polities' wars or the ledger's sacks (those still read only the master dial
meta.war).

What misleads if never done: the story contradicts itself on the map (a troubled people with a calm state and unsacked towns), and
the early/late war dials look broken to someone watching sacks or polities change.

Lane 259 stayed out of `polity_live.py` (lane 258 was rewriting it). What to try:
- polity_live: a people in troubles this step (`History.troubles_n` grows, or a per-step flag the counter could expose) weakens its
  ruling polity: risings or secessions more likely that step (Turchin 2009: instability 3.8 events a decade in decline phases against
  0.6 in growth, Table 1), and pacification G lapses toward 1 for that people;
- settlements: the sack and raid chances x the same E(lev) blend (`CounterMixin._war_era`), and higher in a troubled century.
- [ ] a troubled people's polity shows it (a rising, a secession or a weaker pacification) in the same step
- [ ] meta.war_early / war_late move the settlement ledger's sacks as they move war-torn land

## Updates
- 2026-11-09: Created from inbox draft draft-polities-read-war-troubles.md (found by lane259).
