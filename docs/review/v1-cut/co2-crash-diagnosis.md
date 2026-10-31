# CO2 crash in L6 draw 639472 (lane 94, PW-1224): diagnosis

## In plain words

At the very end of this world's history, its continents crash together into one large landmass (36% of the surface). That closes the oceans between them, so the subduction zones, which in this model supply about 92% of all volcanic CO2, get half as long, and the plates slow to half their speed. The volcanic CO2 supply falls by 3.5x in 70 Myr. The rock-weathering thermostat responds about as the model is built to, so it has to lower CO2 by about 2 e-folds for every e-fold the supply falls. Two things let it fall all the way to 36 ppm. First, plants in the model keep speeding up weathering even at CO2 levels where real plants would starve. Second, the weathering happens almost all in the tropics, which cool least, while fresh mountain rock keeps arriving there. The direction is real Earth behaviour: low volcanic output goes with ice ages in the plate-reconstruction literature. The size is not: 36 ppm is far below anything in Earth's record, and the drop is faster than the reconstructed swings. **My recommendation: do not block the v1 tag on this world.** It is the red tail of plate-speed variance that the model is known to have (PW-1156, PW-1158), caught at the finish line. The same world had an identical dip (to 110 ppm) at 870-890 Myr and recovered. No single nudge rescues it. The one mechanism worth adding is **plants starving below about 120 ppm (candidate 1, from Pagani et al. 2009)**, but it lifts this world only to about 70 ppm. Schedule it with the PW-1158/PW-1163 pair as v2 work. Settle what counts as a "crash" in PW-1223 before anyone tunes toward a number. Do not add a floor on the source or on CO2: that would be a clamp.

## Setup and reproduction

- Draw: `l6fix` seed 639472, roll 0.001. `paired.sh` (v1-finish-16) adds the roll to the tag's offset (0 for `l6fix`), so the run is
  `tools/ice_diag.py --seed 639472 --myr 1000 --level 6 --set star_brightening=1.0 climate_offset=0.001`.
  The ticket's "climate_offset 0.002" is wrong. 0.002 is the `l6c_p` twin of this seed, which ended at +4.7 C and 902 ppm.
- Code: main at 520abe04, frozen with `git archive` into scratch. `git diff --stat e5b526ff HEAD -- planet/` touches only
  `planet/lineages/` (15 files: dragons, megafauna, history, prey, spec, spread, the dnd sample). **No climate, tectonics,
  erosion or vegetation file changed**, so this is lane 92's code for this purpose.
- The reproduction is **bit-identical** to lane 92's record. At 930 Myr: source_raw 3238, sink_raw 673. At 1000: pCO2 36 ppm,
  src 0.265, sink 0.602, sink_raw 406, dT -10.2. Run 2 (with more instrumentation) matched run 1 step for step
  (`source_raw` identical in all 515 steps), so the instrumentation only reads.
- Instrumentation (scratch copy only, nothing on main): the source's three terms (ridge = new ocean cells, arc = 20 x nominal
  arc growth, plume) and the drift factor in `global_temperature`. The trench flux in `crust.arc_growth`: trench edges, the
  summed convergence at them, and the share behind continental crust. Per-cell snapshots of the weathering parts
  (supply, climate factor, plants, temperature, runoff) at 826/834/876/900/930/960/980/990 Myr. Also `--tect` for plates,
  speed, continents and events.
- Control: the same seed at roll 0.0005 (offset 0.0005). It reproduces lane 92's 513 ppm end. Three L6 runs in all, about
  11-15 min each at 5-10 threads.

## 1. Why the source falls 3.6x

**The source is almost all arcs, and the arcs are the slab flux.** Over 300-990 Myr the median shares are ridges 6.1%, arcs 91.8%
and plumes 2.0% (control: 6.1 / 92.2 / 1.6). The ln arc term follows the summed convergence at trench edges with r 0.94
(control 0.95), and the trench-edge count with r 0.89. Ridges and arcs move together (ln correlation 0.92, control 0.94,
same spread), because both follow plate speed (ln arc against ln median plate speed: slope 1.05, r 0.74). Mantle heat is
1.000 throughout, so the mantle is not cooling.

