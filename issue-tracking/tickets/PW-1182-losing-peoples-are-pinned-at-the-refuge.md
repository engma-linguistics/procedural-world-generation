---
id: PW-1182
title: Losing peoples are pinned at the refuge floor (~0.5 Mkm²) instead of finding a niche of their own
type: task
status: todo
parent: null
milestone: v1
subsystem: timezoom
effort: s
impact: med
found_by: lane77
blocked_by: []
relates: [PW-920, PW-928]
refs: [planet/lineages/history/competition.py, planet/lineages/history/params.py, tools/peoples_robust.py, tools/peoples_robust/trees/menagerie.toml]
created: 2026-10-30
updated: 2026-10-30
---

## In plain words
Many of the smaller peoples end every history holding exactly the same small area, about 0.5 million km² (some 40 cells at L6). That
is the size at which the history stops pushing a losing people back. It isn't a country they found or chose. In the 52-people
menagerie tree, bugbears, firbolgs, loxodons, plasmoids, minotaurs, shifters, duergar, drow and locathah all sit at 0.44-0.54
Mkm² (seed 7, world 4360a3). In dnd, bugbears sit there at density x0.5, x1 and x2 alike. So their density knob moves their reported share only by
arithmetic, never their land.

## Description
competition._compete: a people held above its room loses r = (1 - exp(-dt/TAU)) x clip(held / REFUGE_MKM2 - 1, 0, 1) of the excess,
so displacement stops at REFUGE_MKM2 = 0.5 Mkm², and HOLD_MIN's lapse keeps the range above the same floor. That is "last refuges
hold out", a deliberate floor. But the people then sits wherever the floor caught it (often its founding blob). Nothing makes it
leave for country where it would not be squeezed. Jumps need the people hemmed in (JUMP_HEMMED) and crowded, and they found only on
free land.
Suite numbers (lane 77, range arm): menagerie s7 on 4360a3: 9 of 52 peoples at 0.44-0.54 Mkm², 2 more under it; dnd knob bugbear x0.5 / x1 / x2: area
0.47 / 0.51 / 0.51 Mkm².
Options: (A) a refuge-bound people's jumps ignore JUMP_HEMMED and weigh places by its own room there (K minus rivals' load),
so a squeezed people relocates to where it does better. (B) The floor shrinks with how long a people has been at it, so a hopeless
remnant can end. That is honest extinction with a stated reason, which the owner allows for a reason. (C) Leave it: slivers are
survivors. Lean: A; judge it on the suite's menagerie and knob rows (the area should move with the knob).

## Updates
- 2026-10-30: Created from inbox draft draft-peoples-pinned-at-refuge-floor.md (found by lane77).
