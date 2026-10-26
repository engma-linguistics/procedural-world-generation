# v1-finish-13: the plants' light measured, the drift sized, the carbon-cycle couplings (2026-10-25)

Status: **handed off mid-measurement.** The code is final for this lane (1b52cdf). The full set (L6 1 Gyr 18,
L6 2 Gyr 13, L7 1 Gyr 8) is running on it under nohup, with prefix `cpl`. It has not been tallied, so this is
**not ready to merge** until the tally is in.

## 1. The plants' light on its own (be00f07), L6 1 Gyr, 18 draws
The `shade` set is v1-finish-12's lane, stopped after its L6 set. The table is in `passrate_shade_l6.txt`.

| check | v1-finish-11 physics (10 draws) | shade (18) |
|---|---|---|
| bar (300-end) | 7/10 | **15/18** |
| bar + hard finish checks | 3/10 | **10/18** |
| wet-eq trees >= 20% | 5/10 | **18/18** |
| finish T -6..+3 | 8/10 | 12/18 |
| land ice 1-25% | 10/10 | 16/18 |
| end pCO2 180-600 (diag.) | 5/10 | 9/18 |

The light fix solves the wet tropics: 22-67% trees on every draw. What is left is the finish temperature, and every
failure is on the warm side: +3.2, +3.3, +4.0, +5.6, +7.9 and +9.5 C. These draws ended at pCO2 900-3800 ppm. Two
draws are icebox (819014 c_0 and 619496 fix) and one is never-ice (733847 c_0).

## 2. The drift sized for what the model lacks (dfc8b48; ruling on draft-drift-double-counts-degassing)
`climate_drift` goes from 3 C to **0.8 C**, which is sd(ln source) ~0.09-0.10 (earth.drift_source; it was ~0.36).
The ridges' and arcs' outgassing is explicit, and the plumes' is too since PW-875. So the drift stands only for:
- **Net organic burial** (buried minus weathered and degassed organic C). This is O2's source, so the O2 record
  bounds it:
  - GEOCARBSULF's Phanerozoic O2 is ~15-30% (Berner 2006, 2009), with a ±30% envelope (Royer et al. 2014, AJS 314).
    That is ±~7e18 mol of the 38e18 mol reservoir (Berner 2004; GEOCARBSULF's %O2 = 100 O / (O + 143)).
  - Held over the drift's 40 Myr memory, that is ~0.18e18 mol/Myr, ~3% of the silicate weathering flux
    (~6.7e18 mol/Myr, Berner & Kothavala 2001).
  - Doubling it for pyrite burial offsetting O2 (Berner & Raiswell 1983) gives sd(ln) ~0.05.
  - Royer et al. 2014 agree: the carbonate d13C, which drives GEOCARBSULF's organic burial, is among the top O2
    drivers and is not among the CO2 drivers. Those are ΔT2x, LIFE and GYM.
- **Ocean chemistry**: carbonate on the subducting plates, GEOCARB's f_C (0.75 -> 1 as pelagic carbonate spread,
  Wilkinson & Walker 1989; Berner 2004). Its ln range of 0.29 is sd(ln) ~0.08.
- In quadrature these give ~0.10. Seafloor weathering and reverse weathering are left out: their large changes are
  Precambrian (Isson & Planavsky 2018).
- The size is not fitted to the end-pCO2 band.

## 3. Option C (Pagani et al. 2009): checked, not added
- **The model already has the feedback.** GEOCARB's FERT, (2X/(1+X))^0.4 on planted ground, is GEOCARB's own form of
  it. A separate C3 floor would count it twice.
- **It is weaker than the literature.** From 400 to 100 ppm the planted sink falls ~1.5x (FERT x0.675). Beerling et
  al. 2012 (J. Ecol. 100: 31) model a ~4x fall in the biota's weathering capacity, and Quirk et al. 2014 measure ~3x
  (1500 -> 200 ppm) in growth chambers.
- **What the model lacks** goes to a draft: grassland weathering like forest, and the plants' 124 ppm CO2 floor
  (`draft-plant-weathering-grass-as-forest.md`). Since PW-880 the NPP part no longer carries CO2 (section 4), so that
  draft's ~10% NPP share is gone and FERT alone carries it.

Literature used: Berner 2004 (The Phanerozoic Carbon Cycle); Berner 2006, 2009 (GEOCARBSULF O2); Berner & Kothavala
2001; Berner & Raiswell 1983; Royer et al. 2014 (AJS, GEOCARBSULF error analysis, read in full); Wilkinson & Walker
1989; Isson & Planavsky 2018; Pagani et al. 2009; Beerling et al. 2012 (abstract); Quirk et al. 2014 (abstract).