The last 70 Myr (instrumented run):

| t (Myr) | src | arc term | trench edges | summed conv | conv per active edge | plates | median speed (cm/yr) | largest continent (% of surface) |
|---|---|---|---|---|---|---|---|---|
| 930 | 0.963 | 2650 | 1806 | 9971 | 5.52 | 12 | 3.32 | 15.1 |
| 960 | 0.637 | 1861 | 1756 | 6433 | 3.66 | 15 | 2.88 | 15.6 |
| 984 | 0.540 | 1725 | 1542 | 6349 | 4.12 | 15 (980) | 2.78 (980) | 21.5 (980) |
| 990 | 0.399 | 1177 | 1134 | 4485 | 3.96 | 12 | 2.42 | 21.6 |
| 1000 | 0.265 | 767 | 941 | 2534 | 2.69 | 10 | 1.89 | **36.5** |

- From 930 to 1000 the ln source falls by 1.29. The drift factor (`climate_drift`'s lognormal wander) accounts for -0.12 of
  that (1.125 to 0.995). The tectonic -1.17 splits about equally between **trench length** (edges ln -0.65) and
  **convergence rate** (per edge ln -0.72).
- Trench length falls mostly in the last 20 Myr, at two sutures (982 Myr: a 13.6% piece; 984 Myr: 20.4%). These weld the
  largest continent from 21.5% to 36.5% of the surface (an assembly). The convergence rate peaked at 930 and then fell. The
  plates slowed from 3.3 to 1.9 cm/yr as they welded (12 to 10 plates).
- **930 Myr was a peak**, not a baseline: src was 0.96 at 930, against about 0.65 over 940-970. The lasting drop is about 2.4x
  from the 950-970 level and 3.6x from the peak.
- **It happened once before in this run.** Sutures at 866 and 872 Myr, with speed falling 4.6 to 2.5, took src from 1.15
  (834) to 0.42 (882), 2.7x in 48 Myr. pCO2 fell to 110 ppm and dT to -8.5. It recovered when new subduction started (884,
  888) and speeds rose again.
- **This draw's source runs low all through its second half**: median ln src -0.26 over 300-990, against -0.08 in the
  control. So the final assembly starts from an already-low base (pCO2 218-400 ppm from 850 Myr on). That is PW-1158's
  late-source decline again.
- **The roll is a fresh tectonic history, not a jitter.** By 100 Myr the 0.0005 and 0.001 offsets already differ in plate
  count (14 vs 16) and largest continent (26.5% vs 14.5%). The climate's feedback through erosion and isostasy is enough to
  set the plates on a different path. The control never assembles late: its largest continent is 18% at the end, 15 plates
  at 3.8 cm/yr.
- **Spread in numbers.** ln src sd over 300-990 is 0.24 here and 0.20 in the control (lane 80's cross-draw value is
  0.17-0.24). The worst drop within 70 Myr is 2.8x here (842 to 882, before the finish window adds the last step) and 2.1x in
  the control. Including the finish, it is 3.6x.

## 2. Why the sink barely responds

Over 930 to 1000 the sink (at the balance's CO2) falls only by a factor of 0.60 (ln -0.50), while dT falls 10.5 C. Its parts:

| part (diag) | 930 | 1000 | ln change |
|---|---|---|---|
| climate factor `w_temp` (kinetics x runoff) | 1.704 | 1.069 | -0.47 |
| erosion supply `w_supply` | 151 | 137 | -0.10 |
| plant factor `w_plant` | 2.61 | 2.78 | +0.06 |
| ice-free land share `w_area` | 0.286 | 0.276 | (ice spreads only where little weathers) |
| supply-weighted local T `w_T` (C) | 14.2 | 11.3 | |

The remaining ln -0.79 of the balance has to come from CO2 itself, through `co2_law`. That law has a slope of only 0.21-0.37
at these CO2 levels (bare share 6% to 1.5%; GEOCARB's planted FERT, `(2X/(1+X))^0.4`). So X falls from 1.06 to 0.072.
CO2_TAU is 0.4 Myr, so the stock sits at its steady state each step: at the end, sink x co2_law(0.072) = 0.602 x 0.445
= 0.268, against a source of 0.265. **This is the thermostat's equilibrium, not a runaway.** The ice albedo term moves only
-0.98 to -1.39 C.

Three reasons the sink's climate response is weak:

1. **The weathering is tropical.** 84% (930) to 93% (990) of the sink lies within 15 degrees of the equator (snapshots).
   That is where `temp_response` is lowest (0.5 C per C of dT), and the snapshots' tropical land cooled only about 2.7 C
   for 8 C of dT. That last number is confounded by plate drift over 60 Myr; see the draft on the weathering land's
   response.
2. **Fresh rock keeps arriving in the wet tropics.** On cells that weathered at both 930 and 990, the climate factor falls
   by 0.91 e-folds (local T -3.9 C gives -0.35; ln runoff -0.85 gives -0.56). That is a strong thermostat, about 0.11 per C.
   But only 41% of the 990 sink is on those cells. The rest is rock newly eroding as the colliding belt and drifting
   continents move into the equatorial band (supply-weighted |lat| 20 to 13 degrees). That cancels about two thirds of
   the response. **Net: 0.044 per C of dT, against the model's own small-signal design** `climate_coef()` = 0.09 x 0.6 +
   0.016 = 0.070.
3. **No biological floor.** At 36 ppm the model's planted ground still weathers at FERT = 0.44 of its balance rate. The
   weathering plants are grown at the balance's CO2 (`npp_w`, PW-880), and the vegetation's own CO2 responses are held
   within 124-990 ppm (`vegetation.CO2_RANGE`). The model's own C3 physiology (Farquhar et al. 1980 quantum yield,
   Bernacchi et al. 2001 compensation point, `vegetation._q3`) at the sink-weighted cells gives 3% of the balance's C3
   quantum yield at 35 ppm and 13% at 50 ppm.

**How much each piece matters** (closed-loop, offline: the episode's own gain of 3.9 C of dT per e-fold of CO2, which includes
albedo, CH4 and the star. Scratch script; open-loop for the tectonics):

| what-if (930 to 1000) | end pCO2 | dT change |
|---|---|---|
| the run as it is | 38 ppm (run: 36) | -10.3 |
| sink climate gain at the design 0.070 | 58 | -8.7 |
| drift factor held | 48 | -9.4 |
| plants starve below 124 ppm (candidate 1), no C4 rescue | 73 | -7.7 |
| the same, 30% of the enhancement kept (C4/CAM) | 65 | -8.2 |
| starvation + design gain | 84 | -7.2 |
| a 2.1x source drop instead (the control's worst in 70 Myr) | 109 | -6.2 |

The loop moves CO2 about 2.1 e-folds per e-fold of source. That is the model's thermostat by construction (lane 75's 11 C
of dT per e-fold of source). So even an ordinary source swing takes pCO2 down about 5-fold from wherever it starts, and this
episode started from a transient 532 ppm on an already-low base.

## 3. Plausible or defect?

Only sources read this session are cited:

- **Direction: plausible.** Mills et al. (2017, Nat. Commun., PMC5736558) estimate degassing from the length of
  subduction zones. They find "Model CO2 predictions follow the shape of the subduction zone length curve". Degassing was
  "anomalously low during the Late Neoproterozoic, roughly doubled by the Early Phanerozoic", and the Cryogenian is "a
  unique period of extremely low background temperature" in which moderate sink increases could trigger global
  glaciation. Müller et al. (2024, G-cubed 25, e2024GC011713; EarthByte summary page) link the Sturtian and Marinoan
  glaciations to "a low in mid-ocean ridge outgassing". An assembly that shortens trenches and cools the planet through the
  carbon cycle is Earth-like behaviour.
- **Rate: faster than the reconstructions.** Mills et al. report a twofold change between the Cryogenian and the early
  Palaeozoic. They report "no long-term (>100 Myr) secular changes in plate velocity", and only "shorter periods (~10-20
  Myrs) of significantly higher speeds" in Mesozoic kinematic models. This world's source falls 2.7x in 48 Myr and again
  3.6x in 70 Myr, inside one run. The model's ln source sd (0.2-0.24) may be Earth-like overall (lane 75), but its tail is
  fat: two 2.5-3.6x drops in 150 Myr. It comes from plate speeds that halve within tens of Myr on a grid with 10-16
  plates.
- **Depth: a model defect.** pCO2 36 ppm is far below the ice-core record's minimum: 172 ppmv at about 667 kyr BP (Lüthi et
  al. 2008, Nature 453:379). I have this from the abstract as quoted in a search result; the full text was not reachable.
  Pagani et al. (2009, Nature 460:85; abstract on RePEc) say CO2 "stayed above about 180 parts per million throughout the
  past 24 million years". Their reason: "As CO2 falls to critically low levels due to increased chemical weathering ...
  vegetation activity is substantially reduced, compromising the capacity to further enhance silicate chemical
  weathering". The model has no such limit. Its own plant physiology says C3 plants would be near their compensation
  point here, yet the sink keeps their full enhancement scaled only by GEOCARB's smooth FERT.

