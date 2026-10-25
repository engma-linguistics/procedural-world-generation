# v1 sign-off: the brightening star at 0.45 on Earth-like worlds (PW-780, 2026-10-24)

Earth-like presets only. Water worlds, hothouse and molten worlds are post-v1 (owner, 2026-10-24). The bar and its
thresholds are unchanged. The strict bar fails a run that is never-ice (icehouse < 5%), an always-icebox, or a
hellhole (median dT > 10.5 or max > 15.5).

## What 0.45 means

`star_brightening` 0.45 means the star brightens at 0.45 times a Sun-like star's rate on Gough's (1981) curve,
counted from the run's start (`earth.star_forcing`). That is roughly a K-type star of ~0.75 solar masses, which
evolves more slowly than the Sun. The planet gets +1.6 / +4.1 / +5.6 / +8.5 / +11.5 C of raw forcing at 300 / 744
/ 1000 / 1500 / 2000 Myr. The weathering thermostat draws CO2 down against it and absorbs part of it.

It is a chosen number, not a derived one. A Sun-like 1.0 makes 1 Gyr runs ice-free (16/18 never-ice). Rates
0.2-0.3 pass 12/18 and can't be told apart. 0.45 is the only rate tried that removed the late warming trend at L6
(v1-finish-7).

## Pass rates (strict bar)

The 1 Gyr numbers are v1-finish-7/8's. Since v1-finish-8 (1fa0aeb), only `planet/lineages` has changed, so they
stand on current main. The 2 Gyr L6 rows add six new re-rolled draws to v1-finish-8's seven.

| set | whole run (300 Myr to the end) | late window 1500-2000 | notes |
|---|---|---|---|
| L6 1 Gyr, 18 seed-draws | **13/18 (72%)** | - | 3 never-ice, 2 over 40% |
| L7 1 Gyr, 8 draws | **7/8** | - | no never-ice |
| L6 2 Gyr, 13 draws (7 old + 6 new) | **10/13 (77%)** | **4/13** | 1 hellhole (957317 +0.001, max +15.5), 2 too icy |
| L7 2 Gyr, 3 draws (2 old + 1 new, partial) | 1/2 judged | 0/2 judged | see below |

The six new L6 2 Gyr draws (`passrate_2g_L6.txt`):

| draw | 300-2000 icehouse | 300-1000 | 1000-1500 | 1500-2000 | dT median, late | max dT | verdict |
|---|---|---|---|---|---|---|---|
| seed 11 | 16% | 22 | 22 | 3 never | +8.1 | 12.4 | ok |
| seed 21 | 13% | 2 never | 39 | 2 never | +6.8 | 13.8 | ok |
| 583167 +0.001 | 50% | 65 | 44 | 35 | +3.4 | 12.4 | F, too icy |
| 619496 +0.001 | 14% | 25 | 12 | 0 never | +9.1 | 13.0 | ok |
| 639472 +0.001 | 30% | 45 | 25 | 14 | +3.7 | 8.9 | ok |
| 957317 +0.001 | 7% | 15 | 0 never | 2 never | +10.5 | **15.5** | **F, hellhole** |

- **At 1 Gyr, 0.45 passes the strict bar at about the agreed ~70%** (L6 72%, L7 7/8).
- **2 Gyr whole runs pass too (10/13), but the last 500 Myr does not (4/13).** From 1.5 Gyr the raw forcing is +10 C
  and the thermostat takes back only 2-6 C of it. The late window runs dT +7..+10.5, and 6 of the 13 are ice-free
  there. The first hellhole has appeared: 957317 +0.001 reaches +10.5 / 15.5, right on both lines. It is the same seed
  that sat at +6.0 late on v1-finish-8's draw, so this is chaos plus a drift toward hot.
- **L7 2 Gyr:** v1-finish-8's two draws were 1/2 whole-run strict (seed 12 never-ice), and both were ice-free at
  1500-2000. The new draw (957317, offset 0) was stopped at the compute limit. PARTIAL: see the last section.
  L7 runs warmer than L6 late, which is a lean toward ice-free, not hellhole.

So 0.45 is sound for the 1 Gyr Earth-like preset (`earthlike`, myr 1000). **A 2 Gyr Earth-like run's last 500 Myr is
a greenhouse planet**: mostly ice-free, with a hellhole now within reach.

## What an amateur geologist or hydrologist would find off

