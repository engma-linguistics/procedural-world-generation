---
id: PW-1625
title: The after-run tech tree times every contact front from the whole run's median border, so it and the live tree still part on contacts
type: task
status: todo
parent: PW-661
milestone: v4
subsystem: peoples
effort: m
impact: med
found_by: lane265
blocked_by: []
relates: [PW-1597, PW-1596, PW-1473, PW-1612]
refs: [docs/review/culture/polities/round22.md, docs/review/culture/polities/round22/diff_known.py, docs/review/culture/polities/round22/trace.py, "planet/lineages/techtree.py::links_of", "planet/lineages/techtree.py::Calendar.advance", "planet/lineages/history/tech_live.py::LiveTech._links", "planet/lineages/history/tech_live.py::LiveTech._retime", docs/review/culture/polities/round9.md, "world 4360a3"]
created: 2026-11-10
updated: 2026-11-10
---

## Description
**In plain words.** The tech tree's know-how crosses from one people to a neighbour as a front whose speed depends on how long
their shared border is. The tree built after a run reads each pair as one interval, first contact to last, with the *whole run's
median* border; the tree inside the history (switch `POLITIES_LIVE`) can only read the border as it stands, and re-times a front
when the border grows (PW-1473). After lane 265 fixed the other read-out differences (regions, tracks; round22.md), this is what
still parts the two trees on the same history: on L6 world 4360a3 seed 7 (switch on, lane 265 code, scratch run 314c9b, gone) the
first differing date is the felines' spirit ritual, 943 kyr ago by contact live and never before the felines end rebuilt, and the
12 largest peoples' writing median is 2,848 ya live against 2,899 rebuilt on the same history and town footprint (one tree step).
The whole-run median is also the after-run tree seeing its own future: a front 5,000 years ago is timed partly by a border the
peoples only drew later.

Try: the after-run tree reads each pair's border of the time (meta.contacts' series, the value at the stored frame at or before
the step, as `techtree._frame_of` now does for the tracks) and re-times its fronts as the border grows, as `LiveTech._retime`
does; then live and after-run read contacts alike. This moves the default (switch-off) calendar; measure on the five PW-1597 pairs.

**What misleads if never done.** The two calendars cannot agree to the tree step on the same history, so the PW-1597 on/off
check keeps a residual that is the read-out's, not the history's; and every after-run calendar date taken by contact leans on
borders from the future.
- [ ] rebuilt tree on a switch-on run's history equals its live tree (round22/diff_known.py: no differing records from contacts)

## Updates
- 2026-11-10: Created from inbox draft draft-after-run-tree-reads-whole-run-borders.md (found by lane265).
