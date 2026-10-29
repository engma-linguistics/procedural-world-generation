# Lane 25: deserts and the sea's moisture source (PW-015 with PW-821), and the paired merge judge (PW-994), 2026-10-29

## Verdict
- **PW-994 is done:** `../v1-finish-16/pjudge.py` and a generic `../v1-finish-16/paired.sh`. How to use them is in
  that folder's README.
- **PW-015, round 1, is committed on the branch (5840dcc6). Sea evaporation is now a bulk exchange.** Earth's B share is
  now 27.3% of land (L7 27.6%) against Kottek's 30.1, up from 20.3%. Hot desert is 14.5% against 14.8. The cell-by-cell
  rain pattern improved (log-rain corr 0.648 -> 0.691) and so did the sea's evaporation pattern. The cost is that
  several subtropical coasts dry out (SE USA, Pampas, Japan, E Australia, Mediterranean).
  - On generated worlds (the paired judge), arid land rises +6.7 points and trees fall -4.2 points. The carbon cycle
    doesn't move, and passes go 29 -> 27 of 36, inside the noise.
  - One test fails: the L4 sea-level warm-up bar, on seed 1 (draft).
  - The coordinator decides the merge.
- **The B deficit is mostly not the sea's moisture source.** It is the land's import of vapour through the land-sea
  (monsoon) circulation, which has no return flow aloft. Round 2 tried that mechanism. It is real, but it needs a depth
  rule per cell. A uniform one made the rain pattern and India worse, so it was dropped (draft for v2).

## Diagnosis (Earth L6, main ed7e87ab; `diag_b.py`, `tools/moisture_budget.py`)
- **Temperatures are not the problem.** The model's temperatures with GPCC's half-year rain give B = 28.8%. The rain is
  what is wrong.
- **Land is ~1.4x too wet.** Land rain is 1122 against GPCC's 791. Runoff/rain is 0.49 against 0.38 when GPCC's rain is
  routed. So land imports ~1.9x the net vapour it should (550 against ~300 mm). Scaling land rain by 0.7 would give
  B 27.4%.
- **Where the obs-B land the model misses lies** (13.8% of land; false B 4.0%). All of it is the local summer:

| box | missed (% of land) | model / GPCC rain there, Jul / Jan | went to |
|---|---|---|---|
| Sahel / W Africa 8-20N | 3.35 | 11.0 / 4.4 | A 48%, C 52% |
| Australia | 2.23 | 1.2 / 3.5 | C 91% |
| S Africa | 1.61 | 1.2 / 2.7 | C 98% |
| N America west | 1.26 | 2.4 / 2.2 | D 82% |
| Mongolia / N China | 1.15 | 4.9 / 0.8 | D 96% |
| C Asia / Iran | 1.04 | 4.0 / 1.5 | C/D |
| E Africa / Horn | 0.92 | 7.8 / 6.0 | A 89% |

- **The vapour is near observed; the rain on it is not.** In those regions' summers the column vapour is 0.9-1.35x
  NCEP's, while the rain per unit of vapour is 2.5-8x observed. Sahel Jul: PW 40 vs 35 mm, rain 4775 vs 1108 mm/yr.
  Gobi Jul: 11 vs 12.5 mm, 1144 vs 278. Australia Jan: 32 vs 25 mm, 1384 vs 431.
- **The rain is supply-limited, not rate-limited.**
  - Turning off the showers' ITCZ boost (`itcz_cv` 0), narrowing the rain belt (`itcz_w` 6), doubling the
    suppression under the sinking air (`cv_sink` 1) or removing the dry-ground heating (`evap_cool` 0): the Sahel stays
    at 2380-2540 mm and B at 19.7-22.2%.
  - PW-821's shower humidity gate gives B 22.5. It dries the Gobi and C Asia, not the Sahel or Australia, whose
    q/qs is 0.64-0.76.
  - What sets the rain is how much vapour the wind brings in. The monsoon wind's strength at 0.5 gives B 27.8%, land
    rain 970 and Sahel 1769.
- **The sea's instant refill is wrong in its own right.** Sea evaporation came out as whatever left the air: 0-10N 830
  against NCEP 1407, 20-30N 2357 against 1689, -30..-20 2147 against 1596. Every strip of sea saturated the air that
  crossed it.

