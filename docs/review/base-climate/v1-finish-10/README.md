# v1-finish-10: the star anchored at the run's end, the plant calendar on Earth's timeline (2026-10-24)

Status: **the code is built and the tests pass. It does NOT pass the v1 bar.** The anchored star, alone or with the
PW-791 thermostat, leaves most 1 Gyr L6 runs as iceboxes or ending CO2-starved. The cause is in the carbon cycle,
not the star (section 4; needs-decision draft `draft-anchored-run-ends-co2-starved.md`). Do not merge this as the
v1 default without settling that draft. L7, 2 Gyr and the scorecard were not run: L6 already fails.

## 1. What was built (design and physics)

**Star (PW-809 B, PW-813, PW-815).** `earth.star_forcing` is counted against today's Sun. The star's age is
4570 − run_end + t (Myr, times `star_brightening`), and the forcing is 238 W/m² × (L/L_now − 1) at the model's
0.81 C per W/m². It is negative early (−15.5 C raw at the start of a 1 Gyr run at full Gough) and 0 at the end.
- `star_age` is removed. `star_now_offset_myr` (default 0; > 0 means the run ends in the future) is added.
- `params.run_end` replaces `flora_end` for both the star and the flora, through one reader, `earth.now_myr`. It is
  0 by default, meaning the run's length: `timeline.simulate` sets it and stores it in the run meta params; direct
  callers set it too (RUN_END_DEFAULT is 1000).
- `check_star` refuses a run that would start before its star formed (> 4570 Myr at 1.0).
- The default star_brightening is now 1.0 (full Gough), as the ruling asks.

**Carbon cycle under the dim start (PW-809).**
1. `start_carbon` starts the stock at the weathering balance for the start's star (`balance_co2`).
2. During the spin-up the sink's reference is no longer the sink itself. It is the sink taken back to the balance
   climate (dT = co2_term(0) + climate_offset). Each cell goes through the weathering temperature law at its own
   temperature response to dT (`temp_response`: climate.compute moves the equator by 0.5 dT and the poles by
   1.5 dT). So a cold spin-up under a faint star is not learnt as the balance, and its slow weathering builds up
   CO2, as after the freeze.
- PCO2_BALANCE 500 and REF_MYR / REF_FREEZE are unchanged. They now mean the balance under today's Sun with the
  spin-up's weatherability.
- At start the derived stock is 3060 ppm at full Gough / 1 Gyr, and 1160 ppm at 0.45.

**Drift on the carbon source (PW-819, coordinator ruling).** The OU walk (`climate_drift` 3 C, 40 Myr) is
multiplicative noise on the outgassing (`drift_source`): ±0.44 e-folds, sized so it gives about the same warming
at the balance. It is no longer a temperature term, and the spin-up doesn't learn it. corr(dT, ln pCO2) after
300 Myr is now **+0.31 to +0.85** in every run (the audit found warm eras CO2-starved).

**Plant calendar (PW-807).**
- `vegetation.GROUPS` carry windows in Ma before now:
  - pioneers 500-470;
  - vascular marsh 440-420;
  - forests 395-375;
  - flowering 140-120;
  - grasses 75-60;
  - C4 grasses 35-25.
- Each window is the per-seed spread, and its young end is the deadline.
- A group whose window lies before the run's start is there from the start.
- `FLORA_PACE` and `plants_from` are removed. Land is bare until the pioneers arrive (pioneers' niche 1 on bare
  land).
- Sea life: skeletal reef builders arrive at 545-520 Ma, drawn per seed (`earth.REEF_BUILDERS_MA`). Before that,
  microbial carbonate builds at `MICROBIAL_REEF` = 0.1 of the reef rate. This is crude: Shark Bay stromatolites
  ~0.4 mm/yr against corals' few mm/yr. Marine algae (> 1 Ga) predate every run, and nothing else in the run is
  tied to sea life.

**Default world moment.**
- `slice --at auto` (and make) is the run's end ("now"). If the end is in an icehouse, it is the latest
  least-ice-quarter frame of the last 12 Myr (`representative_time`).
- `slice --ago MA` asks for an era by age (`highlights.ago_time`).

**Time zoom (PW-828).** `glacial_pco2` 0.68 (LGM 190/280) replaces `co2_share`. It is scaled by the planet's own
glacial cooling.

**Harness.** `passrate3.py` reports per run:
- the strict bar (never-ice, permanent icebox and hellhole all FAIL; icehouse ≤ 40%; thresholds unchanged);
- the forward windows;
- the **end-counted last 540 Myr** (diagnostic);
- pCO2 (median, 10-90%, < 180 ppm share, at the end);
- the **true area-mean T** next to 14.5 + dT (PW-822);
- tree cover;
- the wet-equatorial-lowland trees (|lat| < 10°, > 2000 mm, < 500 m).

