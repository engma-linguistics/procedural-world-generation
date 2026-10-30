---
id: PW-1106
title: "Settlements overlay: villages carpet the globe; show towns and cities at globe scale, villages when zoomed; fix 'the human' wording"
type: task
status: done
parent: PW-1011
milestone: null
subsystem: viewer
effort: s
impact: med
found_by: coordinator
blocked_by: []
relates: []
refs: [docs/review/settlements/2-after-present.png]
created: 2026-10-30
updated: 2026-10-30
---

## Description
**In plain words.** With "Settlements and ruins" on, which is the default, nearly every peopled cell gets a village dot in the same colour. At whole-globe view the continents turn into a carpet of dots, and that hides the colour layer underneath. Towns and cities, the interesting part, are lost among them.

Suggested:
- at globe scale, show towns and cities (and city ruins) only;
- fade villages in as the camera zooms;
- or make villages a separate checkbox, off by default.

The hover card also says "city of the human" and "founded … by the human". It should use the people's plural name ("the humans").

## Updates
- 2026-10-30: Fun lane 61, after the owner's look (10-30: the town dots still far too many, keep the hover): at the default globe view only cities and city ruins show; towns fade in from 10 to 16 px between neighbouring cells on screen, villages, mines and lesser ruins from 18 to 28 px. Shots 9 and 10 retaken.
- 2026-10-30: Status todo -> done. Fun lane 61: at whole-globe view the overlay shows only towns, cities and city ruins; villages and the ruins of villages and towns fade in as the camera closes in (fully hidden while neighbouring cells are under 14 px apart on screen, fully shown from 24 px; so the rule follows the grid level and the window, viewer/globe/settlements.js villageFade). A new box under the overlay, 'villages when zoomed in' (on; ?settleVillages=0), turns them off altogether. Hover and 'why' wording use the people's plural name without its note ('city of the humans', 'driven out by the elves'). ?dist= did nothing when lat/lon were also given (the turn's animation kept the old distance); turnTo now keeps the camera's current distance, so zoomed screenshots work. Before/after: docs/review/settlements/8-11.
- 2026-10-30: Created from inbox draft draft-settlements-overlay-clutter.md (found by coordinator).
