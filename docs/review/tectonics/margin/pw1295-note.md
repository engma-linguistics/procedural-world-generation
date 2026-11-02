# PW-1295: margin cells flicker at the 20 km bound (lane 115)

## In plain words

The flicker was real. With the sea-floor creep on, about 1150 cells per 400 Myr (L6) were turned into ocean floor
within 10 Myr of turning continental, at 19.3 km on average, and about 900 turned continental again within 10 Myr:
the margin's outer cells crossed the one 20 km bound both ways in small steps. Now continental crust is still born at
20 km but is cut off as a shred only below 15 km (`crust.SHRED_KM`). That ends the flicker, and with the creep the
continents' churn falls from about three times main's to main's level. The 36-draw judge (creep off) has no hard
failures, 32/36 passing against 33/36, and no climate change, but 1.3 points less land: the area thermostat now
counts the thin drowned margin cells it keeps, so it holds the same continental area with less thick crust. It's on
by default; the land swing and the creep's cooling (which this doesn't cure) are drafts.

## 1. Confirmation: the flicker is real

tracediag.py now tags every birth, weld and shred on the plate's own grid (slot and cell, so the tag rides with
the crust as the plate moves) and, at each event, bins the Myr since that cell's last event of the other way (a
shred for a birth or weld; a birth or weld for a shred), and its thickness (`flick` in the trace). L6, seeds 1 and
3, 1 Gyr, `--set star_brightening=1.0`, late window 600-1000 Myr, cells / scale^2. Creep = `neck_km=200 rise=1
slope_k=1000`. (Main here is main with PW-1292's A; its land, dT and pCO2 equal pw1292-note.md's A rows.)

| arm, seed | shreds | of them born/welded <= 4 Myr before | <= 10 Myr | <= 50 Myr | > 200 Myr or never | births | of them shredded <= 10 Myr before | <= 50 Myr |
|---|---|---|---|---|---|---|---|---|
| main, 1 | 995 | 75 | 141 | 221 | 747 | 621 | 60 | 168 |
| main, 3 | 1332 | 81 | 159 | 284 | 1020 | 707 | 65 | 181 |
| main + creep, 1 | 3183 | 905 | 1183 | 1454 | 1644 | 2126 | 916 | 1240 |
| main + creep, 3 | 3313 | 872 | 1134 | 1342 | 1899 | 2152 | 884 | 1176 |

Thickness at the event:

| arm, seed | shreds < 15 km | 15-17.5 | 17.5-19 | 19-20 | mean of the quick shreds (<= 10 Myr after birth) | births at 20-21 km |
|---|---|---|---|---|---|---|
| main, 1 | 173 | 274 | 386 | 162 | 18.4 km | 92% |
| main, 3 | 303 | 338 | 462 | 230 | 18.4 km | 93% |
| main + creep, 1 | 965 | 481 | 518 | 1220 | 19.3 km | 97% |
| main + creep, 3 | 1114 | 542 | 515 | 1142 | 19.3 km | 96% |

Reading:
- With the creep, about 1150 cells per 400 Myr are shredded within 10 Myr of being born (900 of them two steps
  later, the next step), against 140-160 on main: eight times as many. About 900 births come within 10 Myr of a
  shred, against 60-65 on main: fourteen times. Those quick shreds are 19.3 km thick on average: they sit on the
  bound. 92-97% of births are at 20-21 km (any thickening crosses the bound in small steps). So the margin's outer cells
  cross the shared 20 km bound back and forth: born at 20.x km, a step's creep or erosion takes them to 19.x km, and
  with at most two continental neighbours they are shredded; sediment brings them back and they are born again.
  That is the flicker, confirmed.
- It is about half of the creep's extra shreds (+2200 / +2000 against main): the quick ones (<= 50 Myr) are +1230 /
  +1060. The other half is long-lived crust (born more than 200 Myr ago, or the start-up continent) thinned below
  20 km and shredded: +900 cells, and 30-34% of all the creep's shreds are already below 15 km. That part is margin
  thinning (necking and the creep stripping the cover), a real loss of continental area, not a flicker.
- Births with the creep: 58% (1240 of 2126) and 55% (1176 of 2152) come within 50 Myr of a shred of the same crust. The doubled
  "arc" births (pw1292-note.md) are mostly these re-births: 466 / 491 of the 918 / 984 arc births come within
  10 Myr of a shred.

## 2. Screens: hysteresis between the bounds

