# Final v1 release checks and hard-bar tally (lane 102, 2026-11-01)

## In plain words

**On the final physics code, none of the 42 re-rolled worlds fails a hard bar.** Zero frozen over, zero boiled, zero lost
their oceans, and zero had a CO2 crash under Daniel's D32 ruling (option B: CO2 below the plants' own compensation point).
The soft scorecard passes at 29 of 36 at L6 (81%, bar about 70%) and 5 of 6 at L7. The L7 Earth check reads the same
as before (Köppen main-group agreement 70%, was 71%). Nothing here is tuned or changed; I only measured.

- **The crash count depends on the line, and I do not pick one.** Under option B (D32, the headline): **0 of 42**.
  Under "CO2 under 100 ppm": **3 of 42** (all L6). Under "falls 8-fold in 50 Myr and does not recover": **25 of 42**
  by the loose reading (end value at most a quarter of the pre-fall value) or **22 of 42** by the strict reading
  (end value at most twice the bottom of the fall). The 8-fold line catches about half of all draws because pCO2
  swings by 8x or more inside 50 Myr in most worlds, even ones that bottom out near 200 ppm, so as defined it is not
  a rare-event line. The lowest any draw gets is 83 ppm. The plants' compensation point sits at only 18 to 38 ppm
  (it depends on temperature), so no draw comes within a factor of 2.5 of it.
