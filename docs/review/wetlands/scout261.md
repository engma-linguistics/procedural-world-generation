# PW-831 scout 261, pass 2 (of 3): the Niger dry-hollow fix (merge) and overbank wetlands (miss: park)

Branch `worktree-agent-ac502a6f660c0286b` (pass 1 `scout260.md` + main c781c395). Scripts: `scout261/`. Scratch (s261) =
`/tmp/claude-1000/-data-personal-repos-procedural-world-generation/43861907-2d55-4b88-96fd-7cf556b60255/scratchpad/s261/`
(deleted after the pass; nothing written to runs/, worlds/ or data/earth).

## In plain words
1. **The Niger now reaches the sea.** The dry-catchment rule (PW-054) closed the inner Niger delta because, on the
   ~55 km cell means, the delta sits in a 20 m deep, 108,000 km2 hollow behind the Tosaye sill. The finer river data
   the Earth world already carries says the Niger's real channel runs straight through that sill (273 m at
   Ke-Macina down to 252 m under the sill, whose cell mean is 284 m): the hollow is an artefact of averaging a gorge
   narrower than a cell. The rule now ignores a hollow that an already-known channel drains: the finer data's river
   heights on Earth, and in generated runs the valleys rivers cut before (the run's valley memory, PW-300). Nothing
   about how much water arrives changes the answer here: even the whole Niger (5,400 m3/s arriving under the
   model's wet climate) could not fill that hollow against the open-water evaporation over it (9,600 m3/s), so a
   rule reading the inflow would still close it.
2. **Wetland evaporation: second miss, recommend park.** Pass 2's mechanism (a river's flood spills over its banks
   where its channel, sized by measured river geometry, can't carry it on a low gradient; the spill evaporates on
   the plain) leaves the Sudd untouched (the model's White Nile falls 1e-4 to 2e-4 there, steeper than the 4e-5 a
   channel of that size needs, and its flood is damped to 1.1x by Lake Victoria), barely touches the Okavango
   (-5%), and either kills the Niger in the Sahel (observed rain) or takes 5% (model climate) where reality is
   -40%. The real swamps owe their losses to channels choked by vegetation and a sharp seasonal pulse, which
   river-geometry averages don't carry. The code is removed from the branch; it is kept as `scout261/overbank.patch`.

## 1. Niger fix (`planet/hydrology.py`: `_dry_hollows`' `chan`, built in `lakes()`)
Diagnosis (`scout261/diag_hollow.py`, `diag_niger.py`; Earth L7, the Earth world's inputs as built):
| hollow kept by main | cells | area km2 | depth m | catchment P/PET | inflow m3/s | open-water deficit over the whole hollow m3/s | lake cells at balance |
|---|---|---|---|---|---|---|---|
| inner Niger delta, model climate | 36 | 107,929 | 20 | 0.51 | 5,436 | 9,643 | 20 |
| same, observed (GPCC) rain | 36 | 107,929 | 20 | 0.49 | 1,846 | 8,867 | 7 |
The literal "inflow against the open-water evaporation over the hollow at balance" test keeps it closed under both
climates (inflow 0.56 / 0.21 of the hollow's evaporation), and a runoff-weighted aridity (the draft's idea) would
reopen it only by also reopening Okavango-type terminal swamps fed from wet highlands. Along the course
(`diag_niger.py`, observed rain), the Earth outlet heights (`earth_data.earth_outlets`) fall monotonically
273 -> 266 -> 258 ... 252 (the Tosaye sill cell, mean 284.1 m) -> 245 -> ... -> 15 m at the coast: by the finer data
there is no hollow.

Code: `lakes()` lowers the ground to the channels it already knows (`outlet` where below the cell mean; `valley`,
the run's memory of the valleys rivers cut, PW-300) into `chan`, and `_dry_hollows` drops a candidate hollow that
`chan` drains (its priority-flood fill on `chan` is not above `chan`). A filter only: it can never add a kept
hollow. One extra priority flood per `lakes()` call (keep is still worked out once per call).

Earth (Earth world's hydrology as built: outlet + closed + valley None; `scout261/earth_wet.py`; main = 56bb8692's rule
on the same inputs):
| | main | fix | rule off |
|---|---|---|---|
| L7 model climate: Niger | ends in a sink at 14.5 N, 4.3 W (2,962 m3/s arriving) | Ke-Macina 3,218, Dire 3,219, Timbuktu 3,219, reaches the sea | same as fix |
| L7 observed rain: Niger | ends at 15.0 N (434 m3/s left) | Ke-Macina 676, Dire 677, reaches the sea | same as fix |
| L7 inland % (model / obs rain) | 21.8 / 22.4 | 21.4 / 21.7 | 21.4 / 21.7 |
| L7 to the sea, k m3/s (model / obs) | 2,080 / 1,291 | 2,083 / 1,292 | 2,083 / 1,292 |
| L6 inland % (model / obs) | 20.6 / 20.9 | 20.5 / 22.7 | 20.5 / 22.7 |
| L6 to the sea, k m3/s (model / obs) | 2,051 / 1,291 | 2,051 / 1,281 | 2,051 / 1,281 |
(HydroSHEDS real inland: 20.5% L6 / 21.3% L7.) With the outlet data the rule is inert on the Earth world as built
(the fix equals rule-off): there the real closed basins are imposed (`closed`) and the outlets give the channels.
L6 under observed rain moves 20.9 -> 22.7% (the rule-off value: main's kept hollows there sent rivers on that now end
in walled real basins; not traced further). Scout 251's Earth bar (`scout250/earth_dry.py`: terrain + model climate,
nothing imposed, valley None) passes no outlet or valley, so `chan` is None there and its numbers are main's by
construction: inland 13.5 / 19.4%, false + 3.6 / 6.8% at L6 / L7.

Generated worlds: the fix acts through the run's valley memory. Fork screen (L6, seeds 1 and 77, main spun to 200
Myr, main and the fix continued to 400 Myr, draws = climate_offset 0 / 1e-5 C after the fork; scout 251's
`fork_run.py`, scout 260's `measure.py`; frames after 200 Myr):

| run | inland median % (p10-p90) | lakes % of land | largest lake median Mkm2 | giant frames % (t >= 300) | to the sea, k m3/s |
|---|---|---|---|---|---|
| s1 main d0 / d1 | 7.3 (5.3-14.9) / 8.6 (4.8-14.9) | 0.67 / 0.59 | 0.12 / 0.09 | 1.5 (0) / 1.5 (0) | 2938 / 2912 |
| s1 fix d0 / d1 | 9.7 (6.2-18.3) / 6.8 (2.1-18.3) | 0.59 / 0.75 | 0.07 / 0.10 | 6.0 (9.3) / 0 (0) | 2885 / 2813 |
| s77 main d0 / d1 / d2 / d3 | 12.3 / 11.9 / 11.9 / 11.9 (p10 2.2-5.4, p90 20.7) | 1.47 / 0.92 / 0.96 / 0.93 | 0.87 / 0.19 / 0.27 / 0.17 | 46.3 (39.5) / 20.9 (0) / 20.9 (0) / 20.9 (0) | 2789 / 2826 / 2809 / 2824 |
| s77 fix d0 / d1 / d2 | 15.9 / 16.1 / 14.2 (p10 7.0-11.0, p90 20.7) | 0.96 / 0.98 / 0.88 | 0.31 / 0.32 / 0.12 | 26.9 (14.0) / 26.9 (14.0) / 22.4 (7.0) | 2682 / 2679 / 2795 |
(main d0 / d1 reproduce scout 260's main rows exactly; d2 / d3 = offsets 2e-5 / 3e-5.)
- Giant-lake frames and lakes %: inside main's draws on both seeds. Seed 1 inland: inside (mean of medians 8.3
  against 8.0). Sea discharge: -2.1% (s1), -0.8 to -4.9% (s77).
- **Seed 77 inland is above main's draws** (14.2-16.1 against 11.9-12.3): the literal bar is missed there. Main's
  1e-5 C draws barely diverge (d1-d3 are the same trajectory), so main's spread is a weak null. On the same state the
  fix changes inland by -0.24 points (s77) and +0.19 (s1) (`same_state.py` on the 200 Myr checkpoints, the run's
  lakes() call: kept dry-hollow cells 1118 -> 636 on s77, 550 -> 532 on s1), and scout 260's unrelated wetland
  candidate moved s77 the same way (12.1 -> 15.6, both draws): most likely any code change knocks s77 onto another
  trajectory, but two seeds can't prove it. A code-perturbation null for fork screens is drafted.

## 2. Wetlands pass 2: overbank spill (missed; `scout261/overbank.patch`, applies on top of the fix)
Mechanism: a river's channel is the downstream hydraulic geometry's section for its flood month, w = 13.4 Q^0.46,
d = 0.18 Q^0.47 (Miller et al. 2014, HESS 18: 4883, Mississippi gauges at the mean annual flow; exponents as Leopold &
Maddock 1953's b ~ 0.5, f ~ 0.4), with Manning's n 0.030 (Chow 1959, clean straight main channel 0.025 / 0.030 /
0.033, via the UN-SPIDER copy of the table). Its equilibrium slope S_eq = (n v / d^2/3)^2 = 1.5e-3 Q^-0.487; on a
lower reach slope S the section carries sqrt(S / S_eq) of the flood; each month's flow above that spills (the
months from `seasonal_flow`'s profile, refactored into `_month_flow`), stands on the cell's flat share
(floodplain's 1 - relief / 400) during the spilling months and evaporates as open water (lake_evap - aet), taken
cell by cell down the rivers. Reach slope: the carved valley floor (outlet data on Earth, the runs' carve), walked
past the flood's eps steps (`_reach_slope`); the filled bed's eps flats (1.8e-7) made every filled cell lose all
it could. The months come from the climate (`months=`: temp, t_warm, t_cold, p_jul, p_jan; runs would need them
passed through `surface.erode`, not done: Earth only).

Earth L7 (`earth_wet.py`, ratios out / in along the traced river; baseline: the fix alone, same inputs):
| | target | observed | fix alone (obs rain / model) | overbank (obs rain / model) |
|---|---|---|---|---|
| Sudd, Mongalla -> 8.8 N before the Bahr el Ghazal | loss >= 30% | 47-57% lost | 2045 -> 2173 (+6%) / not traced | 1932 -> 1946 (+1%) / 11,864 -> 14,543 (+23%) |
| Okavango -> Maun | >= 50% lost | 95-98% lost | 1.03 / 1.71 | 0.95 / 1.71 |
| Niger Dire / Ke-Macina | 0.5-0.75 | ~0.6 | 1.00 / 1.00 | 0 (dies at 14-15 N) / 0.95 |
| to the sea, k m3/s | within 10% of main | | 1,292 / 2,083 | 1,271 (-1.6%) / 2,069 (-0.7%) |
Why it misses (`diag_ob.py` profiles, observed rain):
- **Sudd**: the model's Bahr el Jebel falls 1e-4 to 4e-4 per cell from 5 N to 8 N against S_eq 3.6e-5 for its ~2,000
  m3/s: the channel the geometry gives (300+ m wide, 4 m deep) carries it all. The flood ratio is 1.09-1.12 (Lake
  Victoria damps it), so even the one flat cell (8.5 N, 1.8e-5) spills only 113 m3/s. The real Bahr el Jebel's
  channel carries far less than its inflow because papyrus and floating vegetation choke it; that is not in
  hydraulic geometry fitted on single-thread gauge reaches.
- **Niger**: on the carved delta floor (1.2e-5 to 4.7e-5) the section carries 45-85% of the flood; as the river
  shrinks, S_eq rises (smaller rivers need steeper beds: S_eq ~ Q^-0.49), so the capacity falls faster than the flow
  and the reach runs away until the evaporation cap: under observed rain it loses 93-158 m3/s per cell and dies by
  15 N. The model's Niger flood ratio is 1.6 (real ~3, the 50% BASEFLOW flattens it).
- **Okavango**: its course to Maun is not flat on the cell means; -5%.
Parameters that would close these gaps (a channel-choking factor, a wider flood, a fixed slope floor) are fits, and
the runaway on the Niger has the opposite sign of what the Sudd needs. Pass 3 would need a different mechanism
(vegetation-limited channel capacity, or a real seasonal pulse from PW-028's months, not the damped one): not worth
the third pass now.

## Recommendation
- **Niger fix: committed, merge at the coordinator's call.** Sound, no tuned number, a filter that only removes
  hollows a known channel drains; Earth's Niger reaches the sea at L7 under both climates; goldens regenerated
  (`sim_L4_s1_60myr` moved), `pytest -m "not slow"` 1955 passed. It misses the screen's literal bar on seed 77's
  inland share (+2 to +4 points, above main's narrow draws), with the same-state check pointing to a trajectory flip
  rather than the rule; a wider screen (4 seeds, a code-perturbation null) would settle it.
- **Park PW-831** (two passes, two misses). The scout 260 sheet code and this pass's overbank code are off the branch;
  `scout261/overbank.patch` is the overbank version for whoever takes it up. Note for that pass: the ocean's
  fresh-water budget takes the land's runoff, not the routed flow (scout 260), and the runs don't pass the months.

Costs and cores: the fork screen ran 2 jobs x 4 threads, gated at load <= 30. One `pytest -m "not slow"` run used
the project's default 16 xdist workers for ~2 minutes (above this lane's 8-core cap; later runs used `-n 2`).