Three variants, each on seeds 1 and 3 with and without the creep (same settings as section 1; tracediag.py with
`HYST_SHRED` / `HYST_REBIRTH`, screen switches of the harness):
- **S15**: coherence shreds only below 15 km (`crust.SHRED_KM`; birth stays at 20). Stateless.
- **R25**: a cell whose last event was a shred is born again only at 25 km (others still at 20). Needs a per-plate
  tag (here the harness's), i.e. new plate state if it went in.
- **both**: S15 + R25.

`shreds`, `quick shreds` (<= 10 Myr after a birth or weld), `births`, `quick births` (<= 10 Myr after a shred):
cells / scale^2, 600-1000 Myr. `born`, `coherence`: sim.budget over 600-1000 Myr, km x L5 cells. Land, cont, dT,
pCO2: late-window means. Seeds 1 / 3.

| arm | land % | cont % | late dT (C) | pCO2 (ppm) | shreds | quick shreds | births | quick births | born | coherence |
|---|---|---|---|---|---|---|---|---|---|---|
| main | 34.6 / 33.3 | 40.4 / 40.9 | -0.0 / -0.9 | 1012 / 961 | 995 / 1332 | 141 / 159 | 621 / 707 | 60 / 65 | 12 700 / 14 400 | -4 000 / -6 600 |
| S15 | 34.0 / 33.1 | 42.8 / 42.5 | -0.3 / -1.7 | 933 / 763 | 258 / 224 | 0 / 1 | 278 / 367 | 0 / 0 | 5 800 / 7 700 | +11 100 / +12 500 |
| R25 | 34.8 / 35.1 | 41.0 / 42.0 | -3.2 / -1.7 | 480 / 793 | 1000 / 1178 | 119 / 136 | 598 / 420 | 1 / 2 | 12 500 / 8 800 | -3 500 / -5 100 |
| both | 33.6 / 33.3 | 42.4 / 42.3 | +0.6 / -0.1 | 1046 / 1006 | 228 / 231 | 2 / 1 | 268 / 182 | 0 / 0 | 5 600 / 3 700 | +11 500 / +9 800 |
| creep | 33.1 / 31.9 | 42.0 / 42.1 | +0.8 / -2.7 | 1146 / 581 | 3183 / 3313 | 1183 / 1134 | 2126 / 2152 | 916 / 884 | 43 000 / 43 500 | -40 700 / -39 900 |
| S15 + creep | 32.4 / 31.2 | 42.4 / 42.5 | -3.3 / -4.4 | 616 / 471 | 1032 / 1322 | 9 / 11 | 937 / 827 | 0 / 0 | 19 000 / 16 800 | -5 500 / -7 100 |
| R25 + creep | 31.6 / 31.2 | 41.1 / 41.5 | +2.3 / -0.5 | 1339 / 873 | 2657 / 3066 | 497 / 563 | 1192 / 1570 | 5 / 6 | 25 100 / 32 900 | -28 300 / -31 000 |
| both + creep | 30.6 / 31.3 | 42.0 / 42.0 | -3.1 / +3.4 | 550 / 1781 | 1182 / 1012 | 4 / 7 | 892 / 744 | 0 / 0 | 18 300 / 15 200 | -5 400 / -4 000 |

Late-window continental crust (seeds 1 / 3): mean thickness 34.5 / 34.0 km on main, 33.1 / 33.3 with S15; the share of
the continental crust deeper than 1000 m below sea level 5.6 / 7.4% on main, 11.0 / 11.8% with S15.

Reading:
- **S15 removes the flicker outright** (quick shreds and quick births 0-11, from ~1150 and ~900 with the creep, and
  from 140-160 and 60-65 on main). With the creep, the churn falls to main's level: born 19 000 / 16 800 against
  43 000, coherence -5 500 / -7 100 against -40 000. It needs no new state.
- **R25 only blocks the second half** of the loop: a fresh birth at 20.x km is still shredded at 19.x km the next step
  (quick shreds 500-560 with the creep), it just isn't born again. The churn falls by a third, not to main's level,
  and it would need a per-plate tag. **both** behaves like S15 (the rebirth bound has almost nothing left to hold)
  and adds R25's state for nothing.
- Picked **S15** by mechanism: the flicker is a cell crossing one bound in both directions in small steps, and a gap
  between the two bounds that a step can't cross is the direct cure. A margin cell thinned to 15-20 km is thinned
  continental crust (rifted margins thin continental crust well below 15 km before it breaks), so keeping it
  continental is the better reading than turning it into ocean floor of continental thickness.
- What S15 changes on main (no creep): main's shreds were mostly 15-20 km margin cells (82% of them), so the shred
  sink of continental area falls by three quarters and coherence turns from a net sink (-4 000 / -6 600) into a net
  source (+11 100 / +12 500): the welds are no longer balanced by shreds. Continental crust rises ~2 points (40.4 ->
  42.8, 40.9 -> 42.5), all of it submerged thin margin (land is unchanged, 34.0 / 33.1, the >1 km-deep share of the
  continental crust doubles), and the area thermostat answers by halving births (12 700 -> 5 800, 14 400 -> 7 700).
  Half of main's births were themselves re-births of shreds (190 of 380 arc births on seed 1 came within 200 Myr of a
  shred). dT and pCO2 within the two-seed noise (-0.3 / -0.8 C).