**Verdict.** The mechanism is physically plausible: an assembly shortens trenches and slows plates, the source falls, CO2
falls and the planet cools. The size is a model defect in two parts. (a) The plate-speed volatility gives source swings
faster than the reconstructions (PW-1156 / PW-1158 territory, tectonics). (b) The weathering sink has no biological floor
at low CO2, so nothing stops CO2 short of tens of ppm. (b) is the clean, sourced mechanism. (a) is the larger lever, but it
is v2 tectonics.

## 4. Candidate fixes

Ranked by soundness of mechanism, then cost. None changes a threshold.

### 1. Plants starve below the vegetation's CO2 floor (sink side; recommended, v2 with the PW-1158/1163 pair)
- **Mechanism.** Pagani et al. 2009. Below `vegetation.CO2_RANGE`'s floor (124 ppm), scale the planted ground's
  weathering enhancement (`PLANT_WEATHER - 1`) by the model's own C3 quantum-yield ratio, `_q3(T, 0.7 Ca) / _q3(T, 0.7 x 124)`
  at each cell's temperature. Keep GEOCARB's FERT above the floor, so nothing changes where PW-880 calibrated it. Better:
  lift the same floor for the vegetation itself, so biomes and the sink agree; C4 grass and CAM keep their share.
- **Why a nudge.** It uses existing, sourced physiology (Farquhar 1980, Bernacchi 2001, already in `vegetation.py`). It adds
  no new constant, only removes the 124 ppm hold for one consumer. It sets no target CO2.