## Round 1: sea evaporation as a bulk exchange (`climate.sea_uptake`, 5840dcc6)
- **Mechanism.** Each rain step, the open sea's air takes up 1 - exp(-open x C_E x max(U, 3 m/s) / h x dt) of its
  deficit to 0.98 x q_sat(SST). C_E is 1.3e-3. h = 500 m is the marine boundary layer that the flux fills, which gives
  ~0.6 days or ~400 km of fetch at 7 m/s. The 0.98 is saturation over salt water. Leads take up water per unit of
  time. `rh` 0.85 stays the showers' reference air aloft.
- **Variants on Earth L6.** h = 500 m was not fitted to B. Every 0.98 variant in this table improves the rain pattern,
  so the choice of h barely matters there.

| variant | B % | BWh % | exact / group % | log-rain corr | land P (791) | SE USA (1328) |
|---|---|---|---|---|---|---|
| main (instant refill to 0.85) | 20.3 | 9.0 | 34 / 71 | 0.648 | 1122 | 1109 |
| lane A's: target 0.85, h 1 km | 30.9 | 18.0 | 36 / 70 | 0.650 | 1224 | 121 |
| target 0.85, h 2 km | 34.8 | 20.5 | 37 / 69 | 0.612 | 1215 | 32 |
| target 0.98, h 2 km | 33.5 | 19.5 | 36 / 70 | 0.635 | 1186 | 48 |
| target 0.98, h 1 km | 29.8 | 17.0 | 35 / 70 | 0.670 | 1134 | 209 |
| target 0.98, h 700 m | 28.3 | 15.5 | 36 / 71 | 0.684 | 1087 | 347 |
| **target 0.98, h 500 m (committed)** | **27.3** | **14.5** | **36 / 71** | **0.691** | **1038** | **482** |
| target 0.98, h 300 m | 26.5 | 13.4 | 37 / 71 | 0.694 | 970 | 648 |
| Kottek / GPCC | 30.1 | 14.8 | | | 791 | 1328 |

- With the 0.85 target, the sea's air stays well below it, sea rain collapses and the land gets wetter. The 0.85 is
  the instant refill's equilibrium, not the sea surface's humidity; this answers lane A's open question.
- **Committed, Earth L6 and L7.**
  - L6: B 27.3, BWh 14.5, BSh 4.3 (6.7), exact 36, group 71, corr 0.691, land rain x1.31.
  - L7 (main): B 27.6 (19.6), exact 36 (33), group 70 (70), corr 0.687 (0.621), land rain 1046 (1138).
  - Scorecard: Earth group 70.9 (main 71.2), exact 36.1 (33.9).
- **Sea evaporation by band, model / NCEP (mm/yr)** (main in brackets): 0-10N 1375 / 1407 (830); -10..0 1418 / 1407
  (1094); 20-30N 2014 / 1689 (2357); 30-40N 1545 / 1432 (1976). Sea rain at 20-30N falls to 555 against GPCP 714
  (main 757).
- **Regions, main -> branch (GPCC).**
  - Better: Sahara 297 -> 56 (35), Arabia 442 -> 274 (95), C Asia 411 -> 227 (209), US SW 386 -> 272 (279), Sahel
    2427 -> 2151 (593), S Africa 899 -> 775 (391), Australia interior 751 -> 666 (291), NE USA 1627 -> 1392 (1032).
  - Worse: SE USA 1109 -> 482 (1328), Pampas 548 -> 294 (943), Japan 1153 -> 524 (1672), E Australia 1055 -> 488
    (743), Mediterranean 607 -> 383 (551), Mexico N 237 -> 114 (482), India 696 -> 588 (1109), SE Brazil
    1508 -> 1282 (1418).
  - Their rain came from air that had crossed only a strip of sea, so the instant refill hid wind errors (winter
    subtropical highs and cyclones, PW-026). Draft: draft-subtropical-coasts-dry-after-bulk-evap.md.
- **Still too wet:** Sahel, E Africa, NE Brazil and Gobi, as the next section says.
- **Overturning** (`tools/overturning_report.py --earth`): NH 13.65 -> 13.70 Sv, 89 -> 88% in open polar seas, the
  Norwegian coast open in winter. The stage-1 bar holds. (After stage 1, lane A's 0.85 / 1 km form had weakened it to
  7.2 Sv.)
- **Moisture books:** the probe still reproduces the kernel. Atlantic E-P-R +0.07 -> +0.11 Sv.

### Paired judge, main ed7e87ab+diag (A) vs round 1 (B)
L6 1 Gyr, 18 draws x rolls 0.0005 / 0.001, `pjudge.py`. Full output: `judge_r1.txt` / `.json`.

