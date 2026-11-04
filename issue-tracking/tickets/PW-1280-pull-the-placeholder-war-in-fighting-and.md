---
id: PW-1280
title: Pull the placeholder war, in-fighting and state proxies out of counter.py behind one seam for polities
type: task
status: done
parent: null
milestone: v3
subsystem: peoples
effort: s
impact: med
found_by: coordinator
blocked_by: []
relates: []
refs: [planet/lineages/history/rule.py::StandIns, planet/lineages/history/counter.py::CounterMixin, tests/test_lineages.py::test_polities_swap_the_state_and_war_stand_ins_through_one_seam, docs/review/culture/polities/round5.md, tools/peoples_robust.py::run_one]
created: 2026-11-01
updated: 2026-11-04
---

## Description
**In plain words.** Before polities can replace today's stand-ins, list and isolate them: the in-fighting term (FEUD_CUT, SOCIAL_Q), the state-pacification proxy G and the hostile-frontier share F in planet/lineages/history/counter.py. Put them behind one small interface so polities v0/v1 swap them without touching the rest. No behaviour change; golden outputs must not move. Prep lane for polities (cultures proposal round 2, section 3.3 and 7). Relates PW-1258 (which parks their sizes, not their extraction).

## Updates
- 2026-11-04: Status todo -> done. Lane 180: the stand-ins (pacification G, hostile frontier F with its hostility matrix, in-fighting's circumscription C) moved from history/counter.py into planet/lineages/history/rule.py::StandIns, read through History.rule; polities v1 swaps them by setting CounterMixin.Rule (test_polities_swap_the_state_and_war_stand_ins_through_one_seam). Bit-identical: history state sha256 and the robust suite's run_one numbers unchanged on dnd-s7@4360a3 and sm-s7@af2677; goldens unchanged. docs/review/culture/polities/round5.md
- 2026-11-03: Milestones 11-03: later -> v3: v3 must-have: the seam polities v0 swaps the placeholder war and state proxies through
- 2026-11-03: Triage 11-03: v2 -> later: languages, polities, religion and owner's-world empires wait until food is done (fresh-eyes review, D44)
- 2026-11-01: Created.
