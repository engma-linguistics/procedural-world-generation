---
id: PW-981
title: "Demes: phylogeography pass that cuts each people's range into speech/breeding populations per frame and tracks their splits, fusions and contacts into a dated deme tree"
type: story
status: todo
parent: PW-856
milestone: v2
subsystem: timezoom
effort: m
impact: high
found_by: owner
blocked_by: []
relates: [PW-767, PW-902, PW-731, PW-665]
refs: [planet/lineages/contacts.py, planet/lineages/spread.py, planet/lineages/crossing.py]
created: 2026-10-28
updated: 2026-10-28
---

## Description
Owner 2026-10-28 (design talk, no code yet). Foundation for every language path (faked or first-principles) and likely for PW-856's cultures. Today a people is one presence field over its whole range (humans on three continents = one blob) and groups split by way of life, not geography; no cell records which earlier population its people came from.
Output-only pass over the stored frames, like contacts.py:
- per frame, cut each people's occupied cells into demes by travel cost (corridor and sea-gap machinery from crossing.py) and isolation by distance (a connected continental range becomes a dialect chain, not one community);
- link demes across frames by overlap; newly settled cells at an expanding front take the label of the cell they spread from (spread.nearest_label may do most of it), giving founder chains;
- record splits, fusions, extinctions and deme-to-deme contact intensity over time; ice-age land bridges opening and closing should show up.
Result: a dated, located deme tree nested inside the authored people tree, plus a contact series per deme pair. Caveats: time resolution is the frame spacing (kyr in the glacial zoom); ancestry is inferred from range change; diffusive spread smooths fast corridor migrations.
- [ ] on a fantasy run, a widespread people splits into several demes along real barriers, with dates, and the tree is stored in run meta
- [ ] a review page/map of demes over time

## Updates
- 2026-10-29: Fun lane 46 follow-up: gap splits and fusions must hold 4 frames (PERSIST, from the fuse-back ages: half within 3 frames, flat after) and a 120 km neck of other peoples' land is bridged; b69f51 gap splits 459 -> 102, fusions 389 -> 68, gap events of 60+ cells 494 -> 114, but only 11% have sea, ice or a corridor changing in the gap (another people holds the gap in 90 of the rest); no land bridges on b69f51 (its sea barely moves), three drowned gaps on 2cb509. Per-people cuts: 20-33 s per L7 run (was 71-134 s). Drafts: gap cause, speed floor; scale draft rewritten (~20/~60/~150 human demes); gap-flicker and speed drafts done and removed.
- 2026-10-29: Fun lane 46: demes v0 built (planet/lineages/demes.py; `planet demes RUN`, run by output.save; globe layer "demes", workbench view "species + regional populations"). Review docs/review/lineages/demes.md: b69f51 60 living human demes, 2cb509 16 (a boat diaspora). Drafts: full presence per frame, gap flicker, scale (needs-decision), speed.
- 2026-10-28: Owner 2026-10-28: moved under the cultures epic PW-856 and into v2 (cultures are probably demes more than species); still the foundation of the language work under PW-767 and of the demo PW-986. Strongly tied to PW-902 (ranges follow ice-age sea level and land bridges).
- 2026-10-28: Created.
