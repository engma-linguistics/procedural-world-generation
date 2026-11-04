---
id: PW-794
title: "Horses (and similar high-value mounts) are adopted almost at once on contact: the use front should move at the people-contact speed where the habitat allows (grassland/open), limited by real barriers (dense forest, tsetse-like tropics, mountains, sea)"
type: task
status: todo
parent: PW-103
milestone: later
subsystem: timezoom
effort: s
impact: med
found_by: owner
blocked_by: []
relates: [PW-783]
refs: []
created: 2026-10-24
updated: 2026-11-03
---

## Description
Owner 2026-10-24: like the Plains peoples after horses arrived (~1680-1750, spread across the Plains within decades, partly ahead of Europeans via trade and feral herds), any people in sustained contact who aren't being wiped out should take horses up fast. Coordinator note: real barriers mattered too (tsetse kept horses out of much of sub-Saharan Africa; dense forest and islands slowed them), so 'immediately where the land suits horses'.

## Updates
- 2026-11-03: Triage 11-03: v2 -> later: ice-age/time-zoom work, parked post-v1 (epic PW-470)
- 2026-10-24: Created.
- 2026-10-24: (fun lane 22) animal_defs `uptake = "contact"` (horse) moves the use front at animals.CONTACT_KMYR (8 km/yr vs 1.8) over peopled land, full speed where the cell is in the wild range, pressure x0.8 per cell outside it (forest, tropics, high ground); sea unchanged (boats). seven_meals on 6fbc2c, horse tamed 6.0 kyr ago: known 40.2 -> 152.4 Mkm2 (on wild range 17.8 -> 47.6), peoples taking it up (>=20% of land) 10 -> 29 lines, last uptake 0.1 -> 0.2 kyr ago but most within 1-2.5 kyr of first taming; forest peoples (elf, anja) still low (0.24, 0.31). New summary key `reached_kyr` (landmass -> when use arrived). Riders test unchanged and strict. Needs the owner's eye on whether the world is now over-horsed; see the inbox draft.
