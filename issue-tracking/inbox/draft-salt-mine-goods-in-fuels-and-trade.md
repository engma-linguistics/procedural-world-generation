---
title: Salt mining is read in the brief only; salt works, brines and cured goods do not feed the fuels or a trade table
type: task
status: todo
parent: PW-692
milestone: later
subsystem: timezoom
effort: m
impact: low
found_by: fun-lane-23
blocked_by: []
relates: [PW-797, PW-796]
refs: [planet/lineages/mining.py, planet/lineages/salt_reach.py, planet/lineages/brief.py]
---

## Description
PW-797 v0 adds: the `salt_rock` good, `mining.py` (kind per miner people: salt, ore, salt and ore), a `mining` section in the
brief, a suggested note (what the miners sell and buy back) and `salt_reach.reach(mined=...)` that trades mined salt 1.6x
further (MINED_CAP). Not done: brine boiling at salt mines costs fuel (Hallstatt, Wieliczka), salt-preserved goods (salt pork,
brined cheese) as a trade good, ore-for-salt exchange rates, a real trade table (brief `trade_reach` is still null),
and 'what they get back' is only the miners' country lacks plus neighbour names. Mineral licks stay a poor human salt source.
- [ ] decide whether MINED_CAP should come from a trade table once PW-796 has one
