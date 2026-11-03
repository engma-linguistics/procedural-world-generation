# Lane 150: the Nordic seas get too little of the inflow's heat (PW-1411, PW-1413), 2026-11-03

Status: **diagnosis done; three candidates screened, all three failed (three strikes). No candidate for the judge.
`planet/` is unchanged.**

Main = 65e13f48 (moc_lambda 60, PW-1381). Everything here is Earth L6 unless it says otherwise. The comparison in
every table is the same Earth L6 world on main's code, against the observations named. Scripts in this directory:
- `nordmap.py`: the overturning on its own grid (L5), cell by cell, 55-82 N, 45 W-25 E, plus the sinking by basin and
  the inflow across the Greenland-Scotland ridge;
- `screen.py` (run through `sc.sh` / `batch.sh`): one L6 climate read three ways: lane 142's `heatcross`, the ridge
  numbers, and lane 142's `seabox` against OISST;
- `screen_switches.patch`: the temporary TUNE switches the screens used (removed from `planet/` again).

OISST v2 1991-2020 long-term monthly means (NOAA PSL `downloads.psl.noaa.gov/Datasets/noaa.oisst.v2/sst.ltm.1991-2020.nc`,
fetched to scratch only, as lane 142 did). The Earth data cache is a private copy in this worktree's `data/earth`.

## 1. Where it is set in the code

- **The inflow's heat release.** `ocean.overturning`, the block after `_route`:
  - `mix = moc_lambda x hw / RHO_C_SEA` per coarse cell (hw = cell width x `moc_width` 250 km);
  - `_along(order, par, Q, t_eq, sst, mix, 0)` relaxes the inflow's temperature toward `t_eq` by exp(-mix / Q) per
    cell.
  - `t_eq` is `climate.compute`'s `t_sea = max(sea_temperature(...), FREEZE)`: the latitude's profile, passed through
    `ocean.solve` as `teq_c`. **North of ~66 N it is the freezing point, -1.8 C** (nordmap: every cell 66-80 N).
- **The sinking site.** `ocean.overturning`'s loop over each sea and hemisphere: the `gate` on the winter density at
  `moc_z` against the deep water's (`ref`), times Stommel's `dr`, capped per cell by `moc_k`. A "site" in
  `moc_sites` is one *connected* sinking area, and its lat/lon is the sinking-weighted centroid.
- **The winter swing.** `climate._sea_half` makes the sea's own half-swing (`brine_m` 50 m of heat capacity);
  `ocean.winter_half` cuts its winter half by `1 - share x (1 - brine_m / moc_layer_m)` (0.1 under a full inflow),
  called in `climate.compute` after `ocean.solve`. In `ocean.solve`'s `state()` the same cut sets the winter density.
- **The sea surface.** `ocean.solve.sst_c` and `climate.sea_surface`: sst = sst0 + carried(share x (t_in - t_eq)),
  less its latitude's mean (`moc_zonal` 1). So the Nordic seas' SST is the inflow's own temperature, through share.

## 2. Observed targets (read in this lane unless it says so)

- **Lozier et al. 2019, Science 363, 516** (full text, WHOI copy, read):
  - p. 519: "An estimate of MHT across the entire OSNAP section yields a mean and uncertainty of 0.45 ± 0.02 PW";
    "the heat transport across OSNAP East (0.38 ± 0.02 PW) greatly exceeds that of OSNAP West (0.080 ± 0.004 PW)".
    OSNAP East runs Greenland to Scotland at ~58-60 N, so its 0.38 PW is not all heat into the Nordic seas: part of
    it is lost over the Irminger and Iceland basins.
  - p. 518: overturning across OSNAP East "(15.6 ± 0.8 Sv) dominates that across OSNAP West (2.1 ± 0.3 Sv)"; the
    whole section 14.9 ± 0.9 Sv.
