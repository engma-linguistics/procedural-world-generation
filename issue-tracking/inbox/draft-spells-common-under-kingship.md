---
title: "Most gods grant spells once a people has kingship (68% of cultures have 3+ spell-granting gods)"
type: task
status: needs-decision
parent: PW-1308
milestone: v2
subsystem: timezoom
effort: xs
impact: med
found_by: lane133
blocked_by: []
relates: [PW-1311, PW-1306]
refs: [planet/lineages/gods.py::Pantheons.frame, planet/lineages/gods.py::TIERS, planet/lineages/gods.py::SPELL_IND, docs/review/religion/stats-round1.md, docs/review/religion/religion_stats_individuation.png, docs/review/religion/slice1.md, tools/religion_stats.py]
---

## Description
In plain words: slice 1 said that a people with temples and kingship but no high god would have one god that grants spells. The stats over
15 runs (2,738 living cultures, docs/review/religion/stats-round1.md) show otherwise: 68% of cultures have three or more spell-granting gods,
and 48% of all living gods grant spells. Cause: every non-leading god's ceiling is kingship's 0.6 x (0.5 + 0.5 x its devotion over the
leader's), which is over the spell line (SPELL_IND 0.5) for any god nearly as devoted as the leader.

Options:
- A: keep it (kingship means organised cults of many gods; clerics of several gods is very D&D).
- B: raise SPELL_IND to 0.65 (only kingship leaders and high gods grant spells; about one per culture).
- C: keep SPELL_IND, cap non-leading gods under it (0.45) so only the leading god of a kingship people grants spells.
Lean B or C if Daniel wants spell-granting to be rare; A if not. One constant either way; the stats tool re-measures it in a minute.
