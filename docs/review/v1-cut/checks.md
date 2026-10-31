# v1.0 release checks and hard-bar tally (lane 92, 2026-10-31)

## In plain words

**Not quite clear to tag, and the reason is one world out of 42.** Across 36 re-rolled L6 draws and 6 L7 draws, zero worlds were frozen over in the judged window, zero were boiled, and zero lost their oceans. The soft scorecard passes at 78% at L6 (28 of 36) and 5 of 6 at L7, both above the bar. The Earth check at L7 and the 6-seed scorecard at L6 both read the same as the 10-30 numbers (main-group Köppen agreement 71%). The L7-drier-than-L6 gap (PW-290) is now small: about 2 points of arid land, not the 10 points the health sweep saw. The one problem: one L6 draw (seed 639472, second roll) ends in a CO2 crash. Its CO2 falls to 36 ppm in the last 70 Myr and the world finishes 10 C below pre-industrial, with 24% of the land under ice, so the frozen-over test (40%) does not catch it. The volcanic CO2 source falls by about 70% in those last Myr. Your two-tier bar says CO2 crash must be zero, but nobody has set a number for "crash". I used "pCO2 under 100 ppm at any step after 300 Myr", which is my definition, not yours. By that definition it is 1 hard failure in 42 draws (the other dip, 88 ppm, recovered to 327 ppm by the end). If you rule that a crash this late is a v1 blocker, PW-1156 and PW-1158 come back. If you rule that one in 36 is acceptable, or that the definition is wrong, the tag is clear. That call is yours; I have not loosened or re-tuned anything.

## Setup

