---
id: PW-1275
title: "Density from a shared ladder: way of life x tech stage x land productivity, kind factor 0.8-1.2"
type: task
status: done
parent: null
milestone: v2
subsystem: timezoom
effort: l
impact: high
found_by: owner
blocked_by: []
relates: []
refs: [docs/review/peoples/density-ladder/ladder.md, docs/review/peoples/density-ladder/binford_by_npp.py, planet/lineages/samples/dnd.toml, planet/lineages/samples/techtree.toml, planet/lineages/spec.py::DEMOGRAPHY, planet/lineages/spec.py::WAYS, planet/lineages/landuse.py::shares, planet/lineages/prey.py::people_fields, planet/lineages/prey.py::PEOPLE_EXP, planet/lineages/history/growth.py::ERA_DENSITY, planet/lineages/history/growth.py::_set_era_density, planet/lineages/history/growth.py::_note_eras, planet/lineages/history/model.py, planet/lineages/history/peoples.py::population, planet/lineages/compose.py::compose, planet/lineages/techtree.py::density_x, planet/lineages/history/bands.py, viewer/lineages.html, tools/peoples_robust.py, docs/references/wishlist.md, "Binford 2001 Table 5.01 via D-PLACE dplace-dataset-binford (B008)", "Adams, White & Lenton 2004 Ecol Model 177:353 (Miami model)", "Kelly 2013 Lifeways 2nd ed Table 7-3", "Kroeber 1939 Table 9", "Pingali & Binswanger 1983 World Bank ARU 1 Table I (Boserup 1981 p. 23)", "Bourke & Harwood 2009 Food and Agriculture in PNG", "Zimmermann, Wendt, Frank & Hilpert 2009 PPS 75:1", "Broadberry, Campbell & van Leeuwen 2011 English medieval population", "Butzer 1976 Early Hydraulic Civilization Table 4", "Wang & Huang 1999 (abstract)", "Wilson 1986 ILCA RR14", "Kalff, Downing & Smith 1985 (abstract)", "Warrier et al. 2024 Ecol Soc 29(1):18", "Khazanov 1994 p. 31", "Clark 1999 UC Davis notes ch. 4", "Ramos et al. 2010 NPT 4(3)", "USDA FDC 168580, 169251", planet/lineages/ladder.py, "planet/lineages/ladder.py::Ladder", "planet/lineages/ladder.py::TABLE", "planet/lineages/history/model.py (self.kx, self.ladder)", "planet/lineages/history/growth.py (ladder refresh)", "planet/lineages/landuse.py::frame_inputs", "planet/lineages/spec.py::KIND_RANGE", "planet/lineages/run.py (schema ladder, kind_range)", "planet/lineages/crops.py::Crops.step", "planet/lineages/animals.py::Stock._propensity", "tools/peoples_robust.py::measure (density, ways)", "tests/test_lineages.py::test_people_density_reads_the_ladder", docs/review/peoples/density-ladder/build.md, docs/review/peoples/density-ladder/rungs.png, docs/review/peoples/density-ladder/shares_dnd.png, docs/review/peoples/density-ladder/shares_sm.png, "Binford 2001 Table 5.01 terrestrial bins (binford_by_npp.py, lane 137 rerun)"]
created: 2026-11-01
updated: 2026-11-02
---

## Description
In plain words: a people's density should come from what it does and knows, not who it is. Owner 2026-11-01: one shared ladder for every people (way of life x tech stage x land productivity); the per-people density field becomes a kind factor of 0.5-2x, filled for now only between 0.8 and 1.2 (slightly less for free-ranging kinds such as leonin and tabaxi); the workbench tooltip shows the ladder and the current rung, not a bare number. Ways of life shift with tech for part of a people, not all: some take up farming or herding and outgrow the rest, others stay foragers at low density to this day (any people, not just humans; e.g. leonin to husbandry, orcs part raiders part industry). Dwarves may exceed humans per km2 through an underground or vertical way of life (mushroom farming), a ladder entry, not the kind factor. Steps: source every rung (forager 0.35 Binford 2001 is sourced; gardening, plough farming, irrigation, herding, fishing need sources), show the owner the sourced ladder before building, then build and judge on tools/peoples_robust.py over many trees. Expect humans' share to fall sharply (the 10-12 vs 0.3 ceiling gap is the biggest cause).

## Updates
- 2026-11-02: Status todo -> done. Lanes 136/137 (merged b4bb9a81): density ladder built per PW-1350; D&D humans 56% -> 17% (median of 14 runs), people total 2.3-2.6x; every rung inside ladder.md's sourced range. Results docs/review/peoples/density-ladder/build.md.
- 2026-11-02: Lane 137 measured lane 136's build on the 48-run robust suite (results page at the top of
  docs/review/peoples/density-ladder/build.md): humans 56% -> 17% in D&D, people x2.3-2.6, rungs inside ladder.md's ranges; Q1 A kept
  as "per km2 filled" (no calibration); forager 0.036 confirmed on Binford's fit; 9 inbox drafts. Not merged yet.
- 2026-11-02: All ladder questions settled (PW-1350). Build: ladder with per-rung power (C), mean over land (Q1 A), land decides who farms (Q2 A), irrigation only where water reaches, dwarven holds = valleys' rung + trade placeholder, top at medieval peak; den peoples forager + capped raiding share (source first); remove groups (PW-1357); halflings/gnomes farm (PW-1351).
- 2026-11-02: Lane 130 (step 1): the sourced ladder is written up for the owner, docs/review/peoples/density-ladder/ladder.md (forager 0.01-0.4 from Binford's 339 via D-PLACE, rising ~x14 with NPP on the fit; fishers 0.3-2, rich coasts to ~9; gardening ~2-20; plough 2.5-14 early bronze age to ~35 medieval peak; irrigation 30-240 per watered km2; nomads ~0.3-2; holds = their valleys' rung plus trade, mushrooms add little), every number re-checked by a second agent (corrections listed on the page). Seven rulings needed before the build (inbox draft density-ladder-rulings). Found: halflings, gnomes and dwarves skip the era cap and the land factor (inbox draft halflings-farm-as-foragers-at-12).
- 2026-11-01: Owner 2026-11-01: agreed that a dwarven hold's density is limited by the food it grows or trades for (fungi need feedstock); no underdark (it would upset the tectonics).
- 2026-11-01: Created.
