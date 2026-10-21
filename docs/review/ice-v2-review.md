# Ice ages for v2: a holistic review and plan (PW-470)

2026-10-21, review agent (read-only: no model code changed, no simulations run). Owner, 2026-10-21: "for v2 I want
to tackle it later and holistically including a review of what's been tried and didn't work so far."

Sources: the tickets under PW-470 and the other ice tickets (listed in section 2), the write-ups in
`docs/review/audit/` (ice-framing-deep-dive, icehouse-depth, fixes-ice, ice-veg, pw308-glaciation, pw293-sea-level,
pw313-polar-summers, polar-bundle, PW-030/033/440/448/449/465/471/514 notes), the three unmerged branches
(`worktree-agent-a9f64607e1a64d2e8`, `worktree-agent-af748cc6ffa533997`, `worktree-agent-ae1d70b30254180ac`), the code
(`planet/icemass.py`, `planet/tectonics/earth.py`, `planet/timezoom/`, `planet/finish.py`) and the v1 batch health
report (`docs/review/health/2026-10-21-batch/report.md`).

**In flight, not covered here:** another agent is bringing coast_loss and the batch's cost cut onto main on their own
(PW-514 option A, owner 2026-10-21). This review assumes that lands and builds on it. It does not repeat that work.

**Summary.**
- Since 10-13 there have been about 22 attempts. Each shared fix to the run's ice either deepened its cold eras or
  froze them, and each fix to the time zoom broke run/zoom consistency.
- The common causes:
  1. **The run and the time zoom are two different ice models.** The run solves an equilibrium extent with no flow
     and no budget; the zoom integrates a flowing sheet.
  2. **The run's hysteretic fixed point has no sheet-scale deglaciation.** The 408 m margin edge was an error doing a
     brake's job.
  3. **Saturated feedbacks** leave two branches, warm and cold.
- Kept: the shared `icemass` balance, the zoom's ice physics, coast_loss plus its cost cut (now landing), the glacial
  index as the cycle driver, and the imprint pipeline.
- Recommendation:
  - First make the zoom deglaciate with honest margins.
  - Then spike "one ice model, two clocks" (the run's cold eras from short integrations of the zoom's ice core)
    against a sheet-wide budget in the run's fixed point, and build whichever meets the cost budget.
  - Add the cycle-state storage (PW-464) on top.
  - Defer emergent cycles.

## 1. How ice works today, end to end

```
                       MAIN RUN (Myr steps; climate every 4 Myr)
  ┌─────────────────────────────────────────────────────────────────────────────────┐
  │ global_temperature:  dT → drift (sd 3 C) + 3 C × ln CO2 (weathering thermostat)    │
  │                         − ice albedo(ice area, levels off at 3 C);  τ = 5 Myr       │
  │        │                                                    ▲                       │
  │        ▼                                                    │ ice area              │
  │ climate.compute (bare ground under the old ice, its carried sheet air)              │
  │        │                                                    │                       │
  │        ▼                                                    │                       │
  │ ice_sheets: FIXED POINT of _ice_pass, repeated until the iced cells repeat           │
  │   SMB = icemass.balance averaged over 8 orbit states (±0.85° obliquity, 4 perihelia) │
  │   accumulation where SMB>0 (old ice keeps its height: hysteresis)                   │
  │   + ablation rings while the sheet's surplus pays (melt + flat ICE_CALVE)           │
  │   thickness = Nye profile (75 kPa) from the margin; no flow, no time                │
  │        │                                                                            │
  │        ▼                                                                            │
  │ sea_ice = −0.9 V / ocean area ;  sea_level = sea_ice + sea_tect (basins, ±400 m)    │
  └────────┬────────────────────────────────────────────────────────────────────────────┘
           │ a keyframe's bed, ice, climate, dT        (never fed back)
           ▼
                   GLACIAL TIME ZOOM (500-yr steps, 100 kyr–1 Myr, geology frozen)
  ┌─────────────────────────────────────────────────────────────────────────────────┐
  │ glacial index I(t) ∈ [0,1] (PW-471, cycle.py): scripted Paillard-style 3-state   │
  │   machine on the planet's own summer-sun series; dTg = −I × cooling              │
  │   cooling = 6.5 C × (ice-free snowline land share / 3.5%), cap 1.6×              │
  │ orbit anomaly: 0.25 C per W/m² on land (insol_k), mixed over 600 km (orbit_k)    │
  │ full climate every 10 kyr; same icemass SMB (PDD, carried air, edge_h 408 m)     │
  │ shallow-ice flow, shelves (Weertman, buttress 0.8), calving, sub-shelf melt,     │
  │ ELRA isostasy (3 kyr), carving + till/outwash/loess, vegetation migration        │
  └────────┬────────────────────────────────────────────────────────────────────────┘
           │ any frame (planet make picks 'glacial', 'interglacial' or the end, PW-479)
           ▼
  FINISHED WORLD (finish.py): frame's bed + ice + dT + tilt + tree cover + imprint
           │  glacial_erosion / till / outwash / loess, ice_max, glaciated
           ▼
  REGIONAL ZOOM: glaciers redrawn on the fine terrain (icemass rule at the pixel),
                 U-valleys, fjords, moraines, outwash, loess from the imprint (PW-092)
```

### 1.1 The run's ice (`earth.update_climate` → `earth.ice_sheets`)
- **It is an equilibrium extent, not a sheet that evolves.** Each 4 Myr climate update finds the iced cells as a
  fixed point: `_ice_pass` is repeated (at most 200 passes, PW-364) on the bed the ice presses down, until the iced
  set repeats.