| measure | main | branch | median B-A | 95% CI | B>A / B<A |
|---|---|---|---|---|---|
| arid % of land | 17.5 | 24.5 | **+6.7** | [+5.6, +7.4] | 35 / 1 |
| hot desert % | 5.8 | 11.0 | **+4.6** | [+3.5, +5.9] | 34 / 2 |
| trees % | 38.1 | 33.7 | **-4.2** | [-6.0, -3.1] | 5 / 31 |
| land rain mm | 1166 | 1122 | -46 | [-79, +5] | 13 / 23 |
| land % | 34.9 | 34.6 | -0.3 | [-0.6, -0.1] | 11 / 25 |
| late dT | 1.25 | 0.87 | -0.66 | [-1.26, +0.28] | 14 / 22 |
| late CO2 | 0.71 | 0.61 | -0.08 | [-0.18, +0.01] | 13 / 23 |
| sink ref (ln) | 6.762 | 6.769 | -0.03 | [-0.10, +0.05] | 16 / 20 |
| end T (true - 13.8) | 1.6 | 2.8 | +1.5 | [+0.2, +2.8] | 26 / 10 |

- Passes 29/36 -> 27/36 (r0.0005 16 -> 14, r0.001 13 -> 13). Both 24, main only 5, branch only 3, neither 4;
  McNemar p 0.73. Icebox 13 -> 8, no hellhouse, no SIM SUSPECT.
- The end T move is a finish-window excursion, not a shift in the climate. Paired dT means over 800-900, 900-950,
  950-980 and 980-990 Myr are +0.5, -0.9, -0.5 and -0.5 C, and true T - dT is unchanged (+0.00).
- So the change moves what it targets, the dry land, and nothing in the carbon cycle. The pass count is a check here,
  not the decider, so 2 rolls are enough.

### Tests
- `pytest -m 'not slow'`: 712 passed and 1 failed, with the goldens regenerated (climate_L4, sim_L4_s1_60myr).
- Slow tests: `tests/test_envelopes.py` 11 passed (its dry band is 12-45%), `test_soils` slow passed,
  `test_timezoom_consistency` 3 passed.
- **The failure:** `test_sea_level.py::test_sea_level_starts_at_zero_and_reads_high_in_the_warm_up`. L4 seed 1's
  warm-up basin mean is -55 m against a -50 m bar (main +7). It is systematic over 3 climate_offset re-rolls
  (-52..-58; main +11..+26), so it is a different warm-up path for that seed, not a single flip. Not loosened. Draft:
  draft-sea-level-warmup-seed1-after-bulk-evap.md (needs-decision).

## Round 2 (Earth only, not committed): the vapour's share of the land-sea circulation
- **Mechanism.** The vapour rode `vq = belts + s x (monsoon part)`. A closed thermal cell of depth h, with its return
  flow above, carries a net (1 - e^(-h/H))^2 of the column's vapour (H ~2 km): 0.28 at 1.5 km, 0.60 at 3 km.
- **Uniform s on main** (B / exact / corr / land P / India / SE USA):
  - s 0.5: 27.8 / 38 / 0.621 / 969 / 505 / 570.
  - s 0.3: 31.3 / 39 / 0.579 / 905 / 471 / 308.
- **s 0.3-0.5, deepened to 1 by a first pass's rain** (2000-4000 mm/yr): B 25.7-29.7, corr 0.576-0.614, India
  428-464.
- **Why it failed.** The rain pattern regresses and India dries further. The model rains heavily at every monsoon
  margin, so its own rain can't tell a deep convective monsoon from a shallow heat low. Draft:
  draft-land-sea-circulation-vapour-return-flow.md, with what to try.

## Not done, and suggestions
- A per-world desert quota: none was added, as the owner asked.
- The Sahel, E Africa and NE Brazil are still 3-4x too wet. They need the circulation-depth rule (round 2's draft), not
  a rain-side patch.
- The subtropical coasts: PW-026's winter winds (the coasts draft).

## Example runs (main checkout's store, L6 1 Gyr, default params, `examples.sh`)
- desert-main-s1: e53571 (land 36.2%); desert-new-s1: d1f65c (33.6%)
- desert-main-s2: 1d9507 (35.3%); desert-new-s2: 46730b (34.3%)

## Harness (here)
- `diag_b.py`: the B-deficit attribution on Earth, with optional TUNE overrides.
- `examples.sh`.
- `judge_r1.txt` / `judge_r1.json`: the paired judge's output for round 1.
- The judge itself: `../v1-finish-16/pjudge.py` and `paired.sh`.
