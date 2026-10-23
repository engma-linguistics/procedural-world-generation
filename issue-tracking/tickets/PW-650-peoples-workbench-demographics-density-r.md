---
id: PW-650
title: "Peoples workbench: demographics (density, roaming area), explorers vs. insular peoples, a share of each people taking to the sea; peoples as their own multi-tab app"
type: story
status: done
parent: PW-103
milestone: v2
subsystem: viewer
effort: xl
impact: high
found_by: daniel
blocked_by: []
relates: [PW-635]
refs: []
created: 2026-10-23
updated: 2026-10-23
---

## Description
Owner (2026-10-24): giants should be far fewer in number with larger roaming areas; some peoples insular, some exploratory; landmasses with few or no peoples should be found by the more exploratory or seafaring peoples; not 'no dwarves sail the seas' but a smaller proportion of them would. Model side: per-people density (people per km2 / range per band), growth or expansion rate, exploration propensity and a seafaring share (a fraction of a people's frontier that crosses water, scaled by trait), insularity (resistance to mixing and to leaving home). Owner: this is getting beyond the genetic-tree approach; peoples likely need to be their own multi-tab / multi-screen thing (tree, demographics and traits, places and land use, wishes, results and stories). Next lineages lane after the viewer entry (peoples discoverable) and the preset changes (felines, giants, stems, volcanic and rolling-hills goods) merge.

## Updates
- 2026-10-23: Status todo -> done. Merged: density/roaming, explore, sea share, insularity per people (trait defaults); population and landmass discovery outputs; the five-tab workbench at viewer/lineages.html; preset knobs (giants 0.005-0.01/km2, humans 10). PW-655 resolved by density. Groups designed only: PW-665.
- 2026-10-23: Created.
- 2026-10-23: Workbench lane built the model and the page (docs/proposals/lineages.md, "Workbench lane").
  - Model: four knobs per people, each given in the spec or derived from its traits:
    - `density` (or `band_km2`): sets the numbers, and a viable population of 500 per separate patch;
    - `explore`: pushing into marginal land, and long crossings;
    - `sea_share`: boats, from 6 kyr ago, ~share × 1.7 /kyr with a reach of 300–1500 km. Replaces the `seafaring` trait's knob;
    - `insularity`: mixing and leaving home. Replaces the `insular` / `cosmopolitan` mix knob.

    A mild density push acts on competition. Outputs: populations per people, per landmass and per frame, and per landmass who found it first (`discovered`, `settled_by`, `arrivals`).
  - Preset: giants at 0.005–0.01 /km², insular, pull 0.7 not strict (PW-655 option C); humans and halflings 10–12 /km²; elves explore 0.8; dwarves sea share 0.05; storm giants 0.5; tortles, tritons and sea elves 0.8–0.9.
  - Page: `viewer/lineages.html`, same URL, with tabs Tree & timeline, Peoples, Places & land use, Wishes, Results. Screenshots: `docs/review/lineages/workbench-*.png`.
  - Runs, L7, best of 2, before → after:
    - 1df1c3 (e8cc18 → 37e9da): wish 0.775 → 0.72; humans 19.5 → 34.4 Mkm², 170 M people.
      - Giants: hill 0.47 → 0.35 Mkm² (1,251), cloud 0.97 → 0.40 (819), storm 0.13 → 0.25 (233), frost 3.68 → 4.68 (8,731), fire 0.01 → 0.02 (53). Each now holds one land.
    - 3e9e7d (before the lane → 33b1c3): wish 0.593 → 0.687; humans 20.1 → 30.2 Mkm², 116 M people.
      - Giants: hill 2.83 Mkm² in 69 patches → 0.45 in 1 (597), cloud 0.01 → 0.17 (560), storm 0.10 in 9 patches → 0.17 in 1 (247), frost 4.19 → 4.27 (13,915), fire 0.18 → 0.04 (54).
      - The empty 7.3 Mkm² continent at 64°N: held 0.02 → 0.04. Sea elves sailed there 4.8 kyr ago over 4,450 km. In one earlier try it was held 0.33.
      - The 0.54 Mkm² large island at 5°N: 0.0 → 1.0.
  - Drafts: draft-peoples-density-push (needs-decision), draft-peoples-fire-giants-refuge.
