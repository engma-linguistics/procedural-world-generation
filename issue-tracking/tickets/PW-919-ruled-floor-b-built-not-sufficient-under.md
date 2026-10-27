---
id: PW-919
title: "RULED (floor B built, not sufficient): under the species-area origin draw (PW-888) some peoples now found on small landmasses and start thin: humans at 100 kyr ago, elves on 1df1c3"
type: task
status: todo
parent: PW-692
milestone: null
subsystem: timezoom
effort: s
impact: med
found_by: fun-lane-30
blocked_by: []
relates: [PW-888, PW-885]
refs: [planet/lineages/history.py, "world 2a7385", "world 1df1c3", "dnd tries 7000-7007"]
created: 2026-10-27
updated: 2026-10-27
---

## Description
PW-888 draws each origin's landmass with probability (habitable cells)^0.3 (`history.SPECIES_AREA_Z`), so small landmasses and islands get a share; the founders must be viable (`tree.viable_pop`). Over 8 tries (7000-7007, dnd) this spreads the peoples, but some founders land on a small place and start thin:
- 2a7385, humans at 100 kyr ago: 22.1k, 5.3k, 25.6k, 15.9k, 4.2k, 0.3k, 2.9k, 3.5k cells (before: 3.6k, 24.5k, 18.6k, 16.6k, 17.7k, 3.5k, 3.5k, 24.4k); at the present 28.1k, 13.2k, 30.2k, 29.0k, 5.5k, 15.1k, 14.0k, 9.8k (before 8.7k, 30.5k, 29.8k, 29.4k, 26.7k, 7.2k, 6.7k, 32.6k). Mean at 100 kyr ago falls from 14.0k to 10.0k, the present mean from 21.5k to 18.1k (the old small-continent tries 7000, 7005 and 7006 do better now, the others worse).
- 1df1c3: humans at 100 kyr ago 3, 3 and 32 cells on tries 7001, 7006 and 7004 (2.7-6.7k on all eight before), present 12-26k (13-23k before); elves under 500 cells on 7004 (176) and 7007 (186): 6 of 8 at >= 500 (8 of 8 before).
Likely cause: a founder population at the viability floor (500 people) on a landmass of a few hundred km2 passes the filter but cannot grow. Options: A. accept (isolation, island peoples; the Holocene farmers still reach 12k+). B. raise the founder floor to a multiple of `viable_pop` (say 10x) so a landmass must hold a lasting population. C. weight the draw by (habitable area)^z only above a minimum landmass size and give smaller ones a fixed small share. Lean: B, behind the same 8-try sweep on both worlds.
- [ ] humans >= 1k cells at 100 kyr ago and elves >= 500 on 7 of 8 tries on both 2a7385 and 1df1c3, with no landmass under ~15% of the land holding most peoples

