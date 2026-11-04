---
title: "GROUP_MARGIN x667 leaves a dnd run bit-identical: the groups' found-and-diverge test may never bind"
type: task
status: todo
parent: null
milestone: later
subsystem: peoples
effort: s
impact: low
found_by: lane176
blocked_by: []
relates: []
refs: [planet/lineages/history/groups.py, planet/lineages/history/habitat.py, docs/review/peoples/ledger/round1.md]
---

## Description
**In plain words.** A people's groups (hill dwarves, the herders and farmers of a people) are meant to appear and spread where
their own country suits them better than their people's, by a 15% margin. Raising that margin to 100x, which should stop every
group from appearing or spreading, left a dnd run identical bit for bit.

**What breaks if it is never done.** The groups' placement either comes from somewhere else, so the docs (overview §2.26,
groups.py) describe a rule that doesn't act, or it is dead code that the ledger would retire. Either way, a reader trusts a
mechanism that does nothing.

- Measured (lane 176): dnd seed 7 on 4360a3, `GROUP_MARGIN` 0.15 -> 100 through the robust suite's params override (groups.py and
  habitat.py both import it): every people's share, range and population and the event counts were identical.
- [ ] trace where dnd's groups actually found and grow (`groups._diverge`, the template or split paths)
- [ ] if the margin test never binds at the defaults, retire it (a refactor, pre-approved under the ledger) or fix it