- S15 + creep runs 3.0 / 2.7 C colder than S15 alone on these two seeds (late dT -3.3 / -4.4, pCO2 616 / 471): the cure of the churn
  doesn't cure the creep's cooling (deep-dive.md judge 2: -2.6 C, 2 frozen over).

## 3. Judge: S15 against main, creep off (L6, v1-finish-16's 18 draws x rolls 0.0005, 0.001)

paired_margin.sh from two frozen copies (`git archive`): `base` = main 02517a9c, `on` = 1e4679d3 (main + `SHRED_KM =
15`). pjudge.py over both (36 paired draws), tools/hard_bar.py per arm. No threshold or search window changed.

| measure | main | S15 | median S15 - main | 95% CI | moved |
|---|---|---|---|---|---|
| end T | 0.50 | 0.77 | -1.18 | [-3.62, +2.17] | |
| late dT | 0.62 | 0.50 | -0.27 | [-1.48, +1.76] | |
| late CO2 index | 0.56 | 0.50 | -0.02 | [-0.30, +0.21] | |
| land % | 34.54 | 33.37 | -1.25 | [-1.66, -0.95] | * (33 of 36 draws lower) |
| sink ref / src ref | 6.58 / 7.99 | 6.55 / 8.00 | -0.06 / +0.01 | [-0.11, +0.02] / [-0.07, +0.05] | |
| arid % / hot desert % | 22.4 / 8.8 | 22.7 / 9.2 | -0.1 / -0.4 | [-1.5, +2.0] / [-1.1, +1.4] | |
| land rain (mm/yr) / trees % | 1136 / 34.3 | 1153 / 35.7 | +15 / +0.7 | [-34, +70] / [-1.9, +1.7] | |

Pass: main 16/18 + 17/18 = 33/36, S15 16/18 + 16/18 = 32/36 (both 29, main only 4, S15 only 3; McNemar p 1.0).
Hard bars: frozen over 0/0, boiled 0/0, ocean loss 0/0, CO2 crash 0/0. Secondary: pCO2 < 100 ppm 1 against 2; end
pCO2 outside 180-600 14 against 13; an 8-fold CO2 fall within 50 Myr (end at most 1/4 of before) 25 against 26.