- Code: commit `e5b526ff` (HEAD when the lane started), frozen with `git archive` into the scratchpad so other lanes' edits could not leak into the draws. By the time the earth_check and scorecard ran, main had moved to `1a64cd7c` (lane 83 merge); that diff touches only `planet/lineages/` and `tools/peoples_robust.py`, no climate code.
- Machine: load average 20 to 50 the whole time (L8 peoples run, peoples stress suite, megafauna probes). Caps kept: at most 8 L6 sims, at most 2 L7 sims. /tmp never went above 4.4 GB used.
- Wall time: first sim started 06:14, last result 09:46 (3 h 32 min). The L6 batch of 36 took 06:14 to 08:18 (2 h 04 min); the L7 batch of 6 took until 09:46 (it ran at 95 min per draw under heavy load early, about 50 min later).
- The judge: `docs/review/base-climate/v1-finish-12/passrate4.py` (`judge`) and `tools/ice_criteria.py` (`hard_window`), the finish moment from `planet/highlights.py`, as `v1-finish-16/pjudge.py` uses them. Draw sets and the launcher are `v1-finish-16/paired.sh` (its 18 seed-draws, `star_brightening=1.0`, 1 Gyr, rolls added to each draw's climate_offset). New harness in this folder: `tally.py` (hard-bar tally), `pairs290.py` (PW-290 pairs).

## 1. Hard-bar tally

Commands (scratch under `/tmp/claude-1000/.../scratchpad/l92/`, deleted after; the per-draw tables are kept here):

```
PY=$PWD/.venv/bin/python MAXSIM=8 bash docs/review/base-climate/v1-finish-16/paired.sh $S/code $S/l6 m 0.0005 0.001
LEVEL=7 ONLY=l6fix THREADS=5 PY=$PY MAXSIM=2 bash docs/review/base-climate/v1-finish-16/paired.sh $S/code $S/l7 m 0.0005 0.001   # stopped after 6 draws
uv run python docs/review/v1-cut/tally.py $S/l6 6    # -> tally_L6.txt
uv run python docs/review/v1-cut/tally.py $S/l7 7    # -> tally_L7.txt
```

L6: rolls 0.0005 and 0.001 of the 18 draws (36 pooled). L7: the 4 `l6fix` seeds at roll 0.0005 plus seeds 957317 and 619496 at roll 0.001 (6 draws).

| Hard failure | L6 (36 draws) | L7 (6 draws) | Definition |
|---|---|---|---|
| Frozen over in the judged window | **0** | **0** | `passrate4.judge` frozen: 40%+ of the land under ice inside `ice_criteria.hard_window` |
| Boiled / hellhouse | **0** | **0** | `passrate4.judge` hell: dT median > +10.5 C or max > +15.5 C |
| Ocean loss | **0** | **0** | lane 92's definition: ocean share of the surface < 40% or abs(sea level) > 1000 m at any step after 300 Myr (lowest ocean share seen 61.2%, highest abs sea level 611 m) |
| CO2 crash | **1** (plus one recovered dip) | **0** | lane 92's definition: pCO2 < 100 ppm at any step after 300 Myr |

| Soft measure | L6 roll 0.0005 | L6 roll 0.001 | L6 pooled | L7 |
|---|---|---|---|---|
| Soft pass (bar + finish moment) | 13/18 | 15/18 | **28/36 (78%)**, bar ~70% | **5/6**, bar ~60% (too few draws for a rate) |
| Deep-time bar alone (300 Myr to end) | 18/18 | 18/18 | 36/36 | 6/6 |
| Frozen over any time after 300 Myr (reported only) | 2 | 1 | 3/36 | 0/6 |
| Icehouse (permanent polar sheets, reported only) | | | 34/36 | 6/6 |
| End pCO2 outside 180-600 ppm (diagnostic) | | | 14/36 | 4/6 (all above) |

Notes.
- The 3 L6 draws that touched 40% land ice (peak 42.0, 41.7 and 42.9% of land: `l6c_0` 53669 and `l6fix` 957317 at roll 0.0005, `l6c_p` 583167 at roll 0.001) did so only outside the hard window (the star was still dim), so under the owner's PW-1142 rule they are reported, not failures. I did not need the polar-continent excuse for any world.
- The 8 L6 soft fails are the finish moment missing (the `fm` column in `tally_L6.txt`) while the 300 Myr to end bar passed; all 8 passed the deep-time bar.
- L7 seed 583167 (roll 0.0005) is a soft fail: end true mean T +8.3 C above pre-industrial, end pCO2 2108 ppm. It is not a hellhouse by the dT test (zero draws failed it).
- **The CO2 crash**: `l6fix` seed 639472 at roll 0.001 (climate_offset 0.002). pCO2 373 ppm at 952 Myr, 54 at 993, 36 at 1000; dT -10.2 C; true mean T 3.9 C (9.9 C under pre-industrial); land ice peak 33.7%; finish moment fails. On the step record `source_raw` goes from 3238 at 930 Myr to 890 at the end while the sink's raw value only falls from 673 to 406. This is the source-variance mechanism behind PW-1156 and PW-1158, now appearing without a frozen-over world. The recovered dip: `l6c_p` seed 733847 roll 0.001, minimum 88 ppm, end 327 ppm. Both are listed in the draft below.
- The `trees` column in `tally_L6.txt` is a median over all updates from 50 Myr and includes the early updates before the plants spread (some read 0.0); ignore it. It is not part of any bar.

## 2. L7 earth_check

`uv run python tools/earth_check.py --level 7 --json $S/earth7.json` (about 2 min). Full output: `earth_check_L7.txt`.

| Number | Value |
|---|---|
| Köppen main-group agreement with Kottek (land excl. Antarctica) | **71%** (exact code 38%) |
| Group shares A/B/C/D/E, model vs Kottek (excl. Antarctica) | 20.2/25.2/19.0/23.6/12.0 vs 21.9/30.1/15.9/24.8/7.3 |
| Global mean T, model vs NCEP | 13.9 vs 14.0 C |
| Global mean P, model vs GPCP | 996 vs 983 mm/yr |
| Land rain mean, model vs GPCC | 1053 vs 791 mm/yr (x1.33); log-rain correlation 0.717 |
| Point check | 41/78 exact, 17/78 group only, 20/78 wrong group |
| Dry land (B), model vs obs | 25.2 vs 30.1% (BWh 13.1 vs 14.8) |
| Rivers: runoff / rain on land | 0.50 (Earth about 0.35-0.40) |
| Land draining to closed basins | 23% (Earth about 18%) |
| Biggest auto-ranked misses | Greenland coldest month -14.4 C, Alaska -10.2 C, NE China coldest month +8.5 C, East Africa precip x4.1, Sahel x3.5 |

The plan's trigger ("if group agreement disagrees with the 10-30 numbers, about 70%, stop and diagnose") is not met: 71% matches. The known soft misses (Greenland, rain on coasts, summer winds) are the ones the plan lists as v1 limits.

## 3. Scorecard, 6 seeds at L6

`uv run python tools/scorecard.py --seeds 1 2 3 4 5 6 --myr 1000 --jobs 7` (1120 s, 18.7 min; it appended one line to `docs/scorecard.jsonl`). Output: `scorecard_L6.txt`.

| Item | Result |
|---|---|
| Earth (L6): group agreement / exact | 71.1% / 38.4%; shares A/B/C/D/E 20.3/25.0/19.4/23.8/11.4; log-rain corr 0.721 |
| Land % at 1000 Myr, seeds 1-6 | 31.6, 34.5, 34.3, 33.9, 35.0, 34.9 |
| Crust % | 40.5, 41.1, 41.1, 41.9, 41.3, 43.0 |
| Volume ratio | 0.998, 1.017, 0.991, 0.979, 1.026, 1.021 |
| Largest plate (max over run) % | 24.9 (54.7), 29.9 (37.6), 15.7 (34.3), 17.2 (31.6), 15.8 (47.4), 39.8 (74.4) |
| Tree cover % | 42.8, 41.6, 34.9, 49.7, 40.3, 38.1 |
| Land NPP g C/m2/yr | 462, 411, 276, 495, 422, 405 |
| Ocean age Myr | 54.2, 67.9, 60.8, 49.2, 53.2, 102.3 |
| Peak elevation m | 6801, 7899, 6588, 4015, 6735, 7437 |
| Dry land % | 20.0, 18.5, 19.7, 17.9, 20.8, 16.0 |

Seed 4 has no mountains over 4 km (0.01% of land) and a 4015 m peak; seed 6 has the largest plate at 74.4% at its peak and ocean age 102 Myr. These are the known plate-size peaks (PW-969, v2), not new. No threshold applies to the scorecard (it is tracked, not pass/fail); the land share (31.6 to 35.0%) is in the PW-980 plausibility-miss band already on the board.

## 4. PW-290 pairs (L7 vs L6, same seed, same offset)

The tally draws are exactly such pairs, so no extra sims were needed: the 6 L7 draws against their L6 twins (4 seeds: 583167, 619496, 639472, 957317; 2 at both rolls). `uv run python docs/review/v1-cut/pairs290.py $S/l6 $S/l7`. Medians over the climate updates in 50 to 1000 Myr. Output: `pairs290.txt`.

| Draw | Köppen B % L6 / L7 | Difference | BWh % L6 / L7 | Land rain mm/yr L6 / L7 |
|---|---|---|---|---|
| 583167 r0.0005 | 21.9 / 24.1 | +2.2 | 7.7 / 10.8 | 1099 / 1184 |
| 619496 r0.0005 | 25.0 / 27.1 | +2.0 | 11.4 / 12.4 | 1116 / 1139 |
| 639472 r0.0005 | 24.1 / 23.1 | -1.1 | 10.5 / 10.0 | 1234 / 1076 |
| 957317 r0.0005 | 19.9 / 22.1 | +2.2 | 6.9 / 8.7 | 1079 / 1124 |
| 619496 r0.001 | 24.1 / 26.7 | +2.6 | 9.8 / 10.6 | 995 / 1095 |
| 957317 r0.001 | 23.5 / 20.5 | -3.0 | 8.2 / 6.9 | 1033 / 1074 |
| **Median / mean** | mean 23.1 / 23.9 | **+2.1 median**, L7 drier in 4 of 6 | | median +43 mm/yr |

Reading: PW-290 filed a gap of about 10 points of arid land (L6 28-30%, L7 38-42%) in the 10-15 health sweep. Under today's main the gap is about 2 points on median and the sign is mixed (2 of 6 pairs go the other way). Caveats: these are the 1 Gyr, star_brightening=1.0 climate-diag runs, not the health sweep's `planet simulate` runs, and 6 pairs is a small sample, so I cannot say the ticket is closed, only that this method does not reproduce the 10-point gap. The B share reads lower than the health sweep at both levels (L6 about 23% here, 28-30% there), so the two metrics are not the same measure; the paired difference is the comparable quantity. Tree cover moves -0.2 points on median.

## Follow-ups (drafts, now numbered by the coordinator)

- PW-1224 (`issue-tracking/tickets/PW-1224-*.md`, from the lane 92 draft): the one CO2 crash draw, needs a written diagnosis and a blocker ruling (impact high).
- PW-1223 (`issue-tracking/tickets/PW-1223-*.md`, from the lane 92 draft): needs-decision: ocean loss and CO2 crash have no owner-set numbers; lane 92's definitions are in `tally.py`; move it under `tools/`.

## Files

`tally.py`, `pairs290.py` (harness), `tally_L6.txt`, `tally_L7.txt`, `pairs290.txt`, `earth_check_L7.txt`, `scorecard_L6.txt` in this folder. The draws' `.json.gz` files were deleted with the scratch (about 40 files); rerun the commands above to regenerate. No registered runs, worlds or zooms were created, so nothing needed `planet delete`.
