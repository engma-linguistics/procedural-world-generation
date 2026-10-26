# v1-finish-11: the carbon balance anchored at the run's end, GEOCARB's weathering laws (2026-10-25)

Status: **code committed, tests pass (674 + goldens updated on purpose).** Full Gough alone, thermostat off, still
fails the strict bar (0/6 L6, first wave, stopped). With the PW-791/810 star thermostat on, the bar passes at L6
(16/18 at 1 Gyr; 2 Gyr late window 5/6 so far), but the thermostat sits at its +4% bound for most of the run, the
finished worlds run warm (9/18 outside the owner's human range) and the wet tropics are mostly treeless (3/18 >= 20%).
With the thermostat: L7 2/2 (of 8; stopped at hand-off), 2 Gyr late window 8/13 (62%, bar ~70%). Needs a decision: `issue-tracking/inbox/draft-balance-climate-vs-bar.md`.

## 1. The physics

### 1a. Anchor at the end (coordinator ruling, option A)
The sink's reference is now **the planet's weatherability with land plants, at the balance climate**, as GEOCARB
normalises everything to the present (Berner 1994, 2004).
- During the spin-up (< REF_FREEZE 300 Myr), `update_vegetation` also runs the vegetation model with every plant
  group unlocked, at the balance's CO2 (PCO2_BALANCE 500 ppm). That gives `sim.npp_pot`, the potential vegetation of
  the spin-up's climate. The reference sink is learnt with that potential's plant factor, not the bare land's.
- Bare land before the pioneers (~470-500 Ma) weathers at 1/PLANT_WEATHER of planted ground at the same climate and
  CO2. So it holds high CO2 early, and the plants' arrival brings CO2 down **to** the balance, not below it.
- The reference is still taken back to the balance's climate (PW-809: per-cell temperature response, plus runoff).
- Measured: the reference's potential plant factor is 2.3-2.4 (supply-weighted). The actual factor after the forests
  is 2.0-2.2, so the planted sink is ~10% below its reference and CO2 runs a little above the balance (in the warm
  direction). The cause: the potential is the spin-up's climate at 500 ppm, and the actual vegetation competes with
  a warm start. It is small and is left as is (in the draft).

### 1b. Plant weathering factor (literature)
`plant_factor = 1 + (PLANT_WEATHER - 1) clip(npp / NPP_WEATHER, 0, 1)`. PLANT_WEATHER is **3**, and NPP_WEATHER is
500 g C/m²/yr, about a temperate forest (Luyssaert et al. 2007).

| source | planted / bare |
|---|---|
| Drever 1994 (GCA 58) | < 2x, much of it through the plants' hydrology |
| Moulton & Berner 1998; Moulton, West & Berner 2000 (Iceland, paired catchments) | 2-5x (Ca, Mg) |
| Berner 1994, 2004 GEOCARB f_E (pre-vascular 0.25) | 4x |
| Bormann et al. 1998 (Hubbard Brook sandboxes) | ~10x |

3 is the field pairs' middle, between Drever and GEOCARB. The old factor was 1 + 0.5 clip(npp/800, 0, 1.5) (≤ 1.75,
measured ~1.15-1.2 planet-wide), which is below every source (audit item 25). The new factor is 2.0-2.2 planet-wide
after the forests arrive.

### 1c. Feedback strength (literature against the model)
The steady-state return of a lasting forcing F is G c / (a + G c), with these terms:
- G = 4.33 C per e-fold of CO2;
- c = ln of the sink per C of dT on the weathering land;
- a = the sink's CO2 log-slope.

