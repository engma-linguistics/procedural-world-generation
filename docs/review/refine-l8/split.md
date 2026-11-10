# The split history on a refined L8 world (PW-1265, lane 267)

Daniel's 11-10 split: tectonics, ice ages, evolution, dispersal and languages stay on L7; the settled history (towns, states,
trade, war) runs on the finished world refined to L8. This note has the measured L7 and all-L8 tries (lane 266's first path),
the split's design, its conservation test and the split run, all on Earth-like A (world 899985, time zoom fc5311, dnd tree,
one try, seed 7) and its refined L8 world 5d09cc (lane 266 scratch root).

## 1. Measured: the whole history on L7 vs on L8 (lane 266's path)

MEASURE_TABLE

## 2. The cut

**The cut is the earliest drawn date of a first cultivation among the try's crops** (`history.handover.cut_kyr`: the largest
`animals.Stock.d0` over the crops this world has). Why there:
- Every settled mechanic in the code needs farmers. A crop can only be tamed at a step with `step.ago <= d0`
  (`animals.Stock.step`); a people's era leaves "forager" only once it takes a crop up (`history.growth._note_eras`); the
  live polities seat on sedentary heads, which are heads x the farm share of a non-forager people (`polity_live._heads`), and
  a dragon realm takes tribute only from cells with sedentary heads (`SEDENTARY_MIN`); the settlement ledger, trade and wars
  are made from the stored frames after the run, so they read the settled window's frames, which are all after the cut.
  So nothing a town, state, trade route or war reads exists before the cut, and everything it reads after it is on L8.
- The date is drawn when the History is made (Stock.__init__), so the cut is known before the run starts: no look-ahead, no
  second pass, the same for every grid.
- On Earth-like A seed 7 the cut is CUT_KYR kyr ago (pulses' drawn date; wheat 11.2, the dog at 17.7 is a herd animal and
  does not count). Of the run's STEPS_ALL steps, STEPS_L8 run on L8.
- A tree without crops never farms: the hand-over is then at the last step (the present), so the map is still on the
  world's grid. (A world whose peoples herd but never farm has no settled window in this model.)

## 3. The hand-over (`planet/lineages/history/handover.py`)

The run builds two recent passes: the coarse one on the world the refined world was made from (`meta.refined_from`, here
899985, with its own goods, rain, NPP and rivers) and the fine one on the refined world (lane 266's `recent.Pass` on the
world's grid, the time zoom's frames prolonged by `recent.finer`, the full climates on the zoom's L7 grid). Up to the cut
the History is exactly the L7 history of 899985 (same steps, same draws: the test checks the stored frames cell for cell). At
the first step at or after the cut, `hand_over` moves the History's state onto the fine grid and swaps in the fine Pass, the
fine goods and the fine world's steps for the rest of the run; the frames stored so far are put on the fine grid (each fine
cell shows its first parent's value: the coarse past as it was).

The grids nest (L8 = the L7 cells, same index, plus a cell on each L7 edge's midpoint; `nest.step`'s two parents per fine
cell). Each field by its kind:

| kind | rule | fields |
|---|---|---|
| a category | the fine cell's first parent (a kept cell: itself) | who leads a cell, contact holders, crop/animal routes, rung, polity owner, masks (`_last_held`, `_linger`), counts per cell |
| a quantity per area | the mean of the two parents (a kept cell keeps its own) | habitat shares (`_Kmat`, `_K_now`), fit, learned acceptance (`_Lm`, the learned country), a crop's or animal's knowledge (`rd`), density map (`_dmap`), contact presence, the brakes' K0 |
| a people's numbers | split by area, conserved exactly (below) | `h.p` for every people and megafauna line; overlays (a share of their hosts) take the mean |
| made again from the fine world | rebuilt, not carried | goods, the ladder's land (NPP, grazing, fish, fertile, ore, dens, water), the prey and sea-food fields, the landmasses (`Crossings`), the polities' neighbour and two-ring tables and site layers, cell sizes |
| landmass numbers in the record | renumbered: each coarse landmass to the fine landmass most of its cells carry | crossings reached, animals' and crops' landings, homelands, tamings |
| per-step caches | dropped, remade at the next step | the frontier cache, the present-epoch cache, overkill memo, density memo |

What is not per cell (the demes and cultures are made after the run; tech, attitudes, contacts' pair series, events,
tracks, eras, farm shares, every line's own numbers) carries over unchanged. Live polities (off by default, PW-1434) are
rebuilt on the fine grid with their non-cell state carried; at the cut none is seated yet, since they need farmers.

**Population conservation.** A people's heads per cell are presence (>= EST) x density x the grid's cell area (the history
counts every cell of a grid as equal: `geo.cell_area_km2`). `heads_split` shares each coarse cell's heads out by area in nest's
full weighting: the kept cell takes two half-slots, each midpoint round it one half-slot (a hexagon's heads: 1/4 to its own
fine cell, 1/8 to each of its six midpoints; a pentagon's 2/7 and 1/7). Each fine cell's presence is its heads over the mean of
its parents' densities and the fine cell area. A share that would fall under EST (a range edge's midpoint) would be counted as
nobody, so those heads go back to the parent's own fine cell. Totals are kept exactly per line:
`tests/test_lineages_split.py::test_heads_split_conserves_every_people_and_leaves_none_under_the_floor` (random presences,
densities and a thin line on L3 -> L4, rtol 1e-12), and the run records `meta.handover.people_before` / `people_after`.
The next step is the fine world's own: K, the ladder's density and the megafauna's local density are made on the fine land,
so cells the finer coast puts under the sea lose their people then, by the model, not by the move.

Equal levels: none of this runs (`run.run` only builds the fine pass when `meta.refined_from` names a world on a coarser
grid; `--no-split` keeps lane 266's all-on-the-world path).

## 4. The split run on 5d09cc

SPLIT_RESULTS

## 5. What it does not do (drafts)

DRAFTS
