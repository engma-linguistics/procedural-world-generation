# Rivers, lakes and deltas: findings (2026-10-13)

*From an investigation of world a434c5 (run d05a1e, hothouse, t = 460 Myr), prompted by the owner's questions. Nothing here is implemented yet; it's for discussion.*

The pictures referred to below were in the session scratch dir: `place2_lake_section.png`, `place2_coarse.png`, `place1_zoom_fine.png` and `bigmouth_zoom.png`.

## Two sets of numbers for the same cell
The run viewer and the sliced world (and so every zoom) disagree.

For example, place 1:

| | Elevation | Rain | Climate |
|---|---|---|---|
| Run viewer | 39 m | 3463 mm/yr | Am |
| Sliced world and zoom | 16 m | 1053 mm/yr | (recomputed) |

There are two reasons:
- **The run's climate is out of date.** It is updated only every 8 Myr (`climate_every`), so at t = 460 the rain was computed on the ~456 Myr geography. Plates move about 300 km in 4 Myr.
- **The world reshapes the land before computing climate and rivers.** `_world` adds ±180 m of texture and 12 more erosion passes first.

Rain is very sensitive to where the coast sits, so the two disagree a lot.

## How water is modelled
- **Globe:** priority-flood routing, with exactly one downstream cell each. Every pit is filled up to its spill level. Only a yes/no lake mask is stored; the water level and depth are thrown away (`hydrology.py:54`).
- **No evaporation anywhere.** Runoff = 100% of rain, and lakes lose nothing. Discharges are 2–5× too high: the place-2 lake river carries 189,000 m³/s, almost the Amazon's 209,000. Closed salt lakes can never form.
- **Zoom lakes:**
  - The lake outline comes from the coarse mask.
  - The surface is set to the mean *bed* + 3 m, not the spill level (`zoom.py:464`).
  - The bed is `level − 2 − 40·shore²`, which saturates at 42 m about 8 km from shore (`zoom.py:470`).
  - Lakes are treated as **outlets**, i.e. sinks where water leaves the map (`zoom.py:471`).
- **Sediment** exists only inside the run. Rivers dump it at the mouth, it spreads by diffusion, and isostasy lifts the pile. The zoom models no sediment.

## Place 2: the lake (~430,000 km², an open lake that overflows)
1. **"The giant river doesn't feed the lake."** On the globe, the giant river *is* the lake's outlet. In the zoom, lakes are sinks, so the lake's inflow vanishes: the river carries 33,000 m³/s instead of 127,000–189,000, and there is no outlet channel. **Artifact.**
2. **"Uniformly shallow."** About 90% of the zoomed lake is exactly 42 m deep, because of the hard-coded bed profile. A big, shallow lake on an old shield is realistic (Lake Victoria: mean 40 m, max 84 m). What's unrealistic is the cliff-then-flat profile. **Worse:** the water surface is set too low (258 m instead of the 284 m spill level), and half the land within 6 km of shore is lower than the water, so nothing holds the lake in.
3. **"Little rain feeding the rivers."** The lake cell itself is dry, but its catchment averages 1500 mm/yr, with a 2000–3500 mm belt east and south. With no evaporation, rivers look too big for the rain shown. The rain field is also patchy from cell to cell on flat ground: neighbouring cells differ by a median 1.5× here, versus 1.16× globally. That is a climate.py issue.

## Place 1 and deltas
- **The 11.6 km of sediment at 39 m elevation is realistic.** It is the globe-scale delta; the Niger delta has ~12 km and the Bengal basin 16–20 km. **But elsewhere it's too much:** up to 33 km, against Earth's maximum of ~20–22 km. Nothing limits the pile (no compaction, offshore transport or slumping).
- **Distributaries can't happen.** Both the globe and the zoom route each cell or pixel to a single downstream neighbour, so rivers never split.
- **Delta land does build out, crudely, at the globe scale.** Sediment plus isostasy pushes the coast out 100–200 km at the biggest mouth (2.1°N, 157.5°E, 246,000 m³/s).
- **The zoom adds nothing at the coast.** Coastlines come from noise, with 100–180 m hills right down to the shore. The river sometimes ends in an embayment, the opposite of a delta.
- **The place-2 river's mouth (10.3°N, 77.3°W) has no delta because that coast is brand new.** A rift opened there within the last 4 Myr. A continent's drainage switching to it in a single step is abrupt.

## Candidate fixes, best value first
1. **Zoom lakes pass water through:** re-inject each lake's inflow at its spill point. Low effort.
2. **Store lake level and depth in the world:** the zoom then uses the true spill level, and the shores sit above the water. Low effort.
3. **Lake bed shape from the globe-scale fill depth:** deepening over tens of km, with no fixed 42 m. Low–medium effort.
4. **Zoom delta plain at big mouths:** damp the noise, flatten land to a few metres, and push a lobe out using the sediment cover. Low effort, big visual payoff.
5. **Zoom distributaries:** split the channel below a delta apex (where the plain starts) into 2–6 branches that fan to the coast. Alternatively, let water share among downhill neighbours on low, flat land near the coast. Medium effort.
6. **Evaporation:** runoff = rain × a ratio set by temperature and dryness, lakes lose water to evaporation, and closed salt lakes become possible. This touches the run and the world. Medium effort.
7. **Globe sediment:** deposit near shore first so the coast advances, send the excess to deep water, and cap or compact piles. This changes run behaviour. Medium effort.
8. **Run/world climate mismatch:** show the climate's age in the viewer, or recompute it.
9. **Drainage memory:** so rivers don't switch mouths in a single step.

## Status (branch `water`, 2026-10-13)
- **Done: 6 (evaporation).** `climate.water_balance`: potential evaporation from sunshine and temperature (Oudin), actual evaporation from the Budyko curve per half-year, runoff = rain − evaporation (0.40 of the rain on Earth's land). Rivers in the run and the worlds carry runoff. Lakes evaporate (`kernels.lakes`): closed salt lakes and salt pans form. On Earth's geography the Caspian, Aral, Balkhash, Tarim, Okavango and Altiplano basins come out closed, and 21% of the land drains to closed basins (Earth ~18%). `tools/earth_check.py` reports river discharges.
- **Done: 2 (lake level in the world).** World layers `lake_level` (m, same datum as `elevation`; equal to it where there's no lake) and `lake_kind` (0 none, 1 open, 2 closed, 3 salt pan).
- **Done, partly: 7 (globe sediment).** Near shore first (delta tops fill to +2 m on the shelf, so coasts build out), the excess spreads over ~1000 km of deep sea floor, closed lakes spread their load over their floor, and sediment buried deeper than 18 km becomes metamorphic basement. Piles now top out at ~18 km. The model still treats sediment as crust-density rock, so filling deep water takes ~5× its depth in sediment (Earth: ~3×).
- **Not done: 9 (drainage memory).** A memory of old channels would have to move with the plates (the per-cell arrays are in the world frame, and plates move ~1 cell per step). The real damping is mostly rift-flank uplift, which raises a divide next to a new rift. That's a tectonics change.
- **Found:** generated worlds have almost no closed basins after ~150 Myr (0–2% of the land drains inland). Sediment and erosion fill every hollow, and nothing in the tectonics makes new interior sag basins.