## 4. The coupling-audit carbon couplings (1b52cdf; coordinator, mid-lane)
- **PW-880.** `weathering()`'s plant factor reads `sim.npp_w`: the run's plants (same groups) grown at
  PCO2_BALANCE, through a second `vegetation.model` call per climate update with its own warm start. CO2 now reaches
  planted ground only through FERT. Cost: a second vegetation call per update. The smoke run took 8.6 min for
  400 Myr at L6 on a loaded machine, and pytest took 17:45 against 8:13. Not separated from the load (draft).
- **PW-881.** The runoff factor is each cell's (runoff / RUNOFF_REF)^0.65. RUNOFF_REF is 560 mm/yr, the model
  Earth's ice-free land mean, and it cancels against the reference. Its small-signal slope is RUNOFF_PER_C = 0.016/C
  (measured: the model Earth's sum(runoff^0.65), 0.0163 for dT -3..0 and 0.0154 for 0..+3; land runoff +2.6%/C).
  It feeds climate_coef (so the drift's C-to-ln factor is 0.116 per C) and the spin-up's shift to the balance.
- **PW-875.** The plume melt (head + apron + vents from `volcanism.hotspots`, before the height caps) degasses at
  PLUME_CO2 = 3.3x the ridges' CO2 per km3:
  - ridges ~0.15 wt%: Marty & Tolstikhin 1998's 2.2e12 mol/yr over Crisp 1984's ~21 km3/yr;
  - plume and flood-basalt melts ~0.5 wt%: Self et al. 2006; Black & Gibson 2019.
  - Smoke run, seed 11, L6, 400 Myr: plumes are a median 1.8% of the source (10-90% 0.8-3.2%, max 4.6%). That is
    small against the literature's comparable plume and ridge fluxes. This is the modelled plume melt volume, not the
    yield (draft). Baked-sediment carbon (Svensen et al. 2004) is not counted.
  - The steps now record `plume_src`.
- **PW-873.** The ice-albedo zero is the model's own Earth ice at dT 0, area-weighted: L6 2.77%, L7 3.05%
  (`tools/ice_probe.py 0 --level 6/7`, which now prints the area share; `earth.MODEL_EARTH_ICE`). The run's ice share
  is area-weighted (ocean.cell_area_km2).
- **PW-882.** `zoom_vegetation` sets `s["cloud"]` from the world's sky cover, so cloud forest is named as on the
  globe.
- Checks: pytest 687 pass plus the golden sim, which was updated on purpose (`sim_L4_s1_60myr.json`). earth_check on
  dfc8b48 is unchanged (group 71.2%, exact 33.9%, log-rain corr 0.648). Scorecard: a line was committed for dfc8b48;
  the line for 1b52cdf is running (see 6).

## 5. The human-habitable screen near the run's end (`screen.py`, coordinator's diagnostic)
Each 2-Myr step passes if:
- true mean T is within -6..+3 C of pre-industrial (the climate's true mean carried to the step through dT);
- land ice at that moment is 1-25% of land;
- pCO2 >= 180 ppm;
- for "+trees", wet-eq trees >= 20% at the nearest climate update.

The bar is not part of the screen. On the shade set (18 draws):

| window | screen | +trees |
|---|---|---|
| a passing moment in the last 5 Myr | 14/18 | 14/18 |
| ... 10 Myr | 15/18 | 15/18 |
| ... 20 Myr | 15/18 | 15/18 |
| the end itself | 12/18 | 12/18 |

Latest pass, in Myr before the end: 0 on 12 draws, 2 (958504 c_0), 4 (53669 c_p), 8 (733847 c_0). No pass in 20 Myr
on 3 draws, the warm ones: 733847 c_p, 819014 c_p and 957317 fix. The tally does not show it, so note that the end
screen (12) is above the finish checks (10/18 with the bar): the screen has no bar, and it takes the ice at the
moment, not the least in 12 Myr.

## 6. Hand-off: what is running and how to resume
- **Full set on 1b52cdf, prefix `cpl`.** Three nohup queues: `launch.sh l6 1.0 cpl` (PID 3676396), `g2` (3676397)
  and `l7` (3676398). Logs are in the session scratchpad at `v1f12/lane_cpl_{l6,g2,l7}.log`, and outputs at
  `v1f12/cpl_*`. To resume after a kill, rerun the same three commands from the worktree:
  `nohup docs/review/base-climate/v1-finish-12/launch.sh l6 1.0 cpl &`, and likewise g2 and l7. Finished draws are
  skipped. A killed draw leaves no result file, so it reruns.
- **Tally:** `pr.sh cpl`, or `passrate4.py $V/cpl_*`, and `screen.py $V/cpl_*`. Put the screen's column next to the
  table.
- **Scorecard and earth_check on 1b52cdf:** nohup PID 3676399, writing `v1f13/scorecard2.txt` and
  `v1f13/earth_check2.txt`. The scorecard appends its line to `docs/scorecard.jsonl`; commit it.
- **Then:**
  - If the bar is ~70% on all three sets, the lane is ready to merge.
  - If not, report the numbers. Don't use the thermostat.
  - The warm finish-T failures (section 1) are the next finish question if they persist.
