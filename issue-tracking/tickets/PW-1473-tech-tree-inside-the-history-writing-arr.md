---
id: PW-1473
title: "Tech tree inside the history: writing arrives ~2,000 years late (or never) against the after-run tree of the same history"
type: task
status: todo
parent: PW-661
milestone: v4
subsystem: culture
effort: m
impact: high
found_by: lane-192
blocked_by: []
relates: [PW-1466, PW-1434, PW-1459]
refs: [planet/lineages/history/tech_live.py, "planet/lineages/history/tech_live.py::LiveTech._links", "planet/lineages/techtree.py::Calendar.advance", "planet/lineages/techtree.py::links_of", "planet/lineages/techtree.py::rebuild", docs/review/culture/polities/round8.md, "world 899985 (time zoom fc5311) L7, dnd seed 7, polities in the history on (scratch run, deleted)"]
created: 2026-11-04
updated: 2026-11-04
---

## Description
**In plain words.** With polities in the history switched on, the tech tree now runs inside the history (PW-1466). Most of its
dates match the tree built after the same history: villages, towns, chiefdoms and proto-writing are the same or within a few
centuries. But writing, and what needs it, comes about 2,000 years late or never. On 899985 seed 7 (dnd): the humans never write
(after-run: 2,511 years ago), the hobgoblins write 641 years ago (2,603), the orcs 312 (2,603), the elves never (3,115). So the live
states start only ~500 years ago (36 now), and the switch-on world has far fewer states than the switch-off world, for a reason
that is bookkeeping, not history.

**What breaks if never done.** The live polities cannot become the polities (v4): their states would come two thousand years late
on every world, and the comparison of on and off would mislead.

**Likely cause (untested).** Writing spreads almost only by contact. A pair's front delay is fixed the first time the tree looks at
the pair (`Calendar.advance`: `arrive[k3]`, never moved later), using the border's median so far (`LiveTech._links`). Early in a
contact the border is short, so the live tree fixes a slow front; the after-run tree uses the whole run's median border. Try first:
log, for writing's arrivals, the border weight w the live and after-run trees used per pair. If that is it, candidates: let a live
front be re-timed (never later) when the pair's median border grows, which also allows the after-run tree to stay bit for bit; or
read the border at the step rather than the median.
- [ ] writing's date per people within the 12-seed spread (round 6) of the after-run tree of the same history, on 899985 seeds 7 and 10
- [ ] with the switch off, runs still byte-identical

## Updates
- 2026-11-04: Created from inbox draft draft-live-tree-writing-arrives-late.md (found by lane-192).
