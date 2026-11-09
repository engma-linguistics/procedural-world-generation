---
title: "Languages: accusative and ergative flagging are drawn independently, as case was before lane 7"
type: task
status: todo
parent: PW-767
subsystem: culture
effort: s
impact: low
found_by: language lane 7 (PW-1586)
blocked_by: []
relates: [PW-1586]
refs: ["planet/language/grammar.py::_draw_feature"]
---

## Description
In plain words: lane 7 found that a language's case system was drawn as two separate coin flips ("are there core
cases?" and "are there oblique cases?"), each ignoring the other. Real languages that have one usually have both, so
the separate flips made too many middle-sized systems and too few large ones. Drawing the second flip given the first
fixed it (6+ cases 19% -> about 32% in the harness, WALS 32%).

The alignment draw has the same shape: accusative (GB408) and ergative (GB409) flagging are flipped separately, and
both together are read as "split". With Grambank's rates (44% and 22%) independence alone gives about 10% split
systems, whatever the real joint rate is. Fix: draw GB409 given the drawn GB408, as `case` now does, after checking
Grambank's joint count for the two features (the correlation table has no row for the pair, so the joint needs the
raw values). Check `number` (GB043/GB044) for the same pattern while there.

**What misleads if never done:** the share of split-ergative languages is set by an accident of the draw, not by the
data, and the alignment check would agree only by luck.