- **Tsubouchi et al. 2021, Nature Climate Change 11, 21** (abstract, read at pure.uhi.ac.uk): "the mean ocean heat
  transport was 305 ± 26 TW for 1993–2016" into the Nordic seas and Arctic Ocean. **This is the number PW-1411's
  "the Nordic seas get too little" should be judged on.**
- **Østerhus et al. 2019, Ocean Science 15, 379** (full text, read; Table 1 is an image I couldn't read):
  sect. 4.6, the overflows have "a total volume transport close to 6 Sv"; sect. 4.5 uses "5.8 Sv of overflow water".
  Sect. 1: no heat transport ("our focus is only on the transport of water (volume)").
- **OISST v2 1991-2020** (read as data, sampled per cell as lane 142's `seabox`): Nordic seas box 60-72 N, 20 W-15 E
  annual 7.2 C, coldest month 5.2, winter half-swing (annual minus coldest month) 2.07; NE 50-60 N 2.01; NW 50-60 N
  2.60; the 60-70 N sea band 4.30.
- **Holte et al. 2017, GRL 44, 5618:** winter mixed layers beyond 1500 m in the Labrador and Nordic seas.
  **Not re-read here** (Wiley returned 403, the eScholarship copy came back empty). I only have lane 142's quote.

## 3. What the model does (main, `nordmap.py`, `screen.py`)

| | main | observed |
|---|---|---|
| N Atlantic sinking, total | 12.55 Sv | OSNAP 14.9 Sv (overturning across the section) |
| ... west of 45 W (Labrador) | 3.84 Sv | OSNAP West 2.1 Sv |
| ... Irminger / Iceland basin | 2.92 Sv | (in OSNAP East's 15.6) |
| ... north of the Greenland-Scotland ridge | 5.80 Sv | overflows ~6 Sv (Østerhus) |
| inflow across the ridge | 5.80 Sv at **3.76 C** | |
| its heat above the water sinking north of it (-1.21 C) | **118 TW** | **305 ± 26 TW** (Tsubouchi) |
| heat above all the N Atlantic's sinking water at 60 / 65 N | 0.40 / 0.02 PW | |
| Nordic seas box SST, annual | 4.5 C | 7.2 C (OISST) |

**Correction to the ticket: the overturning does not sink off East Greenland.** The site "67.3 N, 32.1 W, 12.55 Sv"
is the centroid of **one connected sinking area of 5.1 million km2**, from the Labrador Sea to the Barents. Every
Nordic-seas cell sinks 0.1-0.25 Sv. 5.8 Sv sink north of the ridge, which is about the observed overflow.

**The route east of Iceland is open.** On L5 the main branch goes 58.6 N 18.5 W -> 59.8 N 9.8 W -> 62.0 N 8.2 W
(Faroe-Shetland side, 4.7 Sv) -> 64.2 N 6.4 W -> 64.5 N 1.2 W -> 66.6 N 1.4 E -> 68.6 N 4.5 E -> 70.6 N 8.2 E. No
strait lid falls on it. 0.75 Sv go west of Iceland.

**So the volumes are about right, and the shortfall is the temperature.** The ridge's heat is 118 against 305 TW.
At its observed 8 Sv the same water would carry only ~160 TW. The inflow crosses the ridge at 3.8 C on average.

**Why it arrives cold.** Along the main branch (t_in, the inflow; sst, the sea it flows in; t_eq, its target):

| cell | Q Sv | t_in C | model sst C | t_eq C |
|---|---|---|---|---|
| 58.6 N 18.5 W | 6.35 | 9.93 | 10.79 | 2.94 |
| 59.8 N 9.8 W | 4.67 | 7.62 | 9.74 | 2.49 |
| 62.0 N 8.2 W | 4.67 | 6.50 | 8.03 | 1.08 |
| 64.2 N 6.4 W | 3.81 | 5.18 | 6.91 | 0.14 |
| 66.6 N 1.4 E | 3.68 | 2.95 | 4.44 | -1.13 |
| 68.6 N 4.5 E | 2.38 | 1.48 | 3.27 | -1.80 |
| 70.6 N 8.2 E | 1.97 | 0.30 | 2.33 | -1.80 |

- Each cell keeps ~0.8 of the inflow's excess over t_eq (exp(-mix/Q), mix ~0.85e6 m3/s, Q ~4 Sv). That is a loss of
  60 x 6-8 C, **~400-500 W/m2 as an annual mean**, over the route's 250 km.
- Spread over the Nordic seas, Tsubouchi's 305 TW is ~120 W/m2. So the real loss is gentler and spread wider, and it
  ends with warmer water.
- **From 59.8 N on, the inflow is 1.5-2 C colder than the sea it flows in.** The inflow *is* the surface water
  there. Its target is the latitude's profile (2.5 C at 60 N, the freezing point north of 66 N), not the air over a
  sea that the Atlantic water itself keeps at 8-10 C.

## 4. Candidates and screens

Each candidate is planet-generic:
- none uses an Earth location, basin or number;
- λ was re-fitted only to the same process budget lane 142 used (RAPID -> OSNAP, 34% of the 26.5 N heat left at
  60 N).

- **(A) Relax the inflow toward the sea around it without the inflow (`sst0`) instead of the latitude's profile.**
  - Why: the air over the inflow sits over a sea that the wind-driven currents have already warmed.
  - Predicted: less loss everywhere the gyres warm the sea, and more heat at the ridge.
  - Switch `moc_tgt` = 1.
- **(B) Let the air over the inflow take up part of the sea's warmth.** The target is t_eq + k (sst - t_eq), with
  `sst` the overturning's own iterated sea.
  - k = 1 - exp(-h / air_km_sea) = 0.55, from the model's own boundary-layer constant (300 km) and the L5 cell
    width (240 km). It was not fitted.
  - Predicted: a broad warm sea, like the Nordic seas filled by the inflow, loses less than a narrow current does.
  - Switch `moc_tgt_sst`.
- **(C) The bulk sensitivity's Clausius-Clapeyron part.** λ x (γ + Δ(sst)) / (γ + Δ(15 C)), with the Penman slope and
  γ already in `climate.py`.
  - Why: the latent part of d(flux)/dSST halves every ~10 C, so cold Nordic water should lose less per degree than
    the Gulf Stream does.
  - Predicted: a slower decay north of the ridge.
  - Switch `moc_cc_ref`.

Results (Earth L6; heat in PW above all the N Atlantic's sinking water; SST in C against OISST):

| arm | 26.5 N | 60 N | 65 N | 60N/26.5N (Earth 34%) | ridge Sv / C / TW (Tsubouchi 305) | box 40-60 N SST (11.9) | Nordic SST (7.2) | band 60-70 N (4.30) |
|---|---|---|---|---|---|---|---|---|
| **main** (λ 60) | 1.13 | 0.40 | 0.02 | 35% | 5.80 / 3.76 / 118 | 11.9 | 4.5 | 2.09 |
| A, λ 60 | 1.14 | 0.47 | 0.05 | 41% | 5.14 / 4.77 / 109 | 12.2 | 5.3 | 2.38 |
| A, λ 120 | 1.11 | 0.29 | 0.02 | 26% | 4.59 / 2.82 / 65 | 10.6 | 3.6 | 1.50 |
| B, λ 60 | 0.96 | 0.46 | 0.05 | 48% | 5.31 / 7.45 / 136 | 13.0 | 6.7 | 3.17 |
| B, λ 90 | 0.99 | 0.36 | 0.03 | 36% | 5.11 / 5.30 / 100 | 12.0 | 5.2 | 2.43 |
| B, λ 120 | 1.00 | 0.30 | 0.02 | 30% | 4.95 / 4.14 / 81 | 11.3 | 4.4 | 2.00 |
| C, λ 60 | 1.11 | 0.41 | 0.03 | 37% | 5.79 / 4.51 / 128 | 11.9 | 4.8 | 2.28 |
| C, λ 80 | 1.11 | 0.34 | 0.01 | 31% | 5.66 / 3.25 / 103 | 11.2 | 3.9 | 1.84 |
| C + B, λ 80 | 0.96 | 0.40 | 0.05 | 42% | 5.26 / 6.50 / 119 | 12.3 | 6.0 | 2.80 |

Winter half-swings were unchanged in every arm: Nordic 0.49-0.57 against OISST 2.07, NE 0.39-0.41 against 2.01.
None of these candidates touch PW-1413.

**Reading.**
- **Strike 1 (A), strike 2 (B), strike 3 (C).** In every arm, the Nordic SST moves in lockstep with the subpolar box.
  - Where the box is right (main; B λ 90; C λ 60), the Nordic seas sit at 4.5-5.2 C against OISST's 7.2.
  - The arms that warm the Nordic seas to ~6-6.7 (B λ 60, C+B) warm the box 0.4-1.1 C over OISST and leave less than
    Earth's share at 26.5 N.
  - None moves the ridge's heat past 136 TW (Tsubouchi 305).
  - None moves the heat at 65 N past 0.05 PW (the ticket asks >= ~0.2).
- **One exchange law can't separate the box and the Nordic seas.**
  - They are one route, and the box sits upstream of the ridge.
  - Any change that keeps more heat for the Nordic seas keeps it in the box first, and λ has to take it back.
  - The 4x gap in decay per km (section 3) needs something the subpolar gyre's inflow doesn't have and the Nordic
    branch does.

## 5. What I think it is, for the next attempt (not screened)

- **The inflow is one narrow stream with one law, while the real Atlantic water north of the ridge is a wide
  slope-current system.**
  - The real system spreads its heat loss over the eastern Nordic seas at ~120 W/m2.
  - The model drops it within 250 km of the route at 400-500 W/m2.
  - A route that widens where it becomes the polar sea's surface water would lose more, not less, at the same λ.
    So the fix is not the width.
  - The fix is that the heat loss is against air that the broad warm sea has already warmed. That is B, but with the
    air's real fetch over warm water, upwind over many cells, not one cell's k.
  - The model already carries that air (`_winter_air`, `air_km_sea`). The inflow's relaxation would need it on the
    overturning's grid, which `ocean.solve` doesn't have. That is a structural change (an air pass inside `solve`),
    not a TUNE.
- **Or the inflow's surface imprint is the issue, not its route.** sst = sst0 + share x (t_in - t_eq) uses t_eq as
  the base. Where share ~1 the sea should be t_in itself, not sst0 plus the anomaly.
  - In the table in section 3, the model sst sits ~1.5-2 C *over* t_in north of 60 N, where the share is near 1.
    sst0's own anomaly over t_eq is added on top of the inflow's, so the inflow looks warmer at the surface than it
    is.
  - This needs its own look at `climate.sea_surface` and `ocean.solve.sst_c` (PW-265 / PW-589 conserve the heat
    through `moc_zonal`).
- **PW-1412 (winter air over a heat-losing sea) shares the root only through B's idea**, the air over the sea.
  PW-1412's gap is the *winter* air-sea contrast, from the bulk sensible flux. This lane's gap is the inflow's
  annual loss against the air. Same physics (the air over a warm sea), different place in the code. I didn't take
  PW-1412.
- **PW-1413 not attempted.** Lane 142's 100 m `moc_winter_m` is fitted to OISST, and no source I could open gives a
  cooling-season mixed-layer depth.
  - Cheap argument for the next lane: below the summer layer sits last winter's water. The winter must remove the
    summer's heat from the shallow layer before the inflow layer's own heat takes part.
  - So the cut should apply to the inflow's *extra* winter loss, not to the whole own swing. That predicts a winter
    half-swing near the own swing x (1 - share x something smaller than 0.9).

## 6. Not done

- No paired judge, as briefed. There is no candidate.
- No earth_check L7 or scorecard: no arm was good enough to spend them on.
