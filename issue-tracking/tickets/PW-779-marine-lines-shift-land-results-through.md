---
id: PW-779
title: Marine lines shift land results through the shared random stream; give them their own stream, and a low density for storm giants (111 Mkm2 = most of the ocean)
type: task
status: done
parent: PW-729
milestone: v2
subsystem: timezoom
effort: s
impact: med
found_by: coordinator
blocked_by: []
relates: []
refs: []
created: 2026-10-24
updated: 2026-10-24
---

## Description
fun17: with marine lines present, land peoples diverge (dnd dwarf x0.03, gnome x0.15) because marine lines skip the land hop draws. Adding merfolk should not change the dwarves: draw marine randomness from a separate generator. Storm giants hold ~111 Mkm2 in both presets; a rare people needs a low density/share.

## Updates
- 2026-10-24: Status todo -> done. Merged 8537297: per-line generators; land lines byte-identical with/without marine lines; storm giants 111 -> 2.35 Mkm2.
- 2026-10-24: Created.
- 2026-10-24: fun18: a generator per line (seeded run seed + line id) for origin noise, hops and the step order key, so no line's draws depend on how many others are alive; a land parent ends and hands its range over among its land children only (a marine child neither took its land nor held back its end). Test: land/stem/twig/curse byte-identical with and without marine lines (fake world). 1df1c3 seven_meals with vs without merfolk+storm giants: all 48 land lines cell-for-cell identical (a wish toward a marine line is authored coupling, dropped from both). Storm giants narrowed to the cool open sea (temp 6-16 C, depth -3500..-300 m): 111.4 Mkm2 / 240k people -> 2.35 Mkm2 / 7.3k (density kept 0.005).
