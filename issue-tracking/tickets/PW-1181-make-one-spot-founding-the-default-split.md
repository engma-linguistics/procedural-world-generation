---
id: PW-1181
title: Make one-spot founding the default (SPLIT_FOUNDING = local); decide whether a stem's range still passes to its children at its end
type: task
status: done
parent: null
milestone: v2
subsystem: timezoom
effort: xs
impact: high
found_by: lane77
blocked_by: []
relates: [PW-1152, PW-677, PW-888]
refs: [planet/lineages/history/origins.py, planet/lineages/history/params.py, tools/peoples_robust.py]
created: 2026-10-30
updated: 2026-11-03
---

## In plain words
The owner ruled (10-30) that a new people starts at one spot and spreads from there. Lane 77 built that as a switch
(`SPLIT_FOUNDING = "local"`) and measured it on the stress suite, 59 runs against 84 of today's model. It does what was asked. The
kobolds and dragonborn no longer start with the dragons' worldwide range: kobolds fall from 5.4% to 0.24% of people, dragonborn from
4.8% to 1.0%. No people dies out and nothing crashes. It does not make the peoples more even on its own: the humans take the room
the kobolds and dragonborn leave (dnd humans 65% to 72%).
One question is left for the owner. When a stem ends at its last split, its remaining land still goes to its children of the same
kind. The kenku inherit 56 million km² of the avian stem that way, so they are not "one spot" either. A stricter setting
(`local_vacate`) leaves that land empty for the children to spread into.

## Description
`SPLIT_FOUNDING` (params.py; origins._origin_split, _polycentric, _end_parent):
- range (today): the founders also take the whole cut-off part of the parent's range they arise in (78/86 kobold origins, 73/86
  dragonborn, 72/86 aarakocra are "isolated part of the parent's range"), up to POLY_MAX polycentric patches, and the stem's range
  goes to its children at its end, whatever their kind.
- local: FOUNDER_KM about the origin only; no polycentric patches (an authored choice only, per the ruling: portals, or a future
  per-line `sites`); at the stem's end its range passes only to children of its own kind (megafauna to megafauna, peoples to peoples).
- local_vacate: local, and the stem's range passes to no child.
Suite medians, dnd (base + jitter, 14 runs per arm; local_vacate 4 runs on one world only, so information only):
| | range | local | local_vacate |
|---|---|---|---|
| humans | 65% | 72% | 77% |
| kenku | 6.7% | 7.1% | 0.93% |
| kobolds | 5.4% | 0.24% | 0.21% |
| dragonborn | 4.8% | 1.0% | 0.38% |
| brittle peoples (swing > 10x) | 9 | 12 | 4 (n = 4) |
Founding area (median Mkm²): kobold 1.05 to 0.19, dragonborn 1.99 to 0.29, kenku 7.2 to 0.37. Inherited at the stem's end:
kobold 17.6 to 0, dragonborn 21.9 to 0, but kenku 42 to 56 and lizardfolk 28 to 37 (same-kind stems).
Options: A. Default local now (the ruling), keeping PW-677's same-kind handover. B. Default local_vacate (one spot, strictly);
re-measure it on the full suite first (`--arms local_vacate`). Lean: A now, B measured next. Either way, pair it with the
split-teleport fix (draft "split whose stem has died out ... best habitat anywhere"). That fix is what keeps "one spot" near the
parent when the parent is gone.

## Updates
- 2026-11-03: Status needs-decision -> done. Closed 11-03: the SPLIT_FOUNDING switch is gone (params.py comment, lane 83); one-spot founding is the rule (owner D20, 10-31) and origins._end_parent leaves a stem's land empty, passing to no child (the strict local_vacate option); overview 2.26.
- 2026-10-31: Milestone v1 -> v2 (v1 cut plan, docs/review/v1-cut/plan.md): not a tag blocker; v1 tags the planet, peoples ship as a preview.
- 2026-10-30: Created from inbox draft draft-local-founding-default-and-stem-handover.md (found by lane77).