**The land swing, diagnosed** (margindiag's `margin` numbers, late-window means, paired medians over the 36 draws):

| | main | S15 | median S15 - main | S15 > main |
|---|---|---|---|---|
| land % | 34.49 | 33.27 | -1.29 | 2 / 36 |
| continental crust % | 41.16 | 41.28 | +0.02 | 18 / 36 |
| mean continental thickness (km) | 34.50 | 33.59 | -0.83 | 3 / 36 |
| median of the submerged continental crust (m) | -815 | -1089 | -264 | 4 / 36 |
| 200-3000 m, % of the ocean | 11.9 | 13.1 | +1.4 | 28 / 36 |
| shelf (0-200 m), % of the ocean | 2.5 | 2.4 | -0.3 | 14 / 36 |

The continental area doesn't change: the area thermostat holds it (`crust.thermostats`: subduction erosion follows
the area). What changes is what fills it. The 15-20 km margin cells that main shredded now stay continental and
count in the area; on main their shredding balanced the welds, and now coherence is a net source of area (screens:
+11 000 / +12 500 km x cells per 400 Myr against -4 000 / -6 600). The thermostat answers the extra area with
fewer births and more subduction erosion, so the same 41% holds more drowned thin margin and less thick crust: the
crust is 0.8 km thinner on average, the drowned part 260 m deeper, and land 1.3 points less. The margin band
200-3000 m grows by 1.4 points (towards Earth's 19.6%, deep-dive.md), the shelf stays put. No climate measure moved.

**Verdict**: no hard failure, soft pass level with main (32 against 33), climate unmoved; land -1.3 points moved,
explained by the area thermostat counting the kept thin margin. The mechanism is the sound one (a gap between the
bounds; it cures the flicker it was made for, and the creep's churn with it), so it is on by default (`crust.SHRED_KM
= 15`, no switch). The land swing is a draft (draft-area-thermostat-counts-drowned-thin-margin), not fixed here.

**Judge 2 (creep + S15 against S15) not run**: the screens show S15 cures the creep's churn but not its cooling
(-3.0 / -2.7 C against S15 alone on seeds 1 and 3), so the brief's condition ("if creep-on-hysteresis screens look
promising") isn't met. Draft: draft-sea-creep-still-cools-with-the-flicker-cured.

Goldens updated (the shred bound changes every output of the 60 Myr golden run). Scratch runs are deleted. To redo:
tracediag.py with `HYST_SHRED=20` (main's bound) or unset, seeds 1 and 3, `--myr 1000 --level 6 --set
star_brightening=1.0 [neck_km=200 rise=1 slope_k=1000]`; the judge with `paired_margin.sh CODE OUT m 0.0005 0.001`,
one OUT per arm (hard_bar.py reads arm `m`), linked into one root as base_/on_ for pjudge.py.

Scorecard (tools/scorecard.py, d143c2bc, L6 seeds 1 / 2, 1 Gyr, no Earth data in the worktree): land 32.3 / 30.9%,
crust 40.9 / 39.8%, shelf 1.6 / 2.7% of the ocean, submerged continent median -1263 / -968 m, volume x0.974 / 0.978.
The line before it (7c9409e2, an older main): land 33.5 / 32.9, shelf 3.4 / 1.9, -757 / -995 m, volume x1.005 / 1.004.
Same direction as the judge: land a point or two lower, continental volume ~2.5% under its target (thinner crust).

## 4. Round 2: test_envelopes seed 2 goes to a hothouse with the 15 km bound (diagnosis only, no fix)

The coordinator reverted the bound on main (4e3185dc): `tests/test_envelopes.py::test_climate[2]` (L5, seed 2, 400 Myr)
ends at 28.8 C, pCO2 3547 ppm with `SHRED_KM = 15`, against 15.8 C, 327 ppm at 20. Harness:
[envdraw.py](envdraw.py) runs the fixture's own world (L5, `Params(run_end=400)`, dt 2, 0-100 Myr in one call then
4 Myr chunks) for a seed and a bound, with a trace every 4 Myr. It reproduces both numbers exactly.

### Re-rolled draws: 20 seeds, both bounds, end at 400 Myr

| seed | T 15 / 20 (C) | pCO2 15 / 20 | land % 15 / 20 | cont % 15 / 20 | thick (km) 15 / 20 |
|---|---|---|---|---|---|
| 1 | 19.6 / 16.6 | 427 / 425 | 29.2 / 30.7 | 44.5 / 41.4 | 30.4 / 32.0 |
| 2 | **28.8** / 15.8 | 3547 / 327 | 30.9 / 32.1 | 43.5 / 40.3 | 30.8 / 33.0 |
| 3 | 13.1 / 14.3 | 176 / 273 | 29.5 / 30.1 | 42.9 / 40.3 | 31.4 / 33.0 |
| 4 | 17.5 / 14.8 | 494 / 362 | 31.1 / 31.0 | 42.6 / 40.8 | 31.8 / 32.7 |
| 5 | 17.5 / 14.3 | 419 / 222 | 29.5 / 30.7 | 42.9 / 42.1 | 30.8 / 31.7 |
| 6 | 13.1 / 16.5 | 222 / 317 | 29.9 / 30.1 | 41.5 / 42.4 | 31.4 / 31.2 |
| 7 | 21.4 / 9.5 | 1169 / 103 | 28.3 / 31.4 | 43.6 / 40.6 | 30.2 / 33.1 |
| 8 | 16.6 / 15.0 | 412 / 339 | 29.9 / 30.7 | 43.1 / 40.7 | 30.7 / 32.2 |
| 9 | 15.5 / 16.2 | 413 / 304 | 30.4 / 31.2 | 41.4 / 41.5 | 31.6 / 32.0 |
| 10 | 12.8 / 15.9 | 184 / 346 | 30.1 / 31.6 | 43.4 / 39.9 | 31.6 / 32.8 |
| 11 | 16.7 / 16.3 | 509 / 408 | 27.7 / 31.1 | 44.9 / 41.2 | 30.0 / 32.3 |
| 12 | 13.4 / 21.6 | 210 / 1171 | 29.9 / 32.1 | 43.4 / 40.8 | 31.3 / 32.9 |
| 13 | 13.9 / 16.5 | 157 / 340 | 29.6 / 30.5 | 43.1 / 40.4 | 31.1 / 32.7 |
| 14 | 11.2 / 11.3 | 176 / 149 | 28.7 / 30.3 | 43.4 / 40.7 | 31.3 / 32.4 |
| 15 | 17.5 / 13.6 | 435 / 144 | 29.8 / 30.3 | 41.2 / 43.3 | 32.2 / 31.1 |
| 16 | 19.3 / 17.9 | 664 / 611 | 29.4 / 31.4 | 43.9 / 40.4 | 30.3 / 32.5 |
| 17 | 10.5 / 18.0 | 125 / 404 | 31.5 / 30.4 | 42.4 / 41.3 | 31.8 / 32.4 |
| 18 | 11.6 / 12.0 | 224 / 158 | 27.3 / 31.2 | 42.5 / 41.0 | 30.5 / 32.6 |
| 19 | 18.1 / 21.5 | 666 / 813 | 32.3 / 29.3 | 42.1 / 40.7 | 31.8 / 32.2 |
| 20 | 15.6 / 21.9 | 278 / 1096 | 30.2 / 30.4 | 42.2 / 42.4 | 31.8 / 31.6 |

- **Out of the envelope band (|T - 14.5| > 10): 1 of 20 with 15 km (seed 2), 0 of 20 with 20 km.** The 20 km arm's
  warmest ends are 21.9, 21.6 and 21.5 C (seeds 20, 12, 19), within 3 C of the edge; the 15 km arm's next warmest is
  21.4 (seed 7).
- End T: median 16.1 against 16.05 C, paired median difference -0.25 C, the 15 km arm warmer on 9 of 20. Spread
  sd 4.1 against 3.2 C (seed 2 alone makes the difference).
- So **on the band count it looks like chaos**: 1/20 against 0/20 can't be told apart (Fisher p = 1). Seed 2 is
  the most extreme run of the 40 (peak pCO2 6955 ppm; the next highest is 4354, a 20 km run), but other draws go
  further out in the other arm (seeds 12, 20: +8, +6 C with 20 km).
- **But the bound does shift things systematically at L5 / 400 Myr**: continental crust 43.0 against 40.8% (median;
  higher on 17 of 20), thinner by ~1.5 km, land ~1 point lower. Unlike the L6 1 Gyr judge, the area thermostat hasn't
  pulled the area back by 400 Myr.

### Where seed 2's CO2 runs away

Trace (envdraw.py; source = ridge + 20 x the arcs' nominal growth + plume, `earth.global_temperature`; refs learnt
until `earth.REF_FREEZE` = 300 Myr, then kept):

| t (Myr) | dT 15 / 20 | pCO2 15 / 20 | source 15 / 20 | sink 15 / 20 | src ref 15 / 20 | sink ref 15 / 20 | land supply 15 / 20 | cont % 15 / 20 |
|---|---|---|---|---|---|---|---|---|
| 100 | 6.3 / 4.8 | 3168 / 1813 | 2656 / 2816 | 357 / 486 | 2281 / 2338 | 475 / 463 | 94 / 99 | 44.5 / 42.2 |
| 160 | -5.6 / -2.6 | 232 / 379 | 1160 / 1927 | 359 / 465 | 1987 / 2273 | 497 / 522 | 160 / 168 | 39.9 / 39.2 |
| 200 | -4.8 / 3.7 | 494 / 1365 | 1369 / 2816 | 455 / 560 | 1675 / 2296 | 566 / 543 | 178 / 136 | 39.6 / 39.3 |
| 240 | 1.3 / 5.7 | 1158 / 1668 | 2407 / 3446 | 823 / 560 | 1627 / 2332 | 691 / 522 | 223 / 133 | 39.8 / 39.8 |
| 300 | 10.3 / 3.3 | 3905 / 767 | 3671 / 2517 | 924 / 505 | 1973 / 2384 | 745 / 523 | 154 / 129 | 42.4 / 39.2 |
| 340 | 12.2 / 4.4 | 4195 / 835 | 2609 / 2775 | 665 / 543 | (kept) | (kept) | 117 / 138 | 43.2 / 40.1 |
| 380 | 15.5 / 0.8 | 6368 / 281 | 2236 / 1735 | 587 / 436 | 1973 / 2384 | 745 / 523 | 108 / 133 | 43.3 / 40.7 |

The source's parts over the spin-up 100-300 Myr: ridge 158 against 208, the arcs' nominal 1530 against 2120 (from
120 to 260 Myr the 15 km arm's arcs and ridges both sit 25-60% lower: 830-1760 against 1730-2700, 73-177 against
160-252).

Reading: after 300 Myr the two arms' **absolute** source and sink are about the same (2240-2610 against
1735-2775; 400-770 against 420-545). What differs is what they're measured against. In the 15 km arm the source's
reference was learnt during a 140 Myr spell of weak arcs and ridges (1973 against 2384, -17%), and the sink's during
the high weathering supply of 220-300 Myr (745 against 523, +42%). Kept from 300 Myr on, they put the source at
1.13-1.32 of its reference and the sink at 0.54-1.03 of its own, so CO2 piles up for 100 Myr: the frozen-reference
mechanism (PW-558/559 B) locking a spin-up transient in. Over all 40 runs, the end T follows that late imbalance
(correlation 0.80 with ln(source index) - ln(sink index), 300-400 Myr) and hardly the continental area (0.15).

### Is the spin-up dip chance or the bound?

Over the 20 seeds, the 15 km arm's spin-up source (100-300 Myr mean) is lower on 17 of 20 (median -161, ~-7%), and so
its kept source reference (17 of 20). Its late source is higher on 14 of 20, and the late imbalance larger on 12 of 20
(median +0.05 e-folds). On 7 seeds with the parts traced (1-6, 8):

| seed | ridge 15 / 20 | arcs' nominal 15 / 20 | plate speed (cm/yr) 15 / 20 | area gain (`shrink`) 15 / 20 | arc gain 15 / 20 | cont % at 100 Myr 15 / 20 | end T 15 / 20 |
|---|---|---|---|---|---|---|---|
| 1 | 160 / 187 | 1840 / 1990 | 4.13 / 4.47 | 1.23 / 0.93 | 1.21 / 1.38 | 44.1 / 42.2 | 19.6 / 16.6 |
| 2 | 158 / 208 | 1530 / 2120 | - | 1.47 / 1.12 | 1.23 / 1.47 | 44.5 / 42.2 | 28.8 / 15.8 |
| 3 | 159 / 178 | 1680 / 1820 | 4.49 / 4.33 | 1.06 / 0.74 | 1.35 / 1.53 | 42.8 / 42.2 | 13.1 / 14.3 |
| 4 | 181 / 179 | 1860 / 1920 | 4.93 / 4.50 | 1.23 / 1.01 | 1.26 / 1.58 | 43.3 / 41.6 | 17.5 / 14.8 |
| 5 | 160 / 172 | 1690 / 1890 | 4.14 / 4.16 | 1.27 / 1.07 | 1.45 / 1.82 | 42.3 / 42.1 | 17.5 / 14.3 |
| 6 | 165 / 180 | 1950 / 1930 | 4.16 / 4.51 | 1.46 / 0.96 | 1.37 / 1.49 | 44.8 / 42.1 | 13.1 / 16.5 |
| 8 | 167 / 185 | 1810 / 2020 | 3.99 / 4.16 | 1.38 / 1.07 | 1.32 / 1.42 | 42.5 / 40.8 | 16.6 / 15.0 |

(spin-up means; plate speed every 20 Myr, missing for seed 2's first trace)

So it isn't only chance: with the 15 km bound the start-up continents keep more thin margin (more continental area
at 100 Myr on 7 of 7), the area thermostat runs subduction erosion harder (7 of 7), and the ridges and arcs, the
spin-up CO2 source, are weaker (6 of 7 each; plates slower on 4 of 6). The reference learns that weaker source as
the planet's balance. When the source recovers after the freeze the world warms. Mostly this stays in the band (median
end T unchanged). On seed 2 the dip was deepest (-28% arcs) and the freeze caught a weathering-supply peak.

Why weaker arcs and ridges is not shown yet. The likeliest reading: thin margin cells kept as continental crust on a
plate's leading edge count as continent at its trenches, so they meet a trench as continental crust (buoyant,
collision rather than subduction), which shortens the subducting trench and slows the plates. Unverified: the trace
doesn't count trench edges by crust type.

### Candidate fixes (none made)

1. **Thin continental crust subducts.** Below BECOMES_CONT_KM, a continental cell on the sinking side of a trench is
   taken down like ocean floor, not jammed like a continent (Earth's thinned margins are partly subducted before a
   collision locks). Check first: count trench edges whose sinking cell is 15-20 km continental, per arm (cheap,
   envdraw.py plus `bd.at_trenches`). If they're the difference, this is the mechanism-level fix and keeps the
   flicker cure.
2. **Thin margin outside the area thermostat** (PW-1314): count only crust at least BECOMES_CONT_KM thick as the
   continents' area, so the kept margins don't drive subduction erosion. That treats the extra erosion, not the weak
   source.
3. **The frozen reference's fragility** is not this lane's: any change in the spin-up's plate history can lock a
   transient in at 300 Myr (seeds 12 and 20 do it with the 20 km bound). Learning the source's reference as a
   longer mean, or not before the spin-up's start-up continents have dispersed, would make all arms sturdier. That
   is a reference-scheme decision (PW-558/559's owner ruling), not a fix for PW-1295.
4. Not proposed: a different shred bound (17.5 km) to "split the difference". It would trade the flicker cure for a
   smaller version of the same shift, with nothing to justify the number.

Verdict for the coordinator: the band failure on seed 2 is mostly chaos in which run trips the frozen references
(1/20 against 0/20). But the bound does move the spin-up source down systematically (17/20), which makes such trips a
little likelier, and at L5 / 400 Myr it raises continental area by ~2 points. Candidate 1's check is the cheap next
step. The bound stays off on main until then.

## 5. Round 3 (lane 119, PW-1317): do the kept thin margins jam trenches? No

**In plain words:** the guess was that the 15-20 km margin cells the 15 km bound keeps as continent reach trenches
and jam them, which would shorten the subducting trenches and slow the plates. They don't, measurably: such jams add
about 1 collision edge in 900 trench edges. What does differ is that the young planet has **fewer plates**, about
2.5 fewer (-17%) over 100-300 Myr on 8 of 8 seeds, so all its plate boundaries are ~9% shorter: ridges and trenches
alike, hence the weaker ridge and arc outgassing. The plates aren't slower (mean speed unchanged). The fewer plates
come from the kept margins counting as continent in the plates' **dynamics** (the continental keel's drag in the
force balance and the continents' insulation of the mantle): a screen where those two see only crust of 20 km and
up, everything else as the 15 km bound, removes most of the difference. Step 2 (let thin continental crust subduct)
was not made: it would fix a jam that isn't there.

Harness: [jamdiag.py](jamdiag.py), envdraw.py's world (the test_envelopes fixture: L5, `Params(run_end=400)`, dt 2,
its chunks), every step to 300 Myr, counting at `motion.boundaries`: subducting edges (`sub_n`) and their summed
convergence (`sub_conv`, the slab flux), collision edges (`col_n`) and those with a thin (< 20 km) continental side
(`col_thin`), all boundary edges, live plates, the source's parts; events from `sim.events`. Counts are edges /
scale^2. Seeds 1-8 (envelope seed 2 among them), 15 km (the cherry-picked d143c2bc) against 20 km (main's bound).
Means over 100-300 Myr, 15 / 20:

| seed | thin cont % | col_thin | sub_n | sub_conv | all edges | plates | ridge | arcs' nominal | speed (cm/yr) |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 2.95 / 1.59 | 7 / 6 | 806 / 901 | 3963 / 4508 | 1818 / 2020 | 12.5 / 15.2 | 162 / 185 | 1837 / 1983 | 3.80 / 4.17 |
| 2 | 3.63 / 1.84 | 10 / 5 | 709 / 948 | 3539 / 4756 | 1704 / 2014 | 10.8 / 15.7 | 156 / 206 | 1528 / 2101 | 4.13 / 4.84 |
| 3 | 2.94 / 1.76 | 8 / 8 | 760 / 817 | 3694 / 4164 | 1734 / 1889 | 11.8 / 14.5 | 156 / 178 | 1667 / 1803 | 4.20 / 4.05 |
| 4 | 3.37 / 2.24 | 9 / 6 | 789 / 831 | 4127 / 4162 | 1827 / 1909 | 13.9 / 14.0 | 180 / 177 | 1843 / 1912 | 4.74 / 4.26 |
| 5 | 3.51 / 2.48 | 6 / 9 | 761 / 880 | 3686 / 4098 | 1705 / 2003 | 11.0 / 12.8 | 157 / 171 | 1683 / 1891 | 4.01 / 3.95 |
| 6 | 3.54 / 1.74 | 7 / 5 | 863 / 862 | 4212 / 4258 | 1909 / 1887 | 12.2 / 12.8 | 166 / 179 | 1940 / 1915 | 3.97 / 4.29 |
| 7 | 2.97 / 1.36 | 7 / 5 | 841 / 894 | 4280 / 4674 | 1890 / 1986 | 13.1 / 15.5 | 179 / 192 | 1881 / 2043 | 4.47 / 4.29 |
| 8 | 3.22 / 2.27 | 4 / 4 | 821 / 919 | 3994 / 4521 | 1776 / 2079 | 12.3 / 15.1 | 165 / 186 | 1811 / 2030 | 3.85 / 4.01 |

(ridge and arcs' nominal as in section 4, here averaged over every step; they agree with its table within ~2%)

- **The jam is too small to matter.** Collision edges with a thin side: +1.0 per step (median; higher on 6 of 8),
  against 40-240 fewer subducting edges (median -75, fewer on 7 of 8). Subducting edges whose overriding cell is
  thin continent (a kept margin taking the other plate's ocean floor under it) differ by nothing (median -0.0, 4 of 8).
  The thin margin cells themselves double (3.3 against 1.8% of the surface), but nearly all of them sit inside plates,
  not on converging edges. (A sinking cell is always oceanic by `motion.boundaries`' rule, so a kept margin can only
  "jam" as a continent-continent collision edge; those are the `col_thin` counts.)
- **The plates aren't slower.** Mean speed differs by -0.05 cm/yr (median; lower on 4 of 8). Section 4's "slower on
  4 of 6" was the same coin toss.
- **There are fewer plates, so less boundary of every kind.** Plates -2.5 (median; fewer on 8 of 8, -17%), all
  boundary edges -178 (7 of 8, -9%), spreading edges -90 (7 of 8), subducting edges -75 (7 of 8), slab flux -441
  (8 of 8, -10%), ridge -17 (7 of 8), arcs' nominal -154 (7 of 8, -8%). The ridge and arc deficits are the boundary
  deficit: per edge they're about equal in both arms.
- **When:** over 0-100 Myr the arms barely differ (plates within 1, mean over the span), though the 15 km arm logs
  more continental collisions (42 against 30, summed over the 8 seeds) and sutures (4 against 0). Over 100-300 Myr it
  makes fewer plates (rifts plus new subductions, 147 against 160) and loses more (absorbed slivers, sutures,
  consumed: 165 against 157). The plate counts part from ~80-120 Myr on (seed 2: 6-8 plates over 180-240 Myr
  against 12-16).

### What the fewer plates come from: screens (15 km bound, one model term reading only crust >= 20 km as continent)

| arm (each against 20 km, 8 seeds, 100-300 Myr medians) | plates | all edges | sub_n | slab flux | ridge | arcs' nominal |
|---|---|---|---|---|---|---|
| 15 km | -2.5 (8/8 fewer) | -178 (7/8) | -75 (7/8) | -441 (8/8) | -17 (7/8) | -154 (7/8) |
| 15 km, rift cuts' sliver test and strength see >= 20 km (`JAM_THICK_PIECE`, seeds 1-2 only) | 12.3 / 9.6 against 15.2 / 15.7 | | | | | |
| 15 km, force balance (keel drag, traction coupling) sees >= 20 km (`JAM_THICK_DYN=keel`) | -1.9 (6/8) | -209 (7/8) | -96 (6/8) | -412 (7/8) | -22 (5/8) | -181 (6/8) |
| 15 km, mantle insulation sees >= 20 km (`JAM_THICK_DYN=mantle`) | -0.3 (5/8) | -132 (5/8) | -75 (5/8) | -399 (5/8) | -13 (5/8) | -60 (5/8) |
| 15 km, both (`JAM_THICK_DYN=1`) | -0.8 (5/8) | -38 (5/8) | -12 (4/8) | -216 (6/8) | -7 (5/8) | -81 (5/8) |

(n/8: seeds where the arm is lower than 20 km; 5/8 or 4/8 is no sign)

Reading: the rifts' sliver test (`events.piece_ok`, a kept speck making a cut leave a "continental sliver") isn't it:
it vetoes a few more trial cuts with 15 km (50 and 59% against 46 and 36% on seeds 1-2), but the screen that
takes the thin margin out of it leaves the plates as few. The keel
alone isn't it either (the deficit stays systematic, 6-7 of 8). The mantle's insulation alone takes the systematic
sign away (5 of 8 on every measure) but leaves large median deficits in boundary and slab flux; with both terms
reading only thick crust the deficit mostly goes (medians a sixth to a half of the 15 km arm's: plate count and
boundary at a third and a fifth, arcs and slab flux at half; and 4-6 of 8, inside the seed-to-seed scatter). Eight seeds tell a systematic 8/8 or 7/8 from chance
(sign test p 0.01-0.07), not 6/8 from 5/8, so which of the two terms carries more is not settled. So the kept
margins weaken the spin-up's source not at the trenches but by counting, in the mantle and force model, as a wider
continent: `mantle.update` warms the mantle under every continental cell (`insulation x w_cont x lid`) and
`motion.forces` / `mantle.traction` give each continental cell 2.5x the drag and coupling. A 15-20 km rifted margin
has neither a thick lithospheric keel nor a continent's insulating lid; a continental fraction of those weights
(e.g. by thickness, from the 20 km bound up) is the mechanism-level change. Not made here (draft): it touches the
plate dynamics of every run, needs its own screen on the 20 envelope seeds and a judge, and is only needed if the
15 km bound comes back.

Not shown: why a warmer, wider insulated patch gives fewer plates (fewer rifts, more sutures and absorbed slivers
over 100-300 Myr, in about equal parts). The screens settle which model terms carry the effect, not the path.

Verdict: PW-1317's hypothesis is not confirmed; step 2 (thin continental crust subducts) is not proposed. The
envelope seed 2 failure stays what section 4 said: chaos in which run trips the frozen references (PW-1316), made a
little likelier by a ~8% weaker spin-up source, which comes from fewer plates, which comes from the kept margins'
weight in the mantle and force model.
