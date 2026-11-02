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
