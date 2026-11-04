---
id: PW-1286
title: The shelf builds out with a vertical front one cell wide (the clinoform fill has no foreset slope)
type: task
status: todo
parent: null
milestone: later
subsystem: surface
effort: m
impact: med
found_by: lane100
blocked_by: []
relates: [PW-950, PW-818]
refs: [planet/surface.py, paper:Mosher2017, docs/review/tectonics/margin/diagnosis.md, docs/review/tectonics/margin/diagnosis-foreset.md, docs/review/tectonics/margin/margindiag.py]
created: 2026-11-01
updated: 2026-11-03
---

## Description
In plain words: when rivers build a shelf out over deep water, the model fills the next deep cell right up to shelf
level in one go, so the front of the shelf is always a one-cell cliff, whatever the crust under it. Real shelf fronts
(clinoform foresets) slope at a few degrees, so the slope's width should be set by that angle, not by the cell size.

Where: `surface._offshore`, the brink branch (PW-818): a deep cell next to the shelf keeps the whole load up to
`(SHELF_TOP - elev) / iso`, i.e. it is filled toward -60 m with share 1.0. Lane 100 (PW-950 round 2) found that once
the necking zone thins a rifted margin's crust (`crust.necking`, `neck_km`), the margin's edge cells get filled with
several km of sediment by this rule (rifted-margin edge cells ~21 km of crust and sediment at about -900 m, then the
first oceanic cell at about -3800 m; L6 seed 2, 100-400 Myr), so the cliff moves out to the brink instead of going away.
Mosher et al. 2017 (Marine Geology 393: 245-259, p. 248; read by lane 100): upper-slope gradients on the NW Atlantic
margin "exceed 3 degrees, between 200 and 2000 m water depths"; graded slopes decay exponentially seaward (p. 247).

What I'd try: fill the brink cell only up to the level a foreset of slope theta (a few degrees, from that paper)
below the shelf edge allows at that cell's distance (`SHELF_TOP - tan(theta) * d_km * 1000`), passing the rest on; the
shelf then progrades as a sloping wedge whose width is set in km, the same at every grid level. Judge with
`docs/review/tectonics/margin/margindiag.py` (near1/near2, the 200-3000 m share, coast-to-3000 m) and the hard bars.
- [ ] steepest-neighbour gradient on slope cells (-500..-2500 m) at L7/L8 within a factor ~2 of Earth on the same grid
- [ ] no hard-bar failures on the paired judge

## Update (lane 100c, 2026-11-01)
The round-3 diagnosis (docs/review/tectonics/margin/diagnosis-foreset.md) found a one-cell front about right at L6/L7,
since a 3-degree front is about one cell wide there. So lane 100c built sea-floor creep of the sediment cover instead
(`slope_k`, surface._creep; off by default). On the 36-draw paired L6 judge (with necking and rise) it moves every
margin number most of the way to Earth: coast cells with >3 km of water in the next cell 22.8% -> 6.5% (Earth 3.5%),
within 2 cells 59.9% -> 25.2% (Earth 22%), 200-3000 m share of the ocean 12.9% -> 20.0% (Earth 19.6%), coast to
3000 m 240 -> 437 km (Earth 602). The shelf share doesn't move (2.6%, Earth 6.2%). A foreset-angle cap (candidate 1)
is still open for L8 only.

## Updates
- 2026-11-03: Triage 11-03: v2 -> later: surface/resources refinement; not needed for the culinary goal
- 2026-11-01: refs enriched (lane 113): code functions, margin notes and harnesses, papers by key.
- 2026-11-01: Created from inbox draft draft-clinoform-front-has-no-foreset-slope.md (found by lane100).