## Ruling and result (fun-lane-30, second pass)
RULED by the coordinator: option B, a landmass takes an origin only if it can carry a long-term minimum viable population, a multiple of `tree.viable_pop` derived from Traill et al. 2007 (median vertebrate MVP ~4000) over Frankham 2014's 500: `history.ORIGIN_MVP_MULT = 8`. Built and re-measured over 8 tries on 2a7385 and 1df1c3 (dnd): the floor alone does NOT meet the targets.
- No majority landmass holds (kept): top share 50-71% on 2a7385 (the 70% landmass), 29-39% on 1df1c3.
- Elves >= 500 cells: 4 of 8 on each world (before the floor: 8 of 8 on 2a7385, 6 of 8 on 1df1c3; before PW-888: 8/8 on both). Half-elves present: 8 of 8 on 2a7385, 6 of 8 on 1df1c3 (0 cells on 7005, 7006).
- Humans at 100 kyr ago under 1k cells: 2a7385 7004 (84), 7005 (607), 7006 (103); 1df1c3 7004 (32), 7006 (3).
Cause (probe on 2a7385 7004 and 7006): the founders are not rare big-landmass accidents but 1-2 cell places. A cell at L7 is ~3000 km2, so 4000 people fit on one cell at a density of 1.3 per km2 and the floor in people never bites: hominid split onto a 2-cell and a 108-cell landmass, archaic humans onto 88 and 2 cells, humans onto 1 and 2 cells ("across the sea from the parent's range", the PW-888 split rule). The elves on those seeds arrive on the big landmass (41.7k cells) by habitat, so their drop is downstream (the humans/hosts are elsewhere, fewer half-elf meetings), not their own origin.
What would act on it (not tuned): (1) a landmass floor in cells, not people (a range of tens of cells, e.g. the REFUGE_MKM2 0.5 Mkm2 already used for refuges), (2) make the across-the-sea split founding follow the crossing law (probability ~ exp(-gap / L) of the parent's coast, `crossing.hop`) instead of every landmass at 0.6 K, so isolated 1-2 cell places far from the parent are rare, (3) both. Needs the owner/coordinator's call on (1)'s size.

## Re-measurement (fun-lane-30, finishing pass)
Full `uv run pytest -q`: 696 passed, 1 skipped. Re-ran the 8-try sweep (dnd, tries 7000-7007) with and without `SPECIES_AREA_Z` on both worlds; the numbers above reproduce (before = z 0 matches the fl29 report: 2a7385 humans 14.0k at 100 kyr ago, 21.5k now). With the floor (z 0.3): elves >= 500 on 4/8 (2a7385) and 5/8 (1df1c3); half-elves present 8/8 and 6/8; humans under 1k at 100 kyr ago on 3/8 and 2/8. Hobgoblins on 2a7385 7000/7005/7006 recover (82/92/141 cells before; 2070/13246/13925 after), so PW-889 is helped. Peoples by origin landmass on 2a7385: the 70% continent 61% -> 49%, the 19% one 32% -> 20%. The targets for elves and humans remain missed; the unresolved cause is the cell-sized founding places (see above), not the floor's constant.

## Third pass (fun-lane-30): sea-founding follows the crossing law; derived area floor does not bite; needs a call
Built: a split's founders carried over the sea now land with the parent's crossing chances (`crossing.modes`, rate x exp(-gap/L) from the parent's coast, relative to gap 0; the landmass draw is weighted by its best landing). No new constant. Full pytest 696 passed.
Floor from density x MVP: ORIGIN_MVP_MULT x viable_pop / (density x 0.5) = 4000 / (2 x 0.5) km2 ~ 1.3 cells at the default density, so a floor derived this way cannot exclude a 1-2 cell place; it is a census MVP for ~40 generations (Traill 2007), while a daughter must persist 10^2-10^6 kyr. A persistence-scaled floor (MVP growing with the horizon, Lande 1993 environmental stochasticity; needs a generation time per people and an exponent) would bite, but both are new constants: owner's call, not tuned here.
Result over 8 rolls on 2a7385 and 1df1c3 (dnd, 7000-7007): humans at 3 cells at 100 kyr ago still on 2a7385 7004 (the archaic-human parent already on a 2-cell place) and 1df1c3 7006 (human split carried to a 3-cell islet close to the parent coast, then boxed in by the incumbent parent). Hard failure (< 100 cells) 4/16 before -> 2/16. Only these two worlds were measured (not six).

## Fourth pass (fun-lane-30): retimed trees, revised criteria (judged at the present), persistence-horizon floor
Owner rulings applied first: stems are the peoples' last common ancestor (roots <= 20 Myr, named peoples <= ~3 Myr, dragons an ur-dragon splitting at 19.5 Myr with chromatic and metallic splits at 2.5 Myr and the colours as their groups at 750 kyr) in dnd.toml and seven_meals.toml; [[interfertile]] T3 rows keep lizardfolk/tortle/troglodyte and antelope-kin/cervid-kin apart. New pairs below T3 from the retiming: stem x its own children (reptilian x lizardfolk/tortle/troglodyte; ruminant x antelope-kin/cervid-kin, seven_meals; reptilian x lizardfolk/tortle) and the new dragon lines (draconic, chromatic, metallic, kobold, dragonborn pairwise T2).
Measured 6 planets (2a7385, 1df1c3, e71172, 6909cb, a12762, 067778) x 4 rolls (7000-7003, dnd). "Core" = human, elf, dwarf, halfling, gnome, orc, goblin, hobgoblin, bugbear, tabaxi, leonin, kobold, tortle, lizardfolk, dragonborn, aarakocra. Rolls (of 24) with a core people under 100 cells:
- 0e8ced9 code with the retimed trees: at ~100 kyr ago 15, at the present 17 (elves >= 300 cells 18/24; hybrids: no roll with human/elf overlap lacking half-elves; hobgoblins under 300 cells on 3). Present remnants are mostly peoples squeezed to tens of cells on the big landmass (goblins, dwarves, halflings, gnomes, tabaxi, leonin).
- With the persistence-horizon floor (history.origin_mvp, `generation_yr`, c = 1): 100 kyr ago 7, present 10 (elves >= 300: 17/24; hybrid absences 0; hobgoblins under 300 on 1; every core people >= 300 on 3/24). The floor helps (17 -> 10) but does not reach zero.
- Deep-time populations (peak before 20 kyr ago): humans are the peak people on 22/24 rolls; the exceptions are kenku at 1.8x and 2.5x humans before, 3.0x with the floor on one roll, dragonborn 1.2x: none near an order of magnitude.
Remaining present remnants (10 rolls) are gnomes, halflings, dwarves, elves arriving late, goblins: small arrival or niche peoples, i.e. competition and range, not founding size. Needs a ruling on whether small-by-design peoples (gnomes, halflings, tabaxi) count toward "every people >= 300 cells".
Assumptions to review: exponent c = 1 (Lande 1993; Foley 1994 fits not checked) and the generation times (default 25 y, goblinoid 15, dwarf/gnome 40, elf 50): a simple per-people number; life-history stats are PW-917 (v2).

## Fifth pass (fun-lane-30): why the squeezed peoples end small; three mechanisms tried, none merged; origin share
Full `uv run pytest -q` on b78608b: 696 passed, 1 skipped. Criteria as ruled: "main" = human, elf, dwarf, halfling, gnome, half-elf, half-orc, dragonborn, tiefling, orc, goblin (hard failure: < 100 cells at the present); 300 cells per people on ~70% of rolls. 6 planets x 4 rolls (dnd 7000-7003), judged at the present.
Before (b78608b), rolls with a main people < 100 cells: 2a7385 1/4, 1df1c3 1/4, e71172 0/4, 6909cb 3/4, a12762 2/4, 067778 3/4 (10/24). Per-people pass rate (>= 300 cells): human, dragonborn, half-orc, orc, aarakocra, kenku, lizardfolk 24/24; goblin, hobgoblin, leonin, tabaxi, tortle, storm giant 23/24; dwarf, halfling 21/24; kobold 20/24; elf, half-elf, bugbear 17/24; triton 12/24; gnome, firbolg 11/24; goliath 9/24; frost giant, sea elf 8/24; cloud giant, hill giant 6/24; drow, fire giant 1/24. Main peoples under the 70% bar: elf and half-elf (71%, at the bar), gnome (46%).
Diagnosis (instrumented at the present on 2a7385 7002/7003, 1df1c3 7002, e71172 7001):
- The sub-300 cluster at 150-165 cells (giants, drow, firbolg, bugbear, sea elves, tritons) is the refuge floor: displacement slows to 0 at REFUGE_MKM2 = 0.5 Mkm2 = 160 cells at L7. These peoples were squeezed down to it, not founded small.
- It is not a shortage of habitat: each has thousands of cells with K >= 0.5, hundreds to thousands where its K beats every holder's by 1.3x, and room >= EST on 20-80% of them. But that room is far away. Room within 3 rings of the range is ~0 (dwarves 0 of 2590 room cells; gnomes 0 of 6952; drow 0 of 1247; hill giants 8 of 532), and most is more than 60 rings off: other mountain ranges and forests across country the people cannot hold (K < 0.3 cuts the pressure; climbing costs it). One spread of 40 passes from the full habitat (not the thinned presence) reaches 0-20 new cells for dwarves, gnomes, drow, giants. So the limit is dispersal between habitat patches, not the local contest.
- The main-people hard failures split two ways: arrivals or late splits onto small land (gnome on a 26-cell and a 12-cell island, 1df1c3 gnome on a 2.4k-cell landmass at 86 cells), and arrivals pressed into a pocket of the big continent (elves 1-5 cells on 2a7385 7002, 067778 7003; half-elves fail with them).
- Frontier invasion (PW-887), incumbency and density: no sign that they cause it. Room next to the range is filled, and the density push is the same as before.
Tried, measured over the same 24 rolls, not merged (no change beyond roll noise):
- r1, settle with the habitat's pressure where room exists in held country (the PW-683 pioneer spread, no longer only into empty land): main < 100 on 1/1/0/3/4/2 rolls; per-people no better (cloud giant 6 -> 3, goliath 9 -> 4, triton 12 -> 19).
- r2, r1 plus a split's founders carried over the sea over the parent's whole life (reach = 1 - exp(-T x sum rate x exp(-gap/L)), T = the parent's age), "daughters disperse before splitting": identical to r1 within a percent. At gaps of 1000+ km the raft law (3e-4 /kyr, L 150 km) gives ~0 crossings in 20 Myr either way.
- r3, home ground: a rival's closed-country (territorial) term on a cell x min(1, its K / one's own), so the better suited holds its own ground: main < 100 on 1/1/0/3/3/2 rolls (9/24 vs 10/24); goliath 9 -> 15, drow 1 -> 2, cloud giant 6 -> 2, gnome 11 -> 9: reshuffles rolls, no net gain.
Origin share (top origin landmass, mean of 4 rolls, vs its share of the land): 2a7385 82% on 70%, 1df1c3 55% on 32%, e71172 74% on 48%, 6909cb 73% on 55%, a12762 78% on 82%, 067778 88% on 76%. Worse than main on 2a7385 (61% on 70% before PW-888, 49% with z 0.3 on the old trees). Cause: the reptilian root moved from 320 Myr to 20 Myr (and its lines from 100-250 Myr to <= 3 Myr), so the reptile peoples no longer had hundreds of Myr of drift and rafting to spread. Every people now comes from 3 roots plus the arrivals, and under the existing crossing law a 20 Myr tree does not cross 1000-2300 km seas. r2 is the "disperse before splitting" fix through that law, and it does not move the share. Lowering the share needs a ruling, not a constant: either accept phylogenetic clustering (descendants near their ancestors) as the 20 Myr consequence, or let the roots draw separate landmasses.
Leftovers: draft-squeezed-peoples-dispersal-limited.md (needs-decision).

## Updates
- 2026-10-27: Created from inbox draft draft-small-landmass-founders-start-thin.md (found by fun-lane-30).