- **The dry shift lane 98 saw (18.8 to 22.9%) is real on those six scorecard worlds, and it is not a shift in the
  model.** The six scorecard seeds again come out at 23.0% dry (was 18.8% at the old baseline, 22.9% in lane 98's run).
  But the 36 re-rolled L6 draws, the evidence you asked for, show **no shift**: arid land is 23.1% on lane 92's code
  and 23.2% on today's, a paired difference of +0.09 points (standard error 0.54), up in 20 draws and down in 16.
  The old scorecard's 18.8% was the low outlier of a distribution centered near 23%. I read PW-1234 as chaos plus an
  unlucky baseline, not a mechanism. The scorecard's NPP (412 to 372) and tree cover (41.2 to 36.0%) did fall on the six
  seeds; the draws' own tree column is not reliable (see notes), so I cannot say whether that part is real. One honest limit: the 36 draws and the
  scorecard measure arid land slightly differently (climate-diagnostic median vs scorecard dry land at 1000 Myr).
- The Earth check moved in two places, both already explained by lane 98's inland-pits write-up: the Atlantic's E-P-R
  (+0.54 to +0.12 Sv, a bookkeeping correction) and the 78-city point check (41 exact to 37 exact, same wrong-group count of 20).

## Setup

- Code: main at `6837941e` (inland pits PW-1229 and plant CO2 floor PW-1227 merged), frozen with `git archive` into
  scratch. Main has since moved (lane 109 and others, now merged into this branch); the diff from `6837941e` touches
  only `planet/lineages/`, `nest.py`, `refine.py`, `server.py`, `world.py`, `zoom/stage_terrain.py`, tests and docs,
  nothing in `climate.py`, `vegetation.py` or `tectonics/`, so the numbers stand for the current tip.
- Draws: the same as lane 92. L6: the 18 seed-draws of `v1-finish-16/paired.sh` at rolls 0.0005 and 0.001 (36 pooled),
  1 Gyr, `star_brightening=1.0`. L7: the 4 `l6fix` seeds at roll 0.0005, plus seeds 957317 and 619496 at roll 0.001 (6).
- Caps kept: 6 L6 and 2 L7 sims at once, 2 numba threads each (about 16 cores).
  Wall time 18:58 to 23:29 + 2 h for the last pair of L7 draws.
- The harness is now `tools/hard_bar.py` (moved from `docs/review/v1-cut/tally.py`; PW-1223 asked for this):
  `uv run python tools/hard_bar.py DIR_ROOT LEVEL`. Its hard CO2 crash is D32 option B: at any step after 300 Myr,
  pCO2 below `vegetation._gstar(T) / 0.7`, T the global mean true temperature of that step. (The plant code works
  with ci = 0.7 Ca, so the ambient compensation point is G* / 0.7.) Secondary rows: under 100 ppm, under 60, under 50,
  and the two 8-fold readings, defined below. Older notes that mention `v1-cut/tally.py` mean this file.
- The Köppen download failed again, so earth_check and the scorecard ran from a `git archive` copy with `data/earth`
  copied to scratch. Nothing was written into `data/earth`. The same code, so the same numbers.

## 1. Hard-bar tally

| Hard failure | L6 (36) | L7 (6) | Pooled (42) |
|---|---|---|---|
| Frozen over in the judged window (40% of land under ice) | **0** | **0** | **0** |
| Boiled / hellhouse | **0** | **0** | **0** |
| Ocean loss (ocean share under 40% or abs sea level over 1000 m, after 300 Myr) | **0** | **0** | **0** |
| **CO2 crash, D32 option B (pCO2 under the plants' compensation point)** | **0** | **0** | **0** |
| (secondary) pCO2 under 100 ppm | 3 | 0 | 3 |
| (secondary) pCO2 under 60 ppm | 0 | 0 | 0 |
| (secondary) pCO2 under 50 ppm | 0 | 0 | 0 |
| (secondary) 8-fold fall in 50 Myr, end at most 1/4 of pre-fall | 21 | 4 | 25 |
| (secondary) 8-fold fall in 50 Myr, end at most 2x the bottom | 19 | 3 | 22 |

Definition of the 8-fold rows (mine, since none was written down): from t0 at or after 300 Myr, pCO2 falls to at
most 1/8 of its t0 value within 50 Myr, and at the end of the run it is still at most 1/4 of the t0 value (loose) or at most twice the
lowest value reached in that 50 Myr (strict). `worst50` in the tally files is the lowest 50-Myr ratio any draw reaches (0.03 to 0.15).

| Soft measure | L6 roll 0.0005 | L6 roll 0.001 | L6 pooled | L7 |
|---|---|---|---|---|
| Soft pass (bar + finish moment) | 15/18 | 14/18 | **29/36 (81%)**, bar ~70% | **5/6** (bar ~60%) |
| Frozen over any time after 300 Myr (reported) | | | 1/36 | 0/6 |
| Icehouse (reported) | | | 36/36 | 6/6 |
| End pCO2 outside 180-600 ppm (diagnostic) | | | 10/36 | 2/6 (one low, one high) |

Lane 92 had 28/36 and 5/6, so the soft pass is flat within noise.

## 2. Minimum pCO2 per draw

Ascending, all 42 draws. T is the global mean true temperature at the draw's minimum step, dT is that minus 13.8 C
(pre-industrial), "comp" is the plants' compensation point at that T (G*/0.7, ppm). Full table with the 8-fold flags:
`final-tally_L6.txt`, `final-tally_L7.txt`.

Counts: under 50 ppm **0**, under 60 ppm **0**, under 100 ppm **3**, below the compensation point at any step **0**.

| min pCO2 ppm | draw | t Myr | T at min C | dT | comp ppm |
|---|---|---|---|---|---|
| 83.3 | L6 r0.001 l6fix 639472 | 946 | 5.2 | -8.6 | 20.7 |
| 90.4 | L6 r0.0005 l6c_p 619496 | 948 | 5.8 | -8.0 | 21.3 |
| 91.0 | L6 r0.001 l6c_0 958504 | 864 | 3.4 | -10.4 | 18.5 |
| 106.0 | L6 r0.0005 l6c_p 639472 | 976 | 5.1 | -8.7 | 20.5 |
| 109.0 | L6 r0.001 l6fix 583167 | 880 | 8.8 | -5.0 | 25.4 |
| 111.1 | L7 r0.0005 l6fix 619496 | 956 | 5.3 | -8.5 | 20.7 |
| 117.9 | L6 r0.0005 l6c_p 819014 | 732 | 3.7 | -10.1 | 18.9 |
| 118.0 | L6 r0.001 l6c_p 583167 | 850 | 5.3 | -8.5 | 20.8 |
| 118.1 | L6 r0.0005 l6c_0 53669 | 995 | 7.2 | -6.6 | 23.1 |
| 119.2 | L6 r0.0005 l6fix 957317 | 798 | 4.2 | -9.6 | 19.4 |
| 119.5 | L7 r0.001 l6fix 957317 | 876 | 7.4 | -6.4 | 23.4 |
| 121.9 | L6 r0.0005 l6c_m 958504 | 850 | 10.4 | -3.4 | 27.8 |
| 127.9 | L6 r0.001 l6c_p 819014 | 948 | 9.9 | -3.9 | 27.1 |
| 128.6 | L6 r0.0005 l6c_0 819014 | 990 | 8.9 | -4.9 | 25.6 |
| 130.8 | L6 r0.0005 l6c_0 958504 | 988 | 7.6 | -6.2 | 23.8 |
| 132.1 | L6 r0.0005 l6c_p 733847 | 902 | 9.7 | -4.1 | 26.7 |
| 132.2 | L6 r0.0005 l6c_p 583167 | 982 | 10.2 | -3.7 | 27.4 |
| 132.4 | L6 r0.0005 l6c_0 733847 | 940 | 7.9 | -5.9 | 24.2 |
| 134.9 | L6 r0.0005 l6c_p 958504 | 688 | 5.8 | -8.0 | 21.4 |
| 138.9 | L7 r0.001 l6fix 619496 | 998 | 8.2 | -5.6 | 24.5 |
| 142.1 | L6 r0.001 l6c_p 733847 | 974 | 8.5 | -5.3 | 25.0 |
| 163.8 | L7 r0.0005 l6fix 583167 | 632 | 7.9 | -5.9 | 24.1 |
| 168.8 | L6 r0.001 l6fix 957317 | 876 | 6.3 | -7.5 | 21.9 |
| 175.1 | L6 r0.001 l6c_0 733847 | 918 | 9.4 | -4.4 | 26.2 |
| 181.7 | L6 r0.0005 l6c_m 53669 | 966 | 13.4 | -0.4 | 32.9 |
| 183.2 | L6 r0.001 l6c_m 958504 | 980 | 13.1 | -0.7 | 32.4 |
| 190.5 | L6 r0.0005 l6fix 639472 | 818 | 11.3 | -2.5 | 29.3 |
| 191.3 | L6 r0.001 l6c_p 958504 | 872 | 8.1 | -5.8 | 24.3 |
| 195.1 | L6 r0.001 l6c_m 53669 | 1000 | 10.5 | -3.3 | 28.0 |
| 195.9 | L6 r0.001 l6c_0 53669 | 852 | 11.1 | -2.7 | 29.0 |
| 197.7 | L6 r0.0005 l6c_p 957317 | 978 | 13.2 | -0.6 | 32.5 |
| 200.1 | L7 r0.0005 l6fix 639472 | 746 | 8.7 | -5.1 | 25.3 |
| 217.2 | L7 r0.0005 l6fix 957317 | 852 | 11.2 | -2.6 | 29.1 |
| 221.8 | L6 r0.001 l6c_0 819014 | 882 | 13.2 | -0.6 | 32.7 |
| 230.4 | L6 r0.0005 l6fix 583167 | 956 | 13.9 | +0.1 | 33.8 |
| 280.2 | L6 r0.0005 l6c_p 53669 | 998 | 14.5 | +0.7 | 34.9 |
| 283.3 | L6 r0.001 l6c_p 639472 | 878 | 13.9 | +0.1 | 33.8 |
| 285.9 | L6 r0.001 l6c_p 957317 | 892 | 8.7 | -5.1 | 25.3 |
| 332.5 | L6 r0.001 l6c_p 53669 | 712 | 10.6 | -3.2 | 28.1 |
| 361.3 | L6 r0.001 l6c_p 619496 | 812 | 15.9 | +2.1 | 37.8 |
| 372.3 | L6 r0.0005 l6fix 619496 | 1000 | 15.8 | +2.0 | 37.6 |
| 586.8 | L6 r0.001 l6fix 619496 | 556 | 10.9 | -2.9 | 28.6 |

Reading: the three draws under 100 ppm all bottom out in the last 150 Myr in worlds 8 to 10 C colder than
pre-industrial, where the plants' compensation point is 18 to 21 ppm. The model's weathering feedback holds
the floor at about 4 times that. The lowest draw (83 ppm) is lane 95's old crash draw, now at 83 instead of 36 ppm.

## 3. L7 earth_check (vs `earth_check_L7.txt`, lane 92)

| Number | Lane 92 | Now |
|---|---|---|
| Köppen main-group agreement / exact (excl. Antarctica) | 71% / 38% | **70% / 37%** |
| Group shares A/B/C/D/E (model) | 20.2/25.2/19.0/23.6/12.0 | 20.1/25.0/19.2/23.9/11.8 (Kottek 21.9/30.1/15.9/24.8/7.3) |
| Global mean T / P (model) | 13.9 C / 996 mm | 13.9 C / 996 mm (NCEP 14.0, GPCP 983) |
| Land rain vs GPCC; log-rain correlation | x1.33; 0.717 | x1.34; 0.714 |
| Dry land B / BWh (model; obs 30.1 / 14.8) | 25.2 / 13.1 | 25.0 / 12.9 |
| Point check (78 cities) exact / group / wrong | 41 / 17 / 20 | 37 / 21 / 20 |
| Runoff / rain on land | 0.50 | 0.50 |
| Land draining to closed basins | 23% | 23% |
| Atlantic E-P-R; Atlantic minus Pacific | +0.54 Sv; +137 mm/yr | +0.12 Sv; -55 mm/yr (PW-016 wants +100) |

Group agreement is within a point, so the "stop and diagnose" trigger (about 70% disagreeing) is not met. The Atlantic
E-P-R is lane 98's documented correction (`inland-pits.md`, "a correction, not a climate change"); PW-016's target still
fails, as it did before. Full output: `final-earth_check_L7.txt`.

## 4. L6 scorecard (seeds 1-6, 1000 Myr) vs `scorecard_L6.txt`

Earth line (L6): group agreement 71.1% (was 71.1%), exact 38.2% (38.4%), log-rain corr 0.718 (0.721).

| Per seed (1..6) | Lane 92 baseline | Now | Mean old to new |
|---|---|---|---|
| Land % | 31.6, 34.5, 34.3, 33.9, 35.0, 34.9 | 34.3, 33.9, 34.5, 35.3, 34.0, 34.7 | 34.0 to 34.4 |
| Dry land % | 20.0, 18.5, 19.7, 17.9, 20.8, 16.0 | 25.0, 18.8, 27.9, 24.6, 21.5, 20.4 | **18.8 to 23.0** |
| Land NPP g C/m2/yr | 462, 411, 276, 495, 422, 405 | 388, 285, 423, 278, 425, 433 | 412 to 372 |
| Tree cover % | 42.8, 41.6, 34.9, 49.7, 40.3, 38.1 | 33.4, 30.9, 34.8, 29.9, 46.8, 39.9 | 41.2 to 36.0 |
| Largest plate (max) % | 24.9 (54.7), 29.9 (37.6), 15.7 (34.3), 17.2 (31.6), 15.8 (47.4), 39.8 (74.4) | 17.9 (42.6), 38.0 (67.3), 34.0 (62.5), 27.2 (57.5), 19.1 (25.8), 54.8 (54.8) | |
| Peak elevation m | 6801, 7899, 6588, 4015, 6735, 7437 | 4421, 8295, 6524, 5785, 3746, 5470 | |
| Ocean age Myr | 54.2, 67.9, 60.8, 49.2, 53.2, 102.3 | 49.1, 66.3, 54.6, 56.8, 50.8, 55.6 | |

Dry land is the seed-by-seed move PW-1234 describes. It reproduces: 23.0% against lane 98's 22.9%. The land share is
back at 33.9 to 35.3% (the old seed 1 low of 31.6% is gone). Seed 5 has a 3.7 km peak (no mountains over 4 km), and
seed 2 a 8.3 km peak. Tracked, no threshold applies. One scorecard line appended to `docs/scorecard.jsonl`.

### Does the dry shift hold up (PW-1234)?

| Measure, same 36 L6 draws | Lane 92 code (before pits and floor) | Today | Paired difference |
|---|---|---|---|
| Arid land % (median, 50-1000 Myr) | 23.1 (sd 2.1) | 23.2 (sd 2.4) | +0.09 (se 0.54); up in 20 of 36 |
| Peak land ice % | 25.5 | 25.7 | +0.16 (se 2.0) |

No shift on the 36. The six scorecard worlds' move (18.8 to 23.0) is the baseline's six being low, plus the chaos
every code change causes (any change re-rolls each world's plates). The scorecard's tree cover and NPP drops
may be the same story; the draws' tree column is a median including the pre-vegetation updates and is unusable for this, so
I could not test them on the 36 (the median moved +0.07 points, but see that caveat). If you want trees and NPP closed out, run seeds 7-18 on
both codes, as PW-1234 suggests; I did not.

## 5. Files

`final-tally_L6.txt`, `final-tally_L7.txt` (per-draw tables, min-pCO2 lists with T and compensation point, counts),
`final-earth_check_L7.txt`, `final-scorecard_L6.txt` here; the harness is `tools/hard_bar.py`. Scratch sims deleted.
The draws' `.json.gz` files went with the scratch.