| piece | literature | before | now |
|---|---|---|---|
| kinetics | Ea 40-60 kJ/mol = 5.8-8.7%/K; GEOCARB ACT 0.09 (~62 kJ/mol); field Si 59 kJ/mol (White & Blum 1995) | 0.09 on local T | unchanged (0.09 x the land's 0.5-0.8 response) |
| runoff | GEOCARB (1 + RUN dT)^0.65 (Berner 1994, from Peters 1984); GCM rain +2-3%/K (Held & Soden 2006) | **missing**: the erosion supply is set by uplift (measured −0.008/C) | runoff^0.65 on the climate's own 3%/C rain: +2%/C (`WEATHER_RUNOFF`, `climate.RAIN_PER_C`) |
| CO2, bare ground | GEOCARB R^0.5 | X^0.4 everywhere | X^0.5 |
| CO2, planted ground | GEOCARB II/III (2R/(1+R))^0.4 (Volk 1987): slope 0.2 at the balance, → 0 at high CO2 | X^0.4 (slope 0.4) | (2X/(1+X))^0.4 |

Return of a lasting forcing:
- **Before:** a 0.4, c 0.054. 0.234/(0.4+0.234) = **37%**, the v1-finish-10 diagnosis.
- **Now, planted near the balance:** a ~0.2-0.28 (logged as w_a: 0.19-0.28 after the forests), c 0.0735.
  0.318/(0.24+0.318) = **~57%**, rising to ~70% at 2-3x the balance's CO2.
- **Now, bare land:** a 0.5. Return 39%, but bare land holds 1/PLANT_WEATHER of the planted sink, which is worth
  ~+6 C of CO2 warming before the plants.
- GEOCARB itself gives ~50% bare and ~70% planted (same arithmetic). The model is now inside that range.

Earth check: GEOCARB/Royer's ~1000-4000 ppm early Phanerozoic under a ~4-5% fainter Sun. The anchored runs now carry:
- a median of **750-2400 ppm after 300 Myr** (was 320-1020);
- 5000-15000 ppm in the bare spin-up 1 Gyr ago (Sun 8% fainter).

The CO2 now answers the faint Sun on the evidence's scale. Without the star thermostat, the planet still sits 0-2 C
(dT) colder than the bar needs.

### 1d. Drift and start
- `drift_source` is re-derived on the planted law at the balance (a = 0.2, c as above): 3 C at the balance is
  ±0.36 e-folds of the source (was ±0.44).
- `start_carbon`/`balance_co2` use the new law, with the start's land bare (or START_PLANTED 0.5 planted if the
  pioneers predate the run). It is a first guess only: the stock relaxes within ~CO2_TAU.

Files: `planet/tectonics/earth.py` (`plant_factor`, `weathering`, `co2_law`, `co2_slope`, `co2_stock`,
`climate_coef`, `start_weatherability`, `global_temperature`, `update_vegetation`), `simulation.py` (npp_pot,
pot_frac, pot_lai), `climate.py` (RAIN_PER_C), `diag.py` (w_bare, w_a, w_pot), `tools/ice_diag.py` (fb uses the
logged slope).

## 2. Pass rates, L6 1 Gyr, strict bar (thresholds unchanged)

| setup | strict 300-1000 | last 540 (diag.) | pCO2 median after 300 | end pCO2 in 180-600 | wet-eq trees ≥ 20% | end T in human range | file |
|---|---|---|---|---|---|---|---|
| v1-finish-10 full Gough | 0/6 | 0/6 | 320-1020 | – | 4/6 | – | ../v1-finish-10/passrate_g10.txt |
| **anchored balance, full Gough alone** | **0/6** (stopped) | 0/6 | 752-2370 | 2/6 (90-987) | 2/6 | 4/6 | passrate_a.txt |
| anchored balance + star thermostat | **16/18** | 16/18 | 509-1773 | 10/18 (39-906) | **3/18** | 9/18 | passrate_t.txt |
| probe: alone, climate_offset +2.5 (not a proposal) | 3/6 | 2/6 | 768-2307 | 3/6 | 3/6 | 3/6 | passrate_o25.txt |

