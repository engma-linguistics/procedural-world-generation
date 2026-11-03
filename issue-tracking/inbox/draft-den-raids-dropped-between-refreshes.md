---
title: "Den peoples lose their raiding share when their tech moves between ladder refreshes"
type: task
status: todo
parent: null
milestone: v2
subsystem: peoples
effort: xs
impact: low
found_by: lane 146
blocked_by: []
relates: [PW-1386]
refs: ["planet/lineages/ladder.py::Ladder.refresh", "planet/lineages/ladder.py::Ladder.settled_near", "planet/lineages/ladder.py::Ladder.line"]
---

## Description
In plain words: goblins, kobolds and troglodytes get part of their food from raiding farmers nearby. That share is worked out only on
the ladder's full refreshes (every 500 years). If such a people learns something new in between (say a herd animal), its line is
redone without the farmers-near map, so its raiding share drops to nothing until the next full refresh.

Where: `Ladder.refresh` computes `sn = self.settled_near()` only when `due` and passes it (None when not due) to `line`, which skips
the raid when it is None. Lane 146 (PW-1386) met the same pattern for the foragers' trade share and kept the last map there
(`self._fn`); the raids still drop. Fix: keep the last `settled_near` the same way. It changes den peoples' numbers a little, so the
golden test needs an on-purpose update; check on the robust suite (base family) that the den kinds' ranges move only slightly.
- [ ] `settled_near` kept between due refreshes, as `_fn` is
- [ ] golden updated on purpose; robust base family invariants hold
