---
id: PW-1603
title: "Calendars: how many counts should a world have? States give hundreds on Seven Meals"
type: task
status: todo
parent: null
milestone: later
subsystem: culture
effort: xs
impact: low
found_by: lane255
blocked_by: []
relates: [PW-1435]
refs: [planet/lineages/calendars.py, "planet/lineages/calendars.py::derive", "planet/lineages/calendars.py::P_STATE", "run:1e97dd", "run:a24559", "run:07c755", docs/overview.md]
created: 2026-11-09
updated: 2026-11-09
---

## Description
In plain words: cultures that keep written records can now start counting years from an event, such as "year 212 of the
Founding of Iligya". Most counts come from states, because the states read-out has 600 to 1,600 states and empires per run.
On the stored L7 runs (11-09, current code) the counts are: 78 calendars, 10 still in use, on a24559 (D&D); 308, 45 in use,
on 1e97dd (Seven Meals); 206, 51 in use, on 07c755 (Seven Meals). The odds behind them are judgement calls (module
docstring), loosely set against about 25 pre-modern eras in Wikipedia's "Calendar era" list. If nothing is decided, the viewer's
"dates in" picker on a Seven Meals world lists about 45 live counts and 260 gone ones. It works, but it is long, and repeated
place names show up as "the Founding of the west of Lameth VII".

Options:
- A: keep the odds as they are. Every count has a real event behind it, and the picker sorts the live ones first.
- B: count only the states that reach empire rank, plus faiths and conquests. That gives roughly a third as many.
- C: aim for about 5 to 15 live counts per world by scaling the state odds to the run's number of states.

Lean: A for v4. B is a one-line change if Daniel finds the list too long in the viewer. C is the "fiddly" kind of tuning the
11-03 north star warns against.

Nothing breaks if this is never decided. The only cost is a long picker on busy worlds.

## Updates
- 2026-11-09: Coordinator 11-09: keep the odds (lane's lean); picker lists counts in use first. Moved to later; revisit if Daniel finds it long.
- 2026-11-09: Created from inbox draft draft-calendars-how-many.md (found by lane255).