- **One pass:**
  - The surface mass balance (`icemass.balance`, the time zoom's own PDD rule) is averaged over the cycle's 8 orbit
    states.
  - Accumulation is where that balance is positive: on bare ground (a new cap) or on old ice at the old ice's
    thickness (a margin next to bare land at `EDGE_H` = 408 m).
  - Each sheet then spreads ring by ring onto the cheapest land while its snow surplus pays for the melt plus a flat
    `ICE_CALVE`.
  - The thickness is a 75 kPa Nye profile from the margins (PW-276/366), at most 4 km.
- **Hysteresis is built in.** The old ice's height decides where the next update accumulates, so a big sheet keeps
  itself cold. Its carried air mass (PW-336, 0.6 × the share iced within ~1000 km) does the same on its margins.
- **No time, no flow, no sheet-wide budget.**
  - A sheet is kept if each of its cells' balance at its own height is positive, plus whatever ablation ring the
    surplus pays for.
  - Nothing asks whether the sheet as a whole is in deficit and should thin.
  - The only brake on a margin is the 408 m edge height: an edge cell's balance is taken ~500 m lower, ~3 C warmer,
    than the cell-mean ramp it really is.
- **Coupled to the global temperature.** Ice area → albedo cooling (`ice_albedo` 1.5 C per 3% of the surface,
  levelling off toward 3 C) → `dT` (relaxing over 5 Myr). The other terms are the CO2 weathering thermostat (since
  PW-438: ln pCO2 = ln(source/sink)/WEATHER_CO2, and ice-covered land doesn't weather) and a random drift (sd 3 C).
- **Sea level.**
  - The ice part: −0.9 × ice volume / ocean area.
  - The ocean-basin part: the floor's mean depth against the fixed starting reference (PW-293), ×0.69, levelling off
    toward ±400 m.
- **Isostasy.** The bed is settled at once under the step's ice (0.28 × thickness, flexed; PW-189).

### 1.2 The glacial time zoom (`planet/timezoom/`)
- **Geology is frozen at one keyframe, or at today's Earth.** Ice runs 100 kyr to 1 Myr in 500-yr steps on the same
  grid.
- **Ice physics:**
  - It shares the `icemass` balance.
  - It adds:
    - shallow-ice flow, with the balance applied inside the flow's sub-steps (PW-366);
    - margins at the edge height;
    - shelves (PW-367: Weertman spreading, buttress 0.8, breakup above −5 C air, sub-shelf melt);
    - calving at 1 m/yr per m of depth;
    - ELRA isostasy (τ 3 kyr);
    - glacial carving, till, outwash and loess (PW-037/495/497);
    - vegetation feedback and tree migration (PW-450/213).
- **Orbit.** Berger insolation at the planet's own tilt, ±1.2° obliquity, eccentricity. 0.25 C per W/m² on land and
  0.3 of that at sea, mixed over 600 km (PW-114).
- **The cycle is scripted: the glacial index (PW-471, `cycle.py`), the v1 kludge.**
  - I(t) is a three-state machine (between / building / ending) driven by the percentiles of the planet's own summer
    sun at the "cycling latitude": the mean latitude of ice-free land poleward of the sea-level snowline, in the
    hemisphere that has more of it.
  - The global cooling is −I × `cooling`.
  - `cooling` is 6.5 C at Earth's 3.5% snowline-land share, in proportion elsewhere, at most 1.6×.
  - The index stands in for the CO2 and ice-albedo feedbacks, so the zoom has none of its own.
  - Earth, L6, 600 kyr: cycles of 98–109 kyr, maxima −86..−104 m, endings giving back 57–76 m in 15 kyr, the
    Laurentide reaching 42.5 N.
- **Start.**
  - From a run's moment, its ice is taken as it is (the run's rule's extent).
  - Earth starts from the real ice, with an `anchor=obs` cooling over the ice where the model's summer is too warm.

### 1.3 Finished worlds and the imprint
- `planet finish` / `planet make` turn a frame into a world: bed, ice, dT, sea level, tilt, tree cover, and the
  imprint so far (`glacial_erosion`, `glacial_till`, `glacial_outwash`, `glacial_loess`, `ice_max`, `glaciated`).
- `finish.now_kyr` picks the frame: the glacial maximum, the latest interglacial, or the end (PW-479).
- The run itself keeps a coarse record: `glaciated_myr` and a ×3 glacial erosion in `earth.erode`. Soils and zoom
  vegetation read it.
- A world sliced straight from the run (no time zoom) carries the run's equilibrium ice. That is roughly the
  interglacial extent on moderately cold moments and the glacial one on deep moments (PW-462).
- The imprint is one time zoom deep (PW-496): tens of metres under most ice, against Earth's ~2.6 Myr of glaciations.

### 1.4 Where it stands today (main e599d1e)
- **Earth time zoom on the index: passes.** Cycles 98–109 kyr, maxima −86..−104 m (the LGM ~−120 m), the Laurentide
  to 42.5 N, interglacial ice 9.1–12.2% of land. It needs `glacial_cool` 6.5 C, above the LGM's 4.5–6 C, because the
  sheets respond weakly (PW-435).
- **Run moments in the zoom: 8 of 10 L6 cold moments drift 15–200 m off their start at I = 0** (PW-471/492). The v1
  bar was reworded to "cycles at ~100 kyr without runaway", and all 10 pass that.
- **Warm or already-iced moments get almost no ice age.** The cooling scales with ice-free snowline land (PW-536/538):
  one moment got 0.49 C and a −7 m target.
- **The run's cold eras are too deep.**
  - v1 batch (8 runs × 1 Gyr): ice-part minima −240..−864 m, and 11–40% of keyframes below −150 m in every run. This
    fails the run-level bar everywhere (PW-434).
  - The total sea level ends 1 Gyr at −370..−600 m in 7 of 8 runs. A large part of that is the ocean-basin term, not
    the ice (PW-549, v1, ocean).
- **No emergent ice-age cycle anywhere.** The run has none by design. The zoom's is scripted.

## 2. Chronology of attempts

Dates are 2026. Numbers are L6 unless marked. "Cold-era check" is the 10-seed L6 1 Gyr run test (main 8/10 passes,
bar 7/10: the owner's ~70%).

| # | when | what was tried | numbers | outcome and why | lesson |
|---|---|---|---|---|---|
| 1 | 10-13/14 | **Time zoom built** (224675c). Fixes for generated worlds glaciating too hard (**PW-031**): count only the displaced water, take the run moment as the cycle average | −400 m at dT 0 → bcc894 −171 → −132 m; Earth −53 m. Cold world 8e71fd stayed −258 m | The rest was blamed on the run's rule, which had no ablation zone, and sent to PW-190 | The zoom exposes the run's ice from day one |
| 2 | 10-15 | **One shared mass balance** `icemass.py` for the run, zoom and regional zoom, plus a run rule with an ablation zone (**PW-190**, option C, d5e00f1). **Isostasy** (PW-189) | Rule trade-off: the balance rule made the run −449 m; the old rule made the zoom drift −170..−240. Zoom spread went −127..−321 → −56..−239 m | Kept. Sharing the balance is the right idea | Sharing the *balance* isn't enough: the run's *budget* (no flow, no marine loss) still differs |
| 3 | 10-15 | **Audit fixes PW-274..277** (20684ed): Nye surface from the margin's bed, one ice-surface climate, a new cap's rule the same in the run and the zoom | L5 seed 2 min −371 → −169 m. Antarctic coldest-month bias −10.1 → −1.7 C, but the annual mean now +8.9 C too warm. Zoom drift median −94 → −53, worst −195 → −312 | Kept | Removing a compensating error (the 10 C ice cooling) exposes the base error under it |
| 4 | 10-15 | **PW-308**: runs stopped glaciating after the audit (−9..−48 m on 11 seeds). Run bisects, then the fixed-planet probe `tools/ice_probe.py` | Cause: PW-266's frozen-sea vapour lid (Antarctic snow at dT −6: 92 → 18 mm). Leads at 0.1 (5e24aa9): probe −7.5 → −44 m, 8 icehouse spells, seed 11 −322 m | Kept | **Bisect with fixed-geography probes, not chaotic runs.** The old "working" state was itself a bandaid (sea ice as a full vapour source) |
| 5 | 10-15/16 | **Polar bundle** PW-335/336A/337/332 (baabbba): carried sheet air (`air_mass`), frozen-sea air, capped inversion. **PW-313** (frozen-sea summers, not merged) | Antarctic snow 70–80S 77 → 158 mm (GPCP 210). Probe at dT 0: 0.10% → 2.33% iced. A 6–7 C era gives −146 m. PW-313's "full damping" held Antarctica only by making Greenland 11 C too cold | Bundle kept; PW-313's variant rejected as compensating | Margin snowfall (storm tracks, PW-015) is the real gap. The carried air is the steepest cold feedback |
| 6 | 10-16 | **PW-293** sea level: the start ocean is the model's own steady ocean; `SEA_TECT_MAX` 250 → 400 | Median +148 → +15 m. Icehouse spells 1 → 3. Seed 11 total −370 m (ice −264, basins −105) | Kept | Sea-level offsets of ±100 m mask or create cold-era depth. **Report the ice and basin terms apart** |
| 7 | 10-16 | **PW-364/365** (cdd867d): the run's ice settles to a fixed point within each update (it had lagged ~80 Myr); the orbit mix matches the zoom's | Deepest −219 m, none below −250. L5 envelope world at dT −4: −576 m over 16% (−223 without carried air). Hysteresis −163 vs −32 m depending on the starting ice. Cost +7..+23% | Kept | **The fixed point is where hysteresis lives**: the old ice's height decides its own survival |
| 8 | 10-16 | **PW-418**: the zoom on main fell ~400 m in 50 kyr and carving eroded 10–50× too much | Bisected to 1416523 (PW-015 rain: ~35% more snow on sheets) plus the run/zoom mismatch (PW-366). PW-421 option A: fix PW-366, don't bend the rain | Diagnosis kept | A rain change upstream moves the ice by hundreds of metres. The ice is the climate's most sensitive integrator |
| 9 | 10-19 | **PW-366** (7fbf3b6): run sheets at 75 kPa with each cell's mean rise, `EDGE_H` 333 → 408 m; the zoom's balance inside the flow's sub-steps | Unforced zoom drift −231 → +7 m at 20 kyr (strict xfail now passes). But cold eras deepened to a worst of −368..−609 m (**PW-434**), and Earth's glacial got shallower, −76 → −33 m (**PW-435**) | Kept. PW-434 drift-sd option tried and dropped (4263f74: it only reshuffles which seed goes deep) | **Thicker, honest run sheets make cold eras deeper.** Nothing in the run takes them back down |
| 10 | 10-20 | **PW-438** (152bcd4): weathering fixes plus CO2-dependent weathering (pCO2^0.4, `CO2_MAX` 3) so CO2 can rise and end cold eras | 3 of 4 seeds pass (worst −386/−569/−404/−393 m). Owner: ~70% of seeds is the bar | Kept | The CO2 thermostat is real but slow (Myr). It can't undo a fixed point that holds at any dT the drift visits |
| 11 | 10-16 → 10-19 | **PW-030**: an emergent 100-kyr sawtooth, 5 attempts (eed6a3a): the run's ice-albedo rule in the zoom; proglacial-lake calving; two dust-albedo variants; bed lag; `insol_k` 0.45 | Baseline Earth swing 43 m (obliquity-paced heartbeats). s400 builds once to a rigid cold branch (−161 m); s580 drifts +225 m. Lakes 77–105 m against 5,400–8,900 m of marine calving: no effect. Dust: no effect. `insol_k` 0.45 cycles but melts Antarctica | Only the albedo rule merged | CO2 + albedo amplify any drift ~2.5× onto one of **two saturated branches**. Orbit rectification loses ice (+142 m from eccentricity alone). Cycles need a state-dependent sensitivity and a cold branch that isn't rigid |
| 12 | 10-20 | **PW-440** (3fc7380): a three-mode cycle (between / building / ending, Paillard / Huybers); an ending boosts melt ×1.8, CO2 +80–100 ppm, faster calving | s400 100-kyr spectral power 0.07 → 0.33, swings 30–104 m. But endings take 30–75 kyr and stall with 20–112 m left: a 70–80N sheet with −11 C summers. Earth unchanged (48 m). Run moments still drift +103..+238 m | Merged, later replaced by the index | **Boosting an ending doesn't clear a sheet whose summers are far below melting.** The sheet's own height and air keep it out of reach |
| 13 | 10-20 | **PW-448/449/453**: Earth glacials only ~1.7–1.95 C colder (LGM ~6). Re-anchor the ice-albedo tanh; a physical, snow-season-weighted albedo (229a4ea), 4 attempts | Feedback per metre is fine (0.044 vs 0.048 C/m); the tanh spends 1.4 of its 3 C on today's ice. Linear albedo −42.8 → −70.8 m. A1: Earth −47.6 m but the run 4/10. A2: run 9/10 but Earth −32.6 m | PW-449 wontdo; PW-453 keeps main's tanh | **Any lever shared by the run and the zoom trades Earth depth against run health.** The loop gain is near 1 |
| 14 | 10-20 | **PW-450** vegetation feedback in the zoom (and PW-213 migration) | 60% of the boreal forest turns to tundra, net only −42.8 → −45.1 m; the tropics green as it cools (wrong sign). +11% run time | Kept (cover); its feedback is ~0 | Not a lever for depth |
| 15 | 10-20 | **PW-033 diagnosis** (f624372): Earth glacials are precession pulses (Laurentide 0.17 → 1.72 → 0.26 Mkm² in ~24 kyr) | Ranked causes: (1) margins melt at `edge_h` 408 m against a cell mean ~900 m (fixing it: −45 → −98 m, but the consistency test fails at −46 m); (2) `insol_k` 0.25 is ~3× the seasonal 0.08–0.09; (3) overturning in Baffin Bay, Fennoscandia's January 18 C too cold; (4) Labrador snow half of observed | Became PW-459/460 | **Two shared constants were Earth-flattering errors**: they made sheets fragile, so the orbit could pulse them |
| 16 | 10-20 | **PW-460/459** (branch `a9f64607`, 246ef40): a margin cell's balance over its sub-cell Nye ramp (`margin_ramp`), and the orbit response from each cell's own seasons (`seasonal_k`), in the run and the zoom | Earth zoom, margin only + obs: −82 m, interglacial ice 9.5–12.3%, Laurentide 5.65 Mkm² to 44.9 N, **every Earth target met**. Cold-era check: both 1/10, margin only 0/10, k only 6/10, a2 margin 3/10. Time below −150 m 10–60% → 45–87%. Consistency +17.9 (margin) / +76 m (a1 both) | Not merged (stop rule). **PW-461** | **The 408 m edge was the run's only deglaciation brake.** Honest margins + a hysteretic fixed point = cold eras that never end |
| 17 | 10-20 | **PW-462 deep dive** (63947ad): run ice as the cycle mean, the zoom as a window | Every stored zoom starts at an edge of its own range; window means miss the run by −68..+137 m. Moderate moments: run −19 m, mean of the states' equilibria −83, zoom mean −87. Deep s11 @ 400: run −252, zoom mean +94 above it (≈ 40 rule gap + 20 orbit + 30 feedback reference). On the branch all 8 states agree within −340..−371 m: the freeze isn't about averaging | Plan R1–R8; children PW-463..469 | **The framing moves the problem; it doesn't dissolve it.** The run needs the zoom's marine budget and a feedback swing in its states |
| 18 | 10-20 | **Owner parks ice physics for v1** (bbce1c3). **PW-471 glacial index** (ff89d4e): a scripted I(t) on the orbit, planet-relative cooling. A 40 kyr spin-up was tried and reverted (`PW-471-spinup.patch`) | Earth passes everything (above). Run moments 0/10 on the strict bar (I = 0 drift +16..+101 m), 3/10 with the spin-up (+7% cost). PW-492 option C: ship, bar reworded | Shipped as the v1 kludge | Scripting the pacing decouples it from the broken branches cheaply. **The ice model is then the only remaining problem** |
| 19 | 10-21 | **PW-037/491/495/497** carving, debris fans, outwash, loess on the index | Earth 43 m/Myr mean, p99 300, max 490 (literature range); drifting moments 1–2× Earth; +4.5% cost | Kept | The imprint works when the ice behaves. It's one zoom deep (PW-496) |
| 20 | 10-21 | **PW-536/538**: zooms ae8f75/7ec3fe show no swing | Snowline-land share 0.26% (Earth 3.49%) → cooling 0.49 C, target −7 m. A forced 5 C still only gives corr −0.48 against a start drift of +18..+33 m | PW-538 → v2 | Planet-relative scaling must count the land the ice already holds |
| 21 | 10-21 | **PW-465 coast_loss** (branch `af748cc6`, c720d92): the run's coastal ice pays the zoom's grounding-line outflow (`icemass.coast_loss`, `earth.coast_cost`) | The loss is grounding-line outflow into deep water (70–85%), not front calving. I = 0 drift within 25 m on 9/10 moments (main 4/10); window mean median 17 m vs 99; cold eras 7/10 (seed 7 −362 → −745 m); +39% wall | **Being brought to main now, with the cost cut (PW-514 option A, another agent)** | **The I = 0 drift was a missing budget term.** It fixes the run/zoom start, not cold-era depth |
| 22 | 10-21 | **PW-514 batch** (branch `ae1d70b3`: coast_loss + PW-460/459 + **PW-464** `cycle_ice`, an interglacial fixed point under the warm half-orbit plus index-binned glacial states; cost cut `PASS_TOL`) | Cold eras **1/10** (worst −421..−715 m). Earth maxima −141..−182 m, interglacial ice 16–20%, consistency +40.7 m, endings keep 34 of 36 m after 15 kyr. Cost +4% (cost cut works) | Parked (PW-526). Owner: take coast_loss + the cost cut, review first | **With honest margins neither the run nor the zoom can deglaciate a big sheet.** The interglacial fixed point itself sits at −400..−700 m in cold eras |

Tried and shown not to help (don't retry without a new reason):
- proglacial-lake calving and glacial dust (PW-030);
- a narrower climate drift sd (PW-434 B, PW-368);
- bigger global orbital gain, `insol_k` 0.45 (it melts Antarctica);
- vegetation albedo (PW-450, ~0);
- melt and CO2 boosts at endings (PW-440, which stall);
- a 40 kyr spin-up alone (PW-471 patch, 3/10);
- re-anchoring the albedo on the LGM's forcing (PW-449/453).

## 3. Root causes that recur

1. **The run and the zoom are two different ice models of the same ice.**
   - The run solves an equilibrium extent: no time, no flow, a Nye profile, a flat calving charge. The zoom
     integrates a flowing sheet with shelves, grounding-line outflow, isostatic lag and margins.
   - They share the surface balance (PW-190/277), but not the budget or the dynamics.
   - Every run moment therefore starts at an edge of the zoom's range (PW-462), and every honest change to one side
     breaks the other: PW-366 (cold eras deeper), PW-460 (run freezes), PW-449/453 (Earth vs run).
   - coast_loss closes the biggest term (marine outflow). The extent-vs-dynamics gap remains.
   - This is the root of attempts 1, 2, 9, 13, 16, 17, 18, 21 and 22.
2. **Fixed points that freeze: sheets that can't deglaciate.**
   - The run's sheet survives where each cell's balance *at its own height* is positive. A sheet whose total budget
     is in deficit has no way to thin, lower its surface and walk down the height-mass-balance feedback. Real
     deglaciation runs on that feedback, with isostatic lag (Oerlemans 1980, Pollard 1983, Abe-Ouchi et al. 2013).
   - The old 408 m edge melted margins as if ~500 m lower. That was the only brake, and it is an error that works as
     a brake.
   - The zoom has the dynamics, but at L6 a margin is one ~110 km cell (one-cell ablation zone, PW-115). In PW-440 and
     PW-514 its endings stall on sheets whose summers are −11 C, because the carried air (PW-336/439) and the height
     keep them out of melt range.
   - Attempts 9, 12, 16 and 22 all hit this.
3. **Saturated feedbacks give two branches.** CO2 clipped, ice albedo levelling off (the tanh spends 1.4 of its 3 C on
   today's ice, PW-448), loop gain near 1 on Earth. Any drift lands on a warm or a rigid cold branch (PW-030), and
   small slope changes swing Earth's depth by tens of metres (PW-449/453).
4. **Shared constants that are errors, each holding another error up.** `EDGE_H` 408 m (truth ~900 m cell mean),
   `insol_k` 0.25 (truth 0.08–0.09 from the seasons), LOCAL 0.3, the 10 C ice cooling, sea ice as a vapour source and
   then as a lid.
   - Fixing one exposes the next (attempts 3, 4, 5, 15, 16).
   - Pattern: a constant that flatters Earth's numbers in the zoom is usually also a hidden brake on the run.
5. **Base-climate biases decide the ice's geography.**
   - North America too warm (Labrador July +5.5–6 C), Eurasia too cold (Fennoscandia January −18 C).
   - Overturning in Baffin Bay, half of Labrador's snow, Antarctic margins at about half of GPCP (PW-015/332).
   - So the model's ice grows at 70–80N, not 40–60N (PW-033/448), and it takes a 6.5 C cooling to get a Laurentide.
   - These belong to the climate, not to the ice model.
6. **The run's sea level drifts on its own.**
   - The basin term has a fixed reference and ±400 m of room. 7 of 8 v1 runs end 1 Gyr at −370..−600 m total
     (PW-549, PW-051).
   - Cold-era health numbers mix the two terms unless they are split (PW-293 showed a ±100 m offset changing icehouse
     counts).
7. **Planet-relative scaling that misses the state.** The index's cooling counts only ice-free snowline land
   (PW-538), so a planet whose ice is already down gets no ice age. The target ignores the land the ice can spread
   over (PW-492: moments 1.6–2.5× deeper than their target).
8. **Measurement on chaotic runs.** Run bisects re-roll the history (PW-308), and judging levers one at a time hid
   their interaction: each passes alone, but stacked they fail (PW-514). What worked was fixed-geography probes,
   factor separation and a fixed moment suite.

## 4. What works and should be kept

- **`icemass` as the one surface balance** for the run, the zoom and the regional zoom (PW-190/194/275/277): monthly
  PDD on the shared 12-month climate, lying-snow damping, the carried sheet air (PW-336), one ice-surface climate.
- **The zoom's ice physics:**
  - shallow-ice flow with the balance inside the sub-steps (PW-366);
  - shelves, buttressing, breakup and sub-shelf melt (PW-367);
  - flotation-aware sea level (PW-031);
  - ELRA isostasy (PW-189);
  - carving with Robin's thermal column and the yield cap (PW-037/491).
- **`icemass.coast_loss`** (PW-465): the run's coastal ice pays the zoom's grounding-line outflow. It is landing now.
  So is the cost cut (`PASS_TOL`, coast cost computed once per fixed point: +4% instead of +39%).
- **The glacial index** (PW-471) as a pacing device: planet-relative percentiles of the planet's own summer sun, a
  three-state machine, a backstop. It is cheap and robust, and gives Earth-like 100-kyr cycles. Keep it as the
  default driver in v2. The fix belongs in what it drives, and in how its amplitude is set (PW-538).
- **Sound physics parked on branches**, to re-apply once something can deglaciate: `margin_ramp` (PW-460) and
  `seasonal_k` (PW-459) from 246ef40, and `balance(warm=True)` + `glacial_states` from b74f2c0 (PW-464's machinery).
- **The imprint pipeline:** frames → `finish.glacial_imprint` → soils / zoom landforms (PW-092/495/497), and the
  `now` picker (PW-479).
- **Tools and tests:**
  - `tools/ice_probe.py` (fixed-geography probe);
  - `tests/test_timezoom_consistency.py` (unforced 20 kyr < 25 m: keep it as the *shared rule* check);
  - the PW-471 table of 10 run moments;
  - the 10-seed cold-era check;
  - `tools/sealevel.py` (ice and basin terms apart);
  - the PW-030 `tz_eval.py` / sweep scripts.
- **Process:** stop rules, batches of coupled levers judged together, negative results written down with numbers,
  and Earth as an analogue with its calibration calls flagged (the 6.5 C).

## 5. Options for v2

All bars are planet-relative unless they are Earth-analogue checks:
- **Sea level** in the ice term only, `sea_ice_m`, reported apart from the basins.
- **Ice extent** as a share of the planet's own land poleward of its snowline: ice-free plus iced, PW-538 A.
- **Cycle timing** from the planet's own orbit series.
- **Moment suite** (fixed, used for every option):
  - the L5 consistency fixture;
  - L6 s11 @ 400 (deep);
  - L6 seed 2 @ 580 and @ 620;
  - L6 seed 7's −745 m era from coast_loss;
  - one moderately cold moment;
  - one warm moment (86c513's source);
  - Earth L6.
- **Run bars:** the 10-seed L6 1 Gyr cold-era check (≥ 7/10), plus one L7 run.

### Option 1: a sheet-wide budget in the run's fixed point (PW-526 A)
- **Physics.** A steady sheet's total surface balance equals its losses (calving, outflow, basal melt). Today the run
  only asks that each cell's own balance be positive.
  - Add the sheet-scale budget. After the extent test, each connected sheet integrates its balance plus `coast_loss`.
  - A sheet in deficit thins: its Nye surface drops by the deficit over its area. In the steady profile that is an
    effectively lower yield stress, or retreating the dearest margin ring.
  - The next pass re-tests accumulation at the lower height. The height-mass-balance feedback can then run downhill,
    which is what real deglaciations do.
  - Margins on `margin_ramp` (PW-460) but **integrated over the ramp** (the hypsometric balance). That is what the
    branch already does with 2 Gauss points. Keep it, but let the sheet budget carry the deficit that the 408 m edge
    used to fake.
- **Effort.** m–l, about 2–3 agent-days in the serial run lane, plus the 10-seed checks.
- **Risk: medium.**
  - It is still an equilibrium rule. The two-state hysteresis is real physics and must survive (Antarctica must hold
    at dT 0: the probe's 2.3–2.5%).
  - A budget can also make sheets *grow* where they are in surplus (today only rings grow). That can deepen cold eras
    on snowy coasts.
  - It doesn't close the extent-vs-dynamics gap, so the zoom's window mean will still miss by some tens of metres.
- **Measure.**
  - `ice_probe` hysteresis: Antarctica held at dT 0, and a cold era's sheet gone within one or two updates once dT
    is back above its inception threshold.
  - The 10-seed check.
  - PW-467's window-mean tool on the moment suite.
- **Done when:**
  - With PW-460/459 re-applied: cold eras ≥ 7/10, with no era's ice mean below −450 m on more than 2% of keyframes
    (the PW-449 bar).
  - The probe holds today's Earth ice at dT 0 within 20% of its area, and loses ≥ 80% of a cold era's extra ice
    within 2 updates of a +3 C step.
  - The consistency test is < 25 m.
  - The window mean is within max(15 m, 0.25 × swing) on ≥ 5 of 7 moments.

### Option 2: one ice model, two clocks. The run's cold eras from short zoom integrations (PW-461 B(3))
- **Physics.** At each climate update where the planet has ice or snowline land, run the zoom's own ice core
  (`timezoom` kernels: balance, SIA flow, coast loss / shelves, ELRA isostasy) for a short window under the glacial
  index. It is warm-started from the previous update's ice, so it only has to adapt to 4 Myr of change.
  - Store the window's time mean (`ice`), its interglacial and glacial maxima (`ice_ig`, `ice_glacial`), and the
    index distribution.
  - The run's sea level, albedo and isostasy use the mean (PW-462 R-d).
  - Leave out carving, plants, frames and full climates: one climate per update, as now, with the index's cooling
    applied as the zoom does.
  - The run's ice is then the zoom's ice by construction, and the "window" framing holds exactly. The zoom started
    from a keyframe is a spun-up continuation (PW-469 becomes trivial).
  - Deglaciation comes from the same dynamics as in the zoom: isostatic lag, outflow, thinning. So it still needs the
    zoom-side deglaciation fix, stage 1 below.
- **Effort.** l–xl, about 4–6 agent-days.
  - Factor the zoom's ice step out of `_Sim` into a reusable core (PW-445 shares the helpers).
  - A coarse time step: 2 kyr instead of 0.5. The CFL limit on the SIA at L6 needs checking.
  - Cache and warm-start the state.
  - The run's storage gets `ice_ig` / `ice_glacial`.
- **Cost (estimate, to measure in the spike).**
  - An L6 100 kyr zoom takes ~10 s with everything on (coordination.md speed pass).
  - Ice core only, at 2 kyr steps, over a 40–60 kyr warm-started window: ~1–3 s per cold update.
  - A 1 Gyr L6 run has 250 updates, typically 30–50% of them icy. That is +2..+6 min on ~17–20 min (the v1 batch's L6
    runs took 996–1193 s), so **+15..+35%** at L6. L7 scales ~3×, roughly the same share.
  - Fallbacks: integrate only when the fixed point moves; run the ice core on the L5 parent grid.
- **Risk: medium-high on cost and engineering, low on consistency.** Sheets need ≥ ~20–40 kyr to answer, so a window
  shorter than that biases toward the start. The per-step stop rule from PW-462 applies.
- **Measure.**
  - The window-mean test passes on the moment suite by construction. Check it anyway: a zoom from the keyframe should
    continue the run's statistics.
  - The 10-seed check, the cost, and the Earth zoom bars.
- **Done when:**
  - Cold eras ≥ 7/10, with the same −450 m tail bar as option 1.
  - The keyframe-started zoom's first-100-kyr mean is within max(15 m, 0.25 × swing) of the run's stored mean on
    ≥ 6 of 7 moments.
  - L6 wall ≤ +35%, L7 ≤ +35% (the owner's call, below).
  - Earth's zoom keeps the PW-471 bars.
  - The 25 m unforced test still passes on the core.

### Option 3: a state-forced cycle on equilibria (PW-464 + PW-538 A, the deep-dive's R3)
- **Physics.** Keep the equilibrium run, but compute it at the cycle's states: the warm-half interglacial plus
  index-binned glacial states cooled by I × `cooling`. `cooling` counts iced land too (PW-538 A), so a planet with
  its ice down still gets an ice age. Store the time-weighted mean.
  - This is what b74f2c0 built. It failed only because the interglacial fixed point itself froze. **On its own it is
    not a solution.** It is option 1 plus a better-defined stored state.
- **Effort.** s–m on top of option 1. The machinery exists.
- **Risk: low** once option 1 works. **Fatal** without it (the batch: 1/10).
- **Measure / done when:** as option 1, plus the stored mean equals the time-weighted state mean (a unit test). Earth's
  rule at dT 0 gives a Pleistocene-like mean of about −100..−130 m in the run's terms, with `ice_ig` ≈ today's.

### Option 4: emergent cycles (retire the index)
- **Physics.** Make the 100-kyr cycle come out of the coupled system, from mechanisms the literature credits:
  - isostatic-lag and calving instability at large volume (Pollard 1983, Abe-Ouchi et al. 2013);
  - an ocean carbon reservoir with its own timescale, not CO2 slaved to ice;
  - the sea-ice switch (PW-441);
  - salinity memory (PW-018);
  - dust.
- **Effort.** xl, research.
- **Risk: high.**
  - Five attempts under PW-030 and PW-440 failed: lakes and dust did nothing, boosts stalled, gain changes melted
    Antarctica.
  - The cycles would be planet-specific and hard to keep inside the health bars on 70% of seeds.
- **Measure.** 100-kyr spectral power ≥ 0.3 on Earth and on ≥ 2 run moments. Swing ≥ 80 m on Earth. Builds ≥ 3× longer
  than endings.
- **Done when:** the above, without the index, and every option-1/2 bar still held.
- Realistically this is a later research mode (`index=off` plus the mechanisms), not v2's foundation.

### Comparison
| | fixes run/zoom gap | fixes deglaciation | fixes cold-era depth | cost | effort | risk |
|---|---|---|---|---|---|---|
| 1 sheet budget | partly | yes (run) | likely | ~0 | m–l | medium |
| 2 one ice model | **yes, by construction** | inherits the zoom's | likely | +15..+35% (est.) | l–xl | medium-high (engineering) |
| 3 state-forced | no (needs 1 or 2) | no | no alone | ~0 | s–m | fatal alone |
| 4 emergent | no | maybe | no | ? | xl | high |

## 6. Recommendation and staged plan

**Recommendation: make the zoom deglaciate honestly first. Then spike option 2 against option 1 on cost, and build
whichever passes. Option 3's stored states ride on top of either. The glacial index stays the driver, and option 4 is
deferred.**

The recurring failure is root cause 1 (two ice models), and option 2 is the only approach that removes it rather than
moving it. But option 2 inherits the zoom's deglaciation problem, so that comes first under either option. Option 1 is
the fallback if the spike's cost is too high. It is cheaper, and it fixes the deglaciation brake properly in the run,
but the gap with the zoom stays a calibration chore.

**Stage 0: baseline and harness** (s–m; parallel lane; no physics). Waits for coast_loss + the cost cut on main.
- PW-467: `tools/tz_mean.py`, the window mean against the run, and a strict-xfail slow test.
- Fix the moment suite (section 5) and record main's numbers on it.
- Split `sea_level` into its ice and basin terms in `tools/health.py`'s cold-era checks (PW-549 needs it anyway).
- Turn `tools/ice_probe.py` into a hysteresis probe: a dT up-and-down staircase on a fixed geography, reporting
  extent and volume per step.
- **Checkpoint 0:** a table of all bars on main after coast_loss. Nothing is judged without it.

**Stage 1: honest margins that deglaciate, in the zoom** (m–l; zoom lane; the run untouched). Re-apply `margin_ramp`
and `seasonal_k` (246ef40) to the zoom only. Then find why ramp-margin sheets don't retreat after an ending. Measure, in
this order:
- the carried air on the margins (PW-439);
- the one-cell ablation zone (PW-115: the integrated ramp should cover it);
- isostatic lag (τ 3 kyr: endings need a depressed bed to work);
- the outflow at the front (`coast_loss` in the zoom).

**Checkpoint 1:**
- The Earth zoom with honest margins, index on, meets: cycles 80–120 kyr; endings give back ≥ 60% of their glacial
  excess within 15 kyr; interglacial ice within 9–12% of land; maxima ≤ −80 m at a cooling of ≤ 6 C, so the 6.5 C
  over-ask can go.
- On the moment suite (zoom from the run's ice as now), ≥ 5 of 7 endings return within 20 m of the window's
  interglacial level.
- **Stop rule:** 3 attempts without meeting it → report. The next suspect then is the base climate (root cause 5:
  PW-015 margins, PW-033's North Atlantic), not the ice model.

**Stage 2: spike** (m; run lane). Build the minimal ice core and run it inside 2 runs (L6 seed 2, s11) on 3 moments.
- Measure the cost per icy update, the warm-start window length needed (20/40/60 kyr), and the window mean against a
  full zoom.
- In parallel, prototype option 1's sheet budget on the hysteresis probe.
- **Checkpoint 2 (owner decision):**
  - Option 2 if L6 cost ≤ the agreed budget (lean +35%) and its mean matches a full zoom within max(15 m, 0.25 ×
    swing).
  - Else option 1.

**Stage 3: build the chosen run side** (l). Re-apply PW-460/459 to the run as well. Add option 3's stored states
(`ice_ig`, `ice_glacial`, mean; PW-464). Fix the cooling share (PW-538 A, recalibrated on Earth).
- **Checkpoint 3:**
  - Cold-era check ≥ 7/10, no era mean below −450 m on > 2% of keyframes.
  - The window mean within bar on ≥ 5 of 7 moments.
  - The consistency test < 25 m.
  - The scorecard and earth_check not worse.
  - Goldens updated.
  - One L7 run checked.

**Stage 4: the zoom as a window, and product** (m each; the parallel lane after stage 3).
- PW-469: spin-up, or the run's stored state with option 2.
- PW-468: phase picker in the API and viewer.
- PW-463: health bars as cycle means.
- PW-466: era start/end (lowest).
- PW-496: imprint depth. With option 2 the run can carve as it goes (C). Otherwise scale by `glaciated_myr` (B).
- Close PW-241/295/418/421/436 as superseded.

**Stage 5 (optional, post-v2): option 4** as an `index=off` research mode, with the PW-030 bars.

Separately, outside the ice epic:
- **PW-549 (the basin term's drift)** belongs to the ocean lane. It should be fixed before stage 3's bars are read on
  the total sea level.
- **PW-015's margin snowfall (PW-313/332)** decides whether Antarctica holds by physics rather than by hysteresis.

Rough size: stages 0–3 ≈ 8–12 agent-days, mostly serial in the run lane. Stage 4 ≈ 3–4 more in parallel.

## 7. Open questions for the owner

1. **Which run-side approach?**
   - Options: one ice model (2), a sheet-wide budget in the equilibrium rule (1), or let the spike decide.
   - **Lean: let the stage-2 spike decide, with a preference for 2.** It is the only option that ends the run/zoom
     mismatch rather than moving it, and that mismatch is behind most failed attempts.
2. **Run-time budget for ice in v2.**
   - **Lean: accept up to +35% wall at L6 and L7 on icy runs** (warm runs pay ~0). Above that, option 1.
3. **Keep the glacial index as v2's cycle driver?**
   - **Lean: yes.** Fix the ice it drives and its amplitude; treat emergent cycles (option 4) as a later research
     mode. Five attempts show emergence is a research problem, and the index already gives Earth-like pacing from each
     planet's own orbit.
4. **The glacial cooling (PW-538).**
   - **Lean: A**, count the land under grounded ice in the snowline share, and recalibrate on Earth.
   - Target a cooling within the LGM's 4.5–6 C once the margins are honest (stage 1), dropping today's 6.5 C over-ask.
   - No floor (B is a stopgap).
5. **Re-apply the honest margin and orbit response (PW-460/459) in v2?**
   - **Lean: yes, in both the run and the zoom, but only after stage 1 shows the zoom deglaciates with them.** The
     408 m edge is an error doing a brake's job (no stopgaps).
6. **How deep may a cold era go?**
   - **Lean: keep the PW-449 tail bar** (worst era mean ≥ −450 m, ≤ 2% of keyframes below −430) and the ~70% seed bar.
   - State the bars on the ice term and as cycle means (PW-463).
   - Allow deep, ending icehouses on geographies that earn them, like the L5 envelope world.
7. **Earth's zoom start.**
   - **Lean: keep the real-ice start with `anchor=obs`.** Earth is a test analogue, and its real ice is a true
     interglacial phase. It doesn't need the run's window spin-up.
8. **Imprint depth (PW-496).**
   - **Lean: C if option 2 is chosen** (the run carves as it goes, so a world's imprint is an icehouse deep).
   - Otherwise A now, with B only if the owner wants Great Lakes sooner.
9. **Time box and stop rules.**
   - **Lean: a checkpoint report at the end of each stage.** Stop after 3 failed attempts within a stage, and fall
     back as listed rather than stacking more levers. Stacking was how the PW-514 batch hid its interactions.