- **Expected effect.** This world: about 36 to 65-73 ppm, -10.3 to about -8 C (offline). Still under lane 92's 100 ppm crash
  line, so **alone it does not clear this draw**. Other 41 draws: it acts only below 124 ppm. In tally_L6 that is 6 draws'
  minima (88-119 ppm), which it would lift. No effect on medians or on the warm side.
- **Risks.** Running the vegetation below 124 ppm is untested (biome shifts, C4 takeover). The C3/C4 split of the sink needs
  the weathering plants' PFT mix, which `npp_w` does not keep today. Small risk of a double count with FERT if applied above
  the floor.
- **Cheapest test.** (i) A unit test of the new law against the offline table above. (ii) A screen: this draw plus the 5
  tally draws whose minima were under 124 ppm (733847 l6c_0 r0.0005, 819014 l6c_p r0.0005, 583167 l6c_p r0.0005, 957317
  l6fix r0.0005, 733847 l6c_p r0.001), one roll each, arm against main. Pass if minima rise and median end T moves under
  0.3 C.

### 2. Find the plate-speed volatility (source side; the real lever, v2 tectonics, fold into PW-1158)
- **Mechanism.** The source is the slab flux. Halving the trench length and plate speed in about 50 Myr, twice in one run, is
  what to explain. Read why the plates slow as they weld (12 to 10 plates; the PW-969 giant-plate family), and whether new
  subduction starts too slowly after an assembly. In this run it took about 15 Myr after 872, but it does not happen before
  1000.
- **Why a nudge.** It fixes the tectonics that drive the source, not the source itself.
- **Expected effect.** Unknown until diagnosed. It would cut the source's tail in all draws, so fewer cold and warm
  outliers. **Risk:** tectonics changes move land share, supercontinent cycles and the golden tests; a full re-judge is
  needed.