**Full Gough alone.**
- Icehouse shares 42-95% (were 66-100%); dT medians −2.0..+2.2 (were −2.5..−7).
- Two runs miss by 2 points (42.0%).
- No hellholes, no never-ice.
- Why it still fails: once the forests are in, the planet sits at its balance climate (+1.5 C, 500 ppm) minus the
  star's residual (~30-40% of −4..−6 C). The model's ice makes that an icehouse most of the time. The bar's passing
  regime is dT median ≳ +2.5 (v1-signoff's passing runs: +3..+5).

**With the thermostat** (acceptance 4: brought in because full Gough alone fails).
- `star_ctl` climbs to its +4% bound (+7.7 C) by ~300 Myr and stays at +5..+7.7 for the rest of the run. The run
  therefore ends under a star ~4% brighter than today's Sun.
- About 60-70% of that push is answered by CO2 drawdown. The residual +2-3 C is what passes the bar.
- The cost:
  - end pCO2 39-906 (8/18 outside 180-600);
  - finished worlds +7..+11 C on 5 draws;
  - wet equatorial lowland trees 0-16% on 15/18;
  - median tree cover 22% (10-35%).

**Probe.** A balance 2.5 C warmer at the same CO2, with the thermostat off, gives only 3/6. The draws' spread
(geography, drift) is wider than any one offset covers. The thermostat's per-planet feedback is what pulls the
outliers in.

### Owner's finish diagnostics (coordinator 2026-10-25; reported, not asserted)
The true area mean at the end, against pre-industrial 13.8 C, inside −6..+3 C:
- alone: 4/6 (two at +3.3);
- thermostat: **9/18** (9 too warm, +3.7..+10.7; none too cold);
- 2 Gyr: 3/6.

Land ice at the finish (end of run, and least over its last 12 Myr), against Earth ~10% of land and LGM ~25%:
- **alone:** 3.5-17.6% at the end; no NO-ICE, no LGM-like.
- **thermostat:** 0-12%. NO-ICE (< 1% at the least) on 3/18. 12/18 are below 6%, i.e. well under Earth's 10%, the
  owner's "not much less" floor. Typical: 1-6%.
- So with the thermostat, finished worlds tend to be warmer and less iced than Earth's pre-industrial.

## 3. L7 and 2 Gyr (thermostat on)

**2 Gyr, L6, 13 draws** (`passrate_t_g2.txt`):
- whole run 300-2000: 0/12 (one draw's key collides; 13 ran). The 300-1000 Myr part is ICEBOX or > 55% iced on
  every draw: the Sun there is 13-17% fainter (~−25 C raw), beyond the thermostat's ±4% bound and the bare land's
  CO2 boost;
- 1000-1500: 3/12;
- **late window 1500-2000: 8/13 (62%)**, against the acceptance's ~70%;
- last 540 Myr: 7-8/13;
- end pCO2 19-499 ppm (6/13 below 180);
- wet-eq trees 0-13%.

**L7, 1 Gyr: 2/2 pass** (seeds 957317 and 619496, d1 draws; `passrate_t_l7.txt`):
- icehouse 8% and 23%; dT median +5.3 and +2.8; max +14.1 (hellhole line 15.5);
- end pCO2 213 and 193; finish +0.3 and +1.1 C against pre-industrial; land ice 6-11%;
- wet-eq trees 3-4% (C3 at ~200 ppm, and see the draft).
- The other 6 L7 draws were not run: each takes ~75 min with 2 at once, and the lane was at its hand-off budget.
  To finish: `EXTRA=star_thermostat=1 launch.sh l7 1.0 PREFIX`, minus the two seeds done.

**Wet tropics under the thermostat.** Even at 400-500 ppm at the end the wet equatorial lowland carries 1-4% trees
on the 2 Gyr draws, while the thermostat-free anchored runs carried 3-39%. So it is not CO2 alone. A star ~4%
brighter than today's heats the tropics the most, so tropical heat stress is the likely cause (PW-806); it is
unmeasured here.

## 4. What a separate non-CO2 greenhouse term would change (PW-859, assessment only)

The key fact: the weathering thermostat answers any lasting forcing that isn't carbon, so CH4 or N2O acts like the
star. About 60-70% of it comes back as CO2 change, and only ~30-40% stays as temperature.
- **End CO2 for a given temperature.** The model's dT = 0 is Earth's own climate, which already contains today's
  CH4/N2O. A non-CO2 term changes the CO2 needed only where the planet's other gases differ from today's. If a world
  carries more (a higher CH4 background), the same end temperature needs less CO2, which is worse for C3 forests.
  It doesn't raise end CO2.
- **Glacial-interglacial swing (PW-828).** The time zoom's temperature forcing is one lumped glacial cooling
  (`glacial_cool`, standing for all the cycle's feedbacks, every gas and the ice). `glacial_pco2` 0.68 (190/280)
  only feeds the plants' CO2. So the zoom is not CO2-only for temperature, and CO2-only is right for the plants
  (CH4 and N2O don't fertilise). Splitting out CH4/N2O (~1/3 of CO2's glacial forcing) would not change the plants'
  CO2 swing. It would only split the lumped cooling. Nothing needed for v1.
- **Deep-time methane under the dim star.** A Proterozoic CH4 background (10-100+ ppm: Pavlov et al. 2003, against
  < 10 ppm in Olson et al. 2016) adds a few W/m² in the early part of 2 Gyr runs. Through the thermostat ~35% of
  that stays as warming (~+1-2 C), and early CO2 falls. That helps the 2 Gyr runs' 300-1000 Myr icebox somewhat. It
  doesn't help the 1 Gyr bar, whose cold era is after the forests, when the methane background would be today's.
- **Verdict.** PW-859 is not what stands between the model and the 1 Gyr bar. The bar is set by the balance climate
  (section 2). PW-859 is fine as the next lane's task for the 2 Gyr early era and for honesty of the forcing budget.

## 5. Tests and checks
- `uv run pytest -q`: 674 pass. `tests/golden/sim_L4_s1_60myr.json` is updated **on purpose** (carbon cycle).
- test_co2_stock is rewritten for the law. The steady state is now w co2_law(X) = s; the planted law saturates, so
  past 2^0.4 only warmth balances it (tested). Also new: co2_law/co2_slope and plant_factor. No threshold touched.
- earth_check: unchanged (main group 71.1%, exact 34.0%, log-rain corr 0.648). The climate at dT 0 doesn't depend on
  the carbon cycle.
- scorecard (default params, thermostat off; appended to docs/scorecard.jsonl):
  - seeds 1 and 2 at 1000 Myr: ice 2.7% and 2.8%; land NPP 356 and 283 g C/m²/yr; tree cover 31.0% and 21.9%;
  - plant groups arrive at 500-504, 564-568, 620, 880, 940 and 968-976 Myr.

## 6. What's left
- The decision in `draft-balance-climate-vs-bar.md`: thermostat as the v1 default with its costs, or a warmer
  balance, or the bar.
- Thermostat windup (PW-810's third box): it pins at the bound. The bound, not the band, is doing the work.
- Wet tropics with the thermostat (PW-806 hard check): 3/18.
- L7: 6 more draws (thermostat on), and L7 with the thermostat off for completeness.
- 2 Gyr: the early era is beyond any bounded control (PW-859's Proterozoic methane is the physical candidate, ~+1-2 C
  net). The late window is at 62%.
- `earth.py:987` reefs: an exp overflow warning on L7 (pre-existing reef growth law, harmless min()); not touched.

Harness: `launch.sh`, `pr.sh` (paths for this worktree), `passrate3.py` (adds the finish diagnostics), `terms.py`
(bare share, CO2 slope, potential plant factor), `passrate_{a,t,o25,t_g2,t_l7}.txt`. Raw diagnostics are in the session
scratchpad v1f11/.