1. **The L7 showcase worlds are nearly treeless** (owner-visible; detail in
   `issue-tracking/inbox/draft-treeless-tropics-co2-heat.md`).

   | world | dT | pCO2 | trees | equatorial trees (rain) |
   |---|---|---|---|---|
   | 6fbc2c | +3.8 | 155 | 2.4% | 1.8% (2548 mm) |
   | a12762 | +4.6 | 142 | 1.7 | 1.2 (3010) |
   | 067778 | +0.8 | 221 | 9.6 | 3.1 |
   | 6909cb | +6.4 | 349 | 20.0 | 8.4 (3015) |
   | show-s21 e71172 (new) | +5.5 | 160 | 2.3 | 2.8 (2660) |
   | show-s11 2a7385 (new) | +6.5 | 277 | 15.8 | 8.1 (2918) |
   | bdded2, no star | -2.0 | 350 | 20.7 | 38.0 |
   | Earth 577526 | 0 | 350 | 31.4 | 34.1 |

   Wet tropics with 2500-3000 mm of rain carry 1-8% trees, where Earth carries ~34%.

   **Real, not a code regression.** It comes from two deliberate changes together. Since PW-646 (10-23) plants read
   the run's real pCO2. Since PW-761 (10-24) the star warms the slices by +4-5 C, and the thermostat answers by
   drawing CO2 down to 140-220 ppm. Then the plants' responses are too steep. On Earth's own climate, offline
   (`vegco2_full.py`, `vegshift.py`; rain held):
   - pCO2: 350 / 221 / 155 ppm gives 10 / 3.1 / 0.4% trees. Holocene Earth at 280 ppm would lose about half of its
     forest.
   - Warming: +3 / +6 C gives 5.3 / 2.4% equatorial trees, against 12% at today's temperature.
   - show-s21's own climate (e71172), offline: at its own 160 ppm, 0.6% trees and 1.6% equatorial; at 350 ppm, 5.2 / 7.0%;
     at 350 ppm and 5 C cooler (about its slice warmth taken off), 16.6 / 29.5%. Earth's climate gives 10 / 12% in the
     same rerun. Its geography and rain are forest-friendly; the CO2 and the warmth account for the whole gap.

   The LGM (185 ppm) and the Eocene (+5-10 C) both kept tropical forests. The time zoom's pick and a supercontinent
   interior are not the cause: wet equatorial lowland is treeless too. PW-290 (L7 drier than L6) adds to it, but it
   is not the main term.
2. **CO2 starvation late in long runs.** Over 1000-2000 Myr, pCO2 is below 180 ppm 23-82% of the time (median
   87-244 ppm; `pco2dist.py`). That is the K-star's thermostat doing what Earth's will do in ~1 Gyr
   (Lovelock & Whitfield 1982; Caldeira & Kasting 1992). With item 1's vegetation, it makes every late 2 Gyr world
   a grassland planet.
3. **Even the model's Earth has very little rainforest and hot desert.** It has 1.9-2.7% tropical rainforest and
   3.3-4.8% hot desert, against roughly 10-14% and 14-20% on the real Earth. This is the biome naming and the regional
   rain (PW-228). A reader will notice it on every world.

Nothing else stood out on the Earth-like worlds' summaries:
- relief: highest peaks 6-7 km, trenches 9-10 km, mean land 640-920 m;
- coasts: rocky and beach shores dominate, coral coasts in the tropics, fjords at high latitude;
- rivers: drainage lengths up to ~120 L7 cells;
- lakes: few (70-370 cells at L7).

## Tree cover in the v1 bar?

If it goes in, I would propose it as a plausibility range, judged on the representative slice at L7: global land
tree cover of **15-40%**, and **at least ~20% trees on land within 10 degrees of the equator that gets over 2000 mm
of rain**. Earth sits at 31% / 34%. The pre-star L7 worlds sit at 20-27% / 27-38%. Of the six star-default L7 showcases,
four would fail on the global range and all six on the wet tropics.

That is a proposal only; the threshold is yours. Fixing it means recalibrating the plants' CO2 and heat response
(the draft's option A). That is a v1-sized physics task, not a bar change.

## Files

- `passrate_2g_L6.txt`: the six new L6 2 Gyr draws, judged by v2-climate-1's `passrate2.py` (unchanged bar).
- `pco2dist.py`: pCO2 percentiles per window from the ice_diag json.
- `wetbelt.py`: land rain, temperature and trees per latitude band.
- `vegco2_full.py`, `vegshift.py`: the offline vegetation reruns on a world's stored climate.
- Runs: `docs/review/base-climate/v2-climate-2/launch.sh s6 / s6b / s7`, through `tools/ice_diag.py` on branch
  worktree-agent-af6c091bd3379671c. Its paused PW-798 change is a no-op on flat land: goldens are unchanged, and
  676 tests pass.

## L7 2 Gyr draw (957317, offset 0)

PARTIAL: stopped at 1500 Myr, at the ~80 min compute limit, so it has no json and is not judged on the bar.

| Myr | 100 | 200 | 300 | 400 | 500 | 600 | 700 | 800 | 900 | 1000 | 1100 | 1200 | 1300 | 1400 | 1500 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ice sea level, m | -2 | -2 | 0 | -23 | -7 | -15 | -3 | -7 | -50 | -15 | -3 | -9 | -4 | -13 | -7 |
| dT | +4.0 | +6.7 | +5.9 | +3.3 | +6.4 | +3.6 | +6.9 | +5.5 | +0.6 | +2.0 | +10.3 | +5.9 | +4.5 | +3.1 | +7.4 |

These are the log's one-in-100-Myr samples. Icehouse (ice at or below -20 m) shows at 400 and 900 Myr: 2 of 13
samples after 300 Myr, about 15%, a crude count. dT runs +0.6..+10.3, with a median of about +5.5. That reads as a
warm planet with occasional ice ages, likely an ok or a never-ice. It is not a hellhole so far, but the hot last
500 Myr were not reached.

**Question for the owner: do you sign off `star_brightening` 0.45 as the v1 default for Earth-like worlds (1 Gyr
passes at 72% L6 and 7/8 L7, but 2 Gyr runs end as a warm greenhouse), and should v1 also require forested wet
tropics, which means recalibrating the plants' CO2 and heat response before the tag?**