- **Cheapest test.** No sim at first: from `--tect` records of the 36 tally draws (rerun is about 6 min each), measure the
  distribution of 50-Myr changes in median plate speed and trench flux, against Mills et al.'s "~10-20 Myr periods" scale.
  Lane 94's instrumentation patch (the trench-flux fields) is the template; PW-1158's checkbox asks for a diag field per
  part.

### 3. The PW-1158 + PW-1163 pair as planned (v2)
- It corrects the late-source decline and the bare-ground supply reference together, median-neutral by lane 80's estimate.
- For this draw it would remove part of the low base (median ln src -0.26). Estimate: the lane 80 bias, about -0.15 e-folds,
  is about +1.6 C at the loop's gain, so about 50 ppm here. Not a fix for the tail, but it is the right correction.
- Cheapest test: lane 80's 18-draw design, already specified on PW-1163.

### 4. Check the weathering land's temperature response (diagnostic first)
- The sink's net climate gain here is 0.044 per C against the design's 0.070. That is about 1.6 C of the crash: 38 to 58 ppm
  at the design gain. Part is real geography (fresh tropical rock). Part may be the climate model's tropical land cooling
  less than `temp_response`'s 0.5 per C (snapshots: about 0.34, but confounded by drift).
- Cheapest test: one terrain, `climate.compute` at dT 0 and -8 (seconds). Compare the land's cooling by latitude band with
  `temp_response`. Act only if they disagree.

### 5. Rejected as clamps (flagged)
- **A floor on the source's dip** (the ticket's "floor on the source's dip"), or a pCO2 floor. These set the answer, not the
  mechanism; they are metric-chasing clamps. Reject.
- **Rebalancing ridges against arcs** (ridges are only 6% of the source). Even if Earth's split is more even, it would not
  help: ridge and arc outgassing move together here (r 0.92). Moving to 50% ridges changes the 930-1000 drop only from 3.6x
  to 2.8x. That is not worth recalibrating PW-875's per-km3 yields for this ticket.

### 6. The ruling (for Daniel, with PW-1223)
- Lane 92's "<100 ppm after 300 Myr" is its own definition. With candidate 1 in place, CO2 floors would sit near where C3
  plants starve, about 60-120 ppm by the table above. Any crash line should be set with that in mind, and not tuned to.
- My lean: not a v1 blocker. It is 1 of 36 L6 draws (0 of 6 at L7). It is the known source-tail mechanism (PW-1156/1158), at
  the finish by chance, and it does not freeze the world over (land ice peak 33.7%). Candidate 1 goes to v2 with PW-1158/1163.

## Files and scripts

Scratch only (deleted after the lane): the instrumented code copy, the three runs and the analysis scripts (`ts.py`,
`stats.py`, `snap.py`, `mix.py`, plus inline what-ifs). Nothing was registered, so there is nothing to `planet delete`.
Follow-ups: `issue-tracking/inbox/draft-weathering-plants-starve-below-co2-floor.md` and
`issue-tracking/inbox/draft-weathering-land-temperature-response.md`.

Sources read this session:
- Mills, B. J. W. et al. (2017) Elevated CO2 degassing rates prevented the return of Snowball Earth during the Phanerozoic. Nat. Commun. 8. https://pmc.ncbi.nlm.nih.gov/articles/PMC5736558/
- Müller, R. D. et al. (2024) Solid Earth carbon degassing and sequestration since 1 billion years ago. G-cubed 25, e2024GC011713 (EarthByte summary). https://www.earthbyte.org/?p=10656
- Pagani, M., Caldeira, K., Berner, R. & Beerling, D. J. (2009) The role of terrestrial plants in limiting atmospheric CO2 decline over the past 24 million years. Nature 460, 85-88 (abstract). https://ideas.repec.org/a/nat/nature/v460y2009i7251d10.1038_nature08133.html
- Lüthi, D. et al. (2008) High-resolution carbon dioxide concentration record 650,000-800,000 years before present. Nature 453, 379-382 (abstract via search result only).