These come from new fields in `tectonics/diag.py` updates: trees, wet_eq_trees and pco2.

## 2. Pass rates, L6 1 Gyr, strict bar (`passrate_*.txt`)

| star | strict 300-1000 | last 540 Myr (diag.) | end pCO2 (ppm) | wet-eq trees ≥ 20% | note |
|---|---|---|---|---|---|
| old star (v1-signoff, 0.45 from age 0) | 13/18 | – | 87-244 slices | 4/6 offline | for reference |
| full Gough, anchored | **0/6** (first wave; stopped) | 0/6 | 18-830 | 4/6 | every run ICEBOX; dT med −2.5..−7 |
| 0.45, anchored | **1/6** (first wave; stopped) | 1/6 | 79-1224 | 1/6 | 3 ICEBOX, 2 at 67-80% icehouse |
| full Gough + thermostat (PW-791/810) | **5/18** | 8/18 | median 128 (17-705) | **2/18** | 9 fails at > 40% icehouse; tropics CO2-starved |

- End of the thermostat runs: dT −5.0..+9.4 C. True mean T 7.7-22.7 C against 14.5 + dT of 9.5-23.9: the
  real mean runs ~1-2 C below the label for these offsets (PW-822). Tree cover 8-29% of land.
- No hellholes and no never-ice runs anywhere.
- The two 6-run sweeps were stopped after their first wave: 0/6 and 1/6 can't reach 13/18.

## 3. Tests and checks

- `uv run pytest -q`: 674 pass, 0 fail after the fixes below. The golden `tests/golden/sim_L4_s1_60myr.json` is
  updated **on purpose** (star frame, calendar, drift on the source).
- test changes, all harness only, with no threshold touched:
  - test_vegetation's group-window test is rewritten for the calendar;
  - test_highlights' four representative_time tests are replaced by one for the end / interglacial / --ago rule;
  - test_envelopes passes run_end = 400 (its run continues to 400 Myr);
  - test_ice_diag's temperature identity drops the drift (it's on the source now).
- earth_check is unchanged: group agreement 71%, exact 34%, log-rain corr 0.648. The climate model at dT 0
  doesn't depend on any of this.
- The scorecard was not run: compute went to the sweeps, and the L6 bar already fails.

## 4. Why it fails: the carbon cycle, which the old star was hiding (`terms.py`)

Per 100 Myr in the full-Gough runs, the CO2 term answers the star only partly (e.g. star −14.8 → CO2 +10.9 → dT
−5 at the start). The late runs are cold with the star near 0.
1. **The thermostat is weak.** The sink acts on local temperature, which moves 0.5-0.8 per C of dT, and weathering
   goes as X^0.4. The steady state passes only ~40% of a lasting forcing back, so a faint start stays ~10 C below
   balance. Audit item 14 found that decisions.md:33's "saturating weathering law" was never built; PW-830 (v2)
   carries it. The runoff part of the feedback is near zero (supply −0.008/C).
2. **Weatherability rises against a frozen reference.** The reference is learnt on bare land by 300 Myr. Then
   relief builds (PW-708) and plants arrive at ~470 Ma (plant factor 1.0 → 1.15-1.2), so the sink stays above its
   reference and CO2 falls below the balance: end pCO2 79-207 ppm at 0.45. The old from-age-0 star cancelled
   exactly this trend with +5.6 C of late warming. Anchored, the star ends at 0. The thermostat then brightens the
   star past today's, which draws CO2 down further (median end 128 ppm) and leaves the wet tropics treeless (C3
   starvation, PW-806).

Options are in the draft. The lean is A: anchor the carbon balance at the end as GEOCARB does, so bare early land
weathers less and the plants' arrival brings CO2 to the balance rather than below it.

## 5. What's left

- The draft decision, then re-measure with full Gough alone: 18 L6, 8 L7, 13 L6 at 2 Gyr. `launch.sh l6|l7|g2 RATE
  PREFIX` is ready (EXTRA=star_thermostat=1 for the thermostat).
- After that: the scorecard, PW-202's showcase remake, and the recipe offsets (hothouse, cold, water world).
- Coastal layers on the calendar: `draft-coastal-reefs-on-the-calendar.md`.
- Docs: the overview has no star section yet (audit item 14 of the star audit); README's star text needs the anchor.

Files: `launch.sh`, `passrate3.py`, `pr.sh`, `peek.py`, `terms.py`, `passrate_{g10,a045,t10}.txt`. Raw diagnostics
are in the session scratchpad v1f10/.
