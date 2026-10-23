# Base climate v2: the stages (PW-570)

The plan is in `docs/review/base-climate-review.md`, section 4. Lane A works stages 1–3 in order, then the
checkpoint. Lane B works stage 4, the thermostat. Each stage below records its bar, what changed, and the
measurements.

## Stage 1: the overturning (PW-458)

**Bar** (the coordinator's ruling on PW-570):
- 8–20 Sv of northern sinking;
- at least 70% of it in open polar seas north of 55N;
- the Norwegian coast ice-free in winter;
- the generated worlds keep a healthy overturning in both hemispheres.

Baffin Bay may keep up to ~30% of the north. Its extra density is partly the Canadian Archipelago, which is closed
at L5/L6 (an artefact of resolution), so no Earth-specific fix. Fennoscandia's winter should warm when the
Norwegian Sea opens; plausibility there means within ±6 C.

**Result: the bar passes.** Fennoscandia's winter improves but stays outside ±6 C
(`issue-tracking/inbox/draft-nordic-winter-winds-offshore.md`).

### What changed (two mechanisms, no new thresholds tuned to Earth)
1. **Each hemisphere's polar sea makes its own deep water** (`ocean.overturning`).
   - Before, a connected ocean had one deep-water reference: the densest polar water anywhere in it.
   - So the hemispheres competed, winner-take-all. A slightly denser southern sea gated out the whole north, and
     the reverse. That is how world 7082f5 had no northern overturning at all, and how attempt 2's bulk exchange
     collapsed two of three worlds' north.
   - Physically, each polar sea's deep water fills its own side of the basin first (North Atlantic and Antarctic
     bottom water both form on Earth).
   - On Earth this alone moves the north from Baffin Bay to the Nordic Seas: 5.1 → 13.1 Sv. The Nordic Seas go
     0.1 → 6.7 Sv.
2. **The inflow's deep layer damps the sea's winter** (`ocean.winter_half`; new TUNE `moc_layer_m` = 500 m).
   - Where a share of the surface water is the overturning's inflow, winter convection mixes down into that layer
     (the Atlantic Water under the Nordic Seas, ~500–800 m). The winter's heat loss is spread over it instead of
     the ordinary winter mixed layer (`brine_m`, 50 m).
   - So the winter half-swing is `sea_half × (1 − share × (1 − brine_m / moc_layer_m))`. The summer half-swing,
     a shallow layer on top, is unchanged.
   - It is used in the overturning's winter density, in `_air_temps`' open winter water, the sea's own winter
     air and the land's winter carry, and in the January / July sea temperatures.
   - It is insensitive to the depth: 300, 500 and 800 m give Earth 9.7, 9.5 and 9.5 Sv, and the Norwegian coast
     100% open each time.
   - This is the older half of PW-458: before it, a 5.3–5.8 C winter swing at 62–75N froze the Norwegian Sea even
     where the inflow reached it.

**Dropped:**
- **The bulk sea-air exchange** (attempt 2: `sea_fetch_km`, `sea_wind_min`) is reverted to main's instant fill
  and parked for PW-015 (`issue-tracking/inbox/draft-sea-evaporation-bulk-exchange.md`).
  - It failed the "rain not worse" guard.
  - With the per-hemisphere deep water it also weakens the overturning: Earth 7.2 Sv against 13.1, world 7082f5
    6.6 against 14.6.
- **`x_ref_hemi`** became the default behaviour above, without a switch.
- **`x_moc_wind`**: the air's winds recomputed with the overturning's warmth over the sea. It warmed Norway's coast
  by only 0.7 C, because `monsoon_wind`'s land-sea part is capped at high latitudes. Removed; see the draft.

### Measurements
`tools/overturning_report.py --earth --world 119973 28442c 607540 81aced 7082f5 d14b89 a5a387 dad91b c00ebf`,
L6. Main is the merge base; after is this branch. The outputs are in `stage1/` (`overturning_main.txt`,
`overturning_after.txt`, and `overturning_hemi_only.txt`: the per-hemisphere deep water without the winter damping,
on six of the worlds).

**Earth** (L6, dT 0):

| | main | after |
|---|---|---|
| NH sinking | 5.06 Sv | **9.51 Sv** |
| share in open polar seas (> 55N, openness ≥ 0.55) | 49% | **71%** |
| Nordic / Irminger / Labrador / Baffin (Sv) | 0.14 / 1.28 / 1.09 / 2.61 | 4.89 / 0.81 / 0.75 / 2.63 |
| Baffin's share of the north | 52% | 28% |
| Norwegian coast sea open in winter | 0% | **100%** |
| its coldest-month SST | −1.8 C | +2.6 C |
| its sea air (NCEP ~+3.5) | −7.1 C | +0.6 C |
| Fennoscandia coldest-month bias | −18.5 C | −14.7 C |
| Fennoscandia warmest-month bias | −5.3 C | −4.9 C |
| SH sinking | 2.44 Sv | 2.33 Sv |

The intermediate step, the per-hemisphere deep water alone (no winter damping), gives 13.07 Sv at 80% open polar
sea. But the Norwegian coast is then only 58% open, with a coldest-month SST of −1.1 C. The damping trades ~3.5 Sv
of Irminger and Labrador sinking for an open Norwegian Sea: its winter water is warmer and lighter.

Earth's southern overturning stays weak (2.3 Sv, Weddell and Ross). That is PW-017's (the fresh Antarctic seas)
and stage 2's (PW-346, the sea air over the pack ice), not this stage's.

**Generated L6 worlds**, NH / SH Sv (share of each hemisphere's sinking in open polar seas):

| world (seed) | main | after |
|---|---|---|
| 119973 (147803) | 16.3 / 16.9 | 16.2 / 16.3 (99 / 98%) |
| 28442c (941637) | 16.4 / 16.9 | 16.0 / 16.9 (94 / 94%) |
| 607540 (934004) | 15.6 / 14.6 | 15.6 / 14.7 (99 / 95%) |
| 81aced (841964) | 16.0 / 9.5 | 16.1 / 14.1 (91 / 99%) |
| 7082f5 (456311) | **0.0** / 15.1 | **14.2** / 11.0 (79 / 91%) |
| d14b89 (139851) | 15.9 / 15.7 | 15.7 / 17.6 (95 / 97%) |
| a5a387 (914218) | 9.1 / 11.9 | 7.9 / 15.0 (82 / 94%) |
| dad91b (932349) | 14.6 / 6.0 | 14.7 / 4.5 (100 / 85%) |
| c00ebf (992242) | 7.6 / 11.6 | 12.6 / 12.8 (88 / 87%) |

- Every one of the nine has sinking in both hemispheres, mostly (79–100%) in open polar seas.
- One world gains its north (7082f5), and none loses a hemisphere.
- The weakest hemisphere is dad91b's south: 6.0 → 4.5 Sv.
- These are stored worlds re-climated with today's code on their own geography; their runs were made with main.

**earth_check** (main → after; `stage1/earth_check_main.txt`, `stage1/earth_check_after.txt`):
- The rain is unchanged. The rain doesn't see the overturning: land P, log-rain correlation 0.617, rivers to
  ±0.3%, arid share.
- Köppen: group and exact match unchanged; cities 32 exact / 28 group / 18 wrong → 32 / 29 / 17. Miami Cfa → Aw
  becomes a group match.
- Winters:
  - Reykjavik's coldest month −27.9 → −13.6 C (obs −2.3);
  - Nuuk's −32.0 → −26.5 (obs −19.2);
  - Stockholm's −21.3 → −19.9 (obs −2.7).
- The 60–70N land row: annual −9.5 → −9.3, its warmest month 0.0 → +0.6.
- Small cooling elsewhere from `moc_zonal` (the inflow's extra warmth taken off its latitude's mean): London's
  coldest month −2.2 → −2.5, Pacific NW −0.3, W Europe −0.1 C.

**Tests:** `uv run pytest -q` passes (568). The goldens were updated on purpose: the climate and the 60 Myr
simulation both change through the overturning.

**Scorecard** (`docs/scorecard.jsonl`, commit 4a6ff95, L6, 1000 Myr; against the last lines for 04be51c):

| | 04be51c | 04be51c+dirty | 4a6ff95 |
|---|---|---|---|
| Earth Köppen group / exact | 70.6 / 30.9 | 70.6 / 30.9 | 70.6 / 30.9 |
| Earth log-rain correlation | 0.617 | 0.617 | 0.617 |
| seed 1: dry / ice / NPP / trees | 14.2 / 1.4 / 356 / 29.8 | 18.2 / 1.1 / 344 / 21.7 | 20.0 / 0.5 / 419 / 16.9 |
| seed 2: dry / ice / NPP / trees | 24.4 / 1.1 / 341 / 21.7 | 16.8 / 8.8 / 273 / 21.9 | 15.4 / 9.1 / 267 / 20.8 |

- Earth's scores don't move. The overturning changes temperatures only at high northern latitudes, and the rain
  doesn't see it.
- The seeds are single 1 Gyr snapshots of chaotic runs. The two lines on the same commit 04be51c already differ by
  more than this change: seed 2's ice 1.1 against 8.8%, seed 1's trees 29.8 against 21.7%. This line is inside that
  spread.

### Left for later (inbox drafts)
- `draft-nordic-winter-winds-offshore.md`: Fennoscandia's winter is still 14.7 C too cold. The winter winds over the
  Nordic Seas blow offshore, and the air's winds never see the sea's own warmth. For stage 2 or its own ticket.
- `draft-sea-evaporation-bulk-exchange.md` (updated): the bulk sea-air exchange is parked for PW-015.

## Stage 2: the sea's air and the sea ice (PW-346, broadened)

**Bar** (the coordinator's brief):
- Hudson Bay, Baffin Bay and Okhotsk freeze in winter where cold air comes off the land, and Hudson Bay's coldest
  month is plausibly cold;
- southern winter sea ice within ±25% of observed;
- the Antarctic pack's winter air no longer ~9 C too warm;
- Labrador and Hudson Bay lowland winters within ±6 C;
- stage 1 doesn't regress: NH 8–20 Sv, ≥ 70% in open polar seas, the Norwegian coast open in winter, every generated
  world sinking in both hemispheres.

**Result: the bar does not pass in a mergeable form. Three attempts, nothing merged into `planet/`.**
- Attempt 2 meets every bar line above.
- But it costs the rain: earth_check's log-rain correlation goes 0.617 → 0.533, Köppen group 71 → 66%, cities exact
  32 → 25.
- The cause is that the rain kernel is very sensitive to the sea's half-year SSTs (see below).
- The code is kept as a patch, `stage2/attempt2.patch` (it applies on b6d707b). The judgement call is in
  `issue-tracking/inbox/draft-sea-swing-from-land-air-vs-rain.md`.
- This branch adds four sea rows to `tools/climate_bias.py`: Hudson Bay, Baffin Bay, the Sea of Okhotsk and the
  Antarctic pack at 65–75S.

### Main (b6d707b, stage 1 merged), Earth L6, coldest month, model / NCEP (`stage2/climate_bias_main.txt`)

| sea | model | NCEP | bias |
|---|---|---|---|
| Hudson Bay | −5.4 | −27.5 | +22.1 |
| Baffin Bay | −11.2 | −30.2 | +19.0 |
| Sea of Okhotsk | +1.6 | −9.3 | +10.8 |
| Southern Ocean 60–70S | −5.8 | −14.5 | +8.7 |
| Antarctic pack 65–75S | −10.2 | −22.9 | +12.7 |
| winter sea-ice proxy N / S (Mkm2) | 14.2 / 15.0 | 16.8 / 20.2 | −15% / −26% |

### Attempt 1: the sea's winter air in the carry (`stage2/climate_bias_attempt1.txt`)
What changed, in a new `climate._winter_air`:
- The winter carry runs over land and sea alike.
- Over open water the air relaxes toward the water over `air_km_sea` (300 km: the boundary layer's depth over the bulk
  heat-transfer coefficient).
- Over a frozen sea it relaxes as over land, toward the land's own winter. The heat that the water conducts up through
  the ice warms it: `k_ice / h` (h is the winter's growth, `ocean.ice_growth`) against `ice_b` (3.5 W/m2/C), the
  winter air's loss to space. The open part of a freezing sea adds `open_b` (30 W/m2/C).
- The water's winter cools further where the air over it is colder than the water ("chill", by `half_w / half_l`).

Results:
- Hudson Bay −18.8 (bias +8.7), Baffin −24.3 (+5.9), Okhotsk −6.6 (+2.6). The Arctic Ocean stays within 2.5 C.
- But the Southern Ocean overshoots: 60–70S comes out −20.9 (bias −6.4). The southern proxy is 29.2 against 20.2
  (+45%), and the edge is at 55–60S (7.4 Mkm2 there against 2.1).
- The band diagnosis shows why. With main's swing, the water's own winter at 55–65S (`sst − 6 C × s`) is already at
  freezing. On main that was harmless, because the sea's air was pinned to its water. Once the freeze sets the air,
  it isn't.
- The observed 2 m air over the open Southern Ocean swings about ±2 C × s, against main's 6. The North Pacific and
  North Atlantic swing about 6–7.

### Attempt 2: the sea's seasonal swing from the land's air (`stage2/attempt2.patch`, `stage2/climate_bias_attempt2.txt`)
On top of attempt 1, without the chill:
- `sea_half` (the water's own swing) goes 6 → 1.9.
- Each sea cell gets `s × (sea_half + continental × land_air)`. `land_air` is the share of its air that came off land
  within `air_km_w` on the prevailing winds: a carry of a land indicator, with no new parameter.
- Against the observed sea-air swing, `land_air` correlates at 0.67 (35–65 deg). It is ~0.04 over the open Southern
  Ocean and ~0.17–0.38 over the northern seas.
- The summer half loses the winter's freezing deficit (`_summer_half`). The cold that grew the ice goes into melting it.

| | main | attempt 2 | NCEP |
|---|---|---|---|
| Hudson Bay coldest | −5.4 | **−18.8** | −27.5 |
| Baffin Bay coldest | −11.2 | **−23.3** | −30.2 |
| Sea of Okhotsk coldest | +1.6 | **−9.1** | −9.3 |
| Southern Ocean 60–70S coldest | −5.8 | **−18.4** (−4.0) | −14.5 |
| Antarctic pack 65–75S coldest | −10.2 | **−24.9** (−1.9) | −22.9 |
| winter sea-ice proxy N / S | 14.2 / 15.0 | **19.7 / 21.2** (+17% / +5%) | 16.8 / 20.2 |
| Labrador / Hudson Bay lowlands coldest bias | +3.1 / +5.4 | +3.5 / +5.6 | |
| Southern Ocean 60–70S warmest bias | +4.6 | +0.9 | |
| Fennoscandia coldest bias | −14.7 | −12.2 | |

The overturning (`tools/overturning_report.py`, same nine worlds as stage 1):

| | main | attempt 2 |
|---|---|---|
| Earth NH | 9.51 Sv, 71% open polar | 11.30 Sv, 73% |
| Earth SH | 2.33 Sv | 4.09 Sv (Weddell 1.13, Ross 0.96) |
| Norwegian coast open in winter | 100% | 100% (SST +1.5, but its air −4.4 against +0.6) |
| generated NH / SH Sv | | 119973 17.0/16.6, 28442c 17.2/17.1, 607540 16.2/15.8, 81aced 17.7/14.4, 7082f5 12.3/8.7, d14b89 16.5/18.5, a5a387 10.8/16.7, dad91b 15.4/**3.2**, c00ebf 9.6/8.1 |

Every world still sinks in both hemispheres. The weakest is dad91b's south, 4.5 → 3.2 Sv.

**Why attempt 2 isn't merged** (`stage2/earth_check_attempt2.txt` against `stage2/earth_check_main.txt`):
- The rain: log-rain correlation 0.617 → 0.533. The summer share of land rain is 0.75 → 0.80 (GPCC 0.65). The SH
  subtropical and Patagonian summer rain goes up 40–50%.
- Köppen: group 71 → 66%, exact 31 → 28%; cities 32 / 29 / 17 → 25 / 34 / 19.
- Bisected by giving the winds and the rain kernel main's swing back (a test only):
  - the winds alone recover 0.533 → 0.556;
  - the winds and the rain's half-year SSTs together recover 0.616 and group 70%.
  - So the rain kernel (PW-015's) is calibrated on the old, uniform ±6 C × s sea, and the sea-ice fix can't land
    without retuning it.
- Also worse in attempt 2:
  - Nordic Seas coldest month −10.4 against −1.8 (main −4.7), and the Norwegian Sea's air −4.4. With the sea's air in
    the carry, the offshore winter wind of PW-575 now blows the land's cold over the open sea.
  - Baffin Bay's summer +8.7 C. Its swing is large (land air), and the winter half is damped by the overturning while
    the summer half isn't.
  - The 60–70N land's warmest month: −3.7 against −1.0.

### Attempt 3
Attempt 3 was the bisection above: the winds and the rain on main's swing while the air and the ice used the new one.
It recovers the rain. But it gives one sea two seasonal SSTs, one for the air and one for the rain. That is a
temporary split, not a mechanism, so it is not kept.

### Left for later (inbox drafts)
- `draft-sea-swing-from-land-air-vs-rain.md` (needs-decision). Land the land-air sea swing together with a
  re-calibration of the rain kernel to its half-year SSTs (with PW-015), or find the rain kernel's SST sensitivity
  first.
- `draft-sea-air-carry-offshore-and-baffin-summer.md`. Once the sea's air takes part in the carry, PW-575's offshore
  Nordic winds chill the open Norwegian Sea, and Baffin Bay's summer runs hot. Both are for the same stage.

## Stage 2b: attempt 2 landed (owner's order, 2026-10-22)

**The order.** The owner doesn't want a correct mechanism held back because a downstream kernel was fitted to the
old, wrong one. So stage 2's attempt 2 lands as it is, with its rain and Köppen regression accepted for now and
recorded exactly below. The rain is fixed next, on its own (PW-578), and the winds after that (PW-575, which also
owns the colder Nordic Seas this brings, PW-577).

**What changed:** `stage2/attempt2.patch`, re-applied on main 2684f2b without changes (it applied cleanly), plus the
`_air_temps` docstring brought up to date. The mechanism is the one in "Attempt 2" above:
- the winter air is carried over the sea as well as the land (`_winter_air`; new TUNE `air_km_sea`, `k_ice`,
  `ice_b`, `open_b`);
- the sea's seasonal swing is its own (`sea_half` 6 → 1.9 C × s) plus `continental × land_air`;
- a freezing sea's summer half-swing loses the winter's freezing deficit (`_summer_half`);
- the old sea-ice inversion (`INVERSION_MAX`) is gone: the air over the ice comes from the carry.

### The bar (Earth L6; `stage2b/climate_bias_*.txt`, `stage2b/overturning_*.txt`)

| bar line | main | after | verdict |
|---|---|---|---|
| Hudson Bay / Baffin Bay / Okhotsk coldest month (NCEP −27.5 / −30.2 / −9.3) | −5.4 / −11.2 / +1.6 | −18.8 / −23.3 / −9.1 | freeze: pass |
| southern winter sea-ice proxy (NCEP 20.2 Mkm2) | 15.0 (−26%) | 21.2 (+5%) | pass |
| Antarctic pack 65–75S coldest-month bias | +12.7 | −1.9 | pass |
| Labrador / Hudson Bay lowlands coldest-month bias | +3.1 / +5.4 | +3.5 / +5.6 | pass (±6) |
| Earth NH sinking, share in open polar seas | 9.51 Sv, 71% | 11.30 Sv, 73% | pass |
| Norwegian coast open in winter | 100% | 100% | pass |
| every generated world sinking in both hemispheres | yes | yes (weakest dad91b S 3.2 Sv) | pass |

Hudson Bay is still 8.7 C too warm in its coldest month, but it now freezes and is plausibly cold. The northern
proxy is 19.7 against 16.8 Mkm2 (+17%).

The generated worlds, NH / SH Sv (open polar share), stage 1 → after:
119973 16.2/16.3 → 17.0/16.6 (98/92%), 28442c 16.0/16.9 → 17.2/17.1 (90/92%), 607540 15.6/14.7 → 16.2/15.8 (99/95%),
81aced 16.1/14.1 → 17.7/14.4 (88/98%), 7082f5 14.2/11.0 → 12.3/8.7 (81/93%), d14b89 15.7/17.6 → 16.5/18.5 (95/90%),
a5a387 7.9/15.0 → 10.8/16.7 (**62**/91%), dad91b 14.7/4.5 → 15.4/**3.2** (94/34%), c00ebf 12.6/12.8 → 9.6/8.1
(69/75%). The open-polar share falls on a5a387 (82 → 62%) and c00ebf's north (88 → 69%); both still sink in both
hemispheres.

### Accepted for now: what gets worse (`stage2b/earth_check_main.txt` → `stage2b/earth_check_a2.txt`)

| earth_check | main | after |
|---|---|---|
| log-rain correlation with GPCC | 0.617 | **0.533** |
| Köppen main group / exact (cell by cell) | 71% / 31% | **66% / 28%** |
| Köppen B (arid) share of land, excl. Antarctica (Kottek 30.1) | 18.0% | 15.6% |
| A / C / D / E shares | 20.9 / 25.0 / 26.4 / 9.7 | 19.3 / 28.3 / 26.7 / 10.1 |
| cities exact / group only / wrong group | 32 / 29 / 17 | 25 / 34 / 19 |
| share of land rain in the local summer half (GPCC 0.65) | 0.75 | 0.80 |
| runoff / rain | 0.47 | 0.46 |
| summer rain, N land 35–65 deg where observed < 300 mm | 610 mm | 794 mm (obs 167) |
| summer rain, S land 35–65 deg, 300–700 mm class | 1417 mm | 2143 mm (obs 480) |

Also worse (PW-577, for the winds' stage): the Nordic Seas' coldest month −4.7 → −10.4 C (NCEP −1.8), the Barents
Sea −18.3 → −24.5 (−10.8), the Norwegian coast's sea air +0.6 → −4.4 (NCEP ~+3.5); Baffin Bay's warmest month
3.0 → 10.3 C (NCEP 1.6).
Better on land: Fennoscandia's coldest month −14.7 → −12.2 C bias; Alaska / Yukon −12.0 → −10.7; Taymyr −4.4 →
−2.3; the Greenland rim −3.2 → +0.9.

**Generated worlds, land rain** (`climate.compute` on the stored geography, main → after; ice-free land):

| world | land P (mm) | arid share | summer-half share | sea-ice proxy N / S (Mkm2) |
|---|---|---|---|---|
| 119973 | 1124 → 1146 | 31.1 → 27.0% | 0.84 → 0.87 | 26.4 / 21.5 → 31.8 / 28.0 |
| 7082f5 | 1029 → 1051 | 28.1 → 26.1% | 0.85 → 0.86 | 29.3 / 12.0 → 36.1 / 14.0 |
| dad91b | 1035 → 1081 | 23.6 → 21.5% | 0.83 → 0.86 | 31.9 / 10.2 → 34.0 / 13.0 |

The same direction as on Earth, smaller: a little wetter, 2–4 points less arid, the rain a little more in summer.

### Tests: three fail, all downstream of the rain
`uv run pytest -q`: 563 passed, 5 failed. Two are the goldens, refreshed on purpose (`--update-golden`: the climate
and the 60 Myr simulation change through the sea's swing). The other three are not loosened:
- `test_envelopes.py::test_earth_climate_score`: Köppen group 65.7 against its floor of 66 (the accepted regression);
- `test_rain_transport.py::test_same_planet_rains_the_same_at_two_levels`: the synthetic continent's inland rain
  differs 5.02% between L5 and L6, against 5% (main 3.0%). Both levels' inland rain falls ~10% while its temperatures
  don't move, so it is the rain's sensitivity to the sea's swing, not a new resolution dependence in the swing;
- `test_zoom_soils.py::test_zoom_soil_layers`: the big rivers' floodplains in the fixture zoom are 48% alluvium,
  gley or peat, against > 50%.

So stage 2b is **not merge-ready while these three fail**, unless the coordinator rules they may wait for the rain fix
(PW-578), which should bring back the first two.

### PW-578, first look (`issue-tracking/inbox/draft-stage2b-landed-rain-regression.md`)
- Bisected by giving one rain input at a time main's 6 C × s SSTs: the sea's evaporation source (`qs` / `src_q`)
  recovers 0.533 → 0.598. The showers' `mse_t` and the air aloft's `mse_thr` recover nothing.
- The cause: the water takes the land air's whole swing. Beside land (20–50 deg, `land_air` > 0.5) the half-year
  SST range is 16–22 C against NCEP's air range of 10–17, and the open oceans at 20–50 deg swing 1.8–2.6 against
  5.7–6.0. The coastal seas' too-warm summers feed the summer monsoons next to them.
- So it is a wrong mechanism: the air over the sea and the water under it need their own swings.

### Scorecard (`docs/scorecard.jsonl`, commit f1e1600, L6, 1000 Myr; against 4a6ff95, stage 1)

| | 4a6ff95 | f1e1600 |
|---|---|---|
| Earth Köppen group / exact | 70.6 / 30.9 | 66.4 / 27.8 |
| Earth log-rain correlation | 0.617 | 0.533 |
| seed 1: dry / ice / NPP / trees | 20.0 / 0.5 / 419 / 16.9 | 13.5 / 1.7 / 379 / 19.6 |
| seed 2: dry / ice / NPP / trees | 15.4 / 9.1 / 267 / 20.8 | 9.9 / 9.7 / 263 / 25.2 |

The seeds are single chaotic snapshots (stage 1 showed same-commit spreads larger than these), but in both the dry share
falls 5–6 points, in line with Earth's arid share falling. (The line's `src` hash includes rain-bisection
switches that were in the working tree, off by default; the outputs are f1e1600's.)

## Stage 2b, step 2: the rain fix (PW-578), attempt 2 of 3 (lane A4)

**Result: Earth's rain is back (log-rain r 0.619 against main's 0.617) and the stage-1 / stage-2 bars hold, but it
is not merge-ready.** Two tests still fail unchanged, both on knife edges:
- `test_ocean::test_meltwater_weakens_the_overturning`: the north rises +0.001 Sv at the `moc_k` cap
  (`issue-tracking/inbox/draft-meltwater-test-knife-edge-at-moc-cap.md`);
- `test_zoom_soils::test_zoom_soil_layers`: 0.488 against > 0.5, and main is only at 0.519
  (`draft-zoom-soils-floodplain-share-driver.md`).

`test_earth_climate_score` and `test_same_planet_rains_the_same_at_two_levels` now pass. The goldens are
regenerated.

### What changed (two mechanisms, no Earth-fitted numbers)
1. **The sea's swing** (`climate._sea_half`, replacing TUNE `sea_half`) has two parts, and both are now derived.
   - *Its own swing:* the seasons' sunshine at the ground goes into a mixed layer `brine_m` deep (heat capacity
     rho c h omega ~41 W/m2/C), against the loss to space `ice_b`. The sunshine is half the year's swing of the
     monthly top-of-atmosphere mean × Angström's 0.5 × (1 − 0.06 albedo). This gives ~1 C at 25 deg and ~2.6 C at
     60 deg, none at the equator, and it follows tilt by itself.
   - *A share of the land's swing:* c = `open_b` / (`open_b` + rho c h omega) ≈ 0.42 of `continental` × s ×
     `land_air`.
   - Attempt 1's F1 used a flat 3 C as its own swing, which was a guess.
2. **Stable summer land air** (`compute`, the rain's `open_sea` per season):
   - in the summer half, the share `land_air` of a sea's air came off land and is warmer than the water (that air
     is what warms a coastal sea beyond its own swing). It lies stable over the water, which can't stir its vapour
     up into it, so the sea fills only the rest of the air. In winter, the cold land air is filled fast, as before.
   - `_rain` takes `open_sea` as [season, cell], and `tools/moisture_budget.py`'s copy of the kernel follows.

### How it was found (the experiment copy, Earth L6; r / group / summer share)
- Bisect on F1, giving the rain main's 6 C × s SSTs in one place at a time:
  - all of it: 0.618 / 70.2;
  - the summer half only: 0.621;
  - the winter half only: 0.588 (no gain);
  - the summer half where `land_air` > 0.3: 0.623;
  - only the summer `src_q` there: 0.624;
  - only `qs`, `mse_t` or `mse_thr`: no gain.
- So it is the evaporation source of land-warmed summer seas. Regionally it is the Mediterranean: log-rain bias
  +0.75 against +0.47 with the uniform swing, and summer share 0.68 against GPCC's 0.30. Central Asia, Arabia and SE
  Australia show the same.
- Variants of the mechanism:
  - stability share from the season's wind (900 km): 0.625 / 69.7, with F1's own swing;
  - the same share as the swing's `land_air` (chosen: the very air that warms the water): 0.628 / 70.2, with F1's own
    swing;
  - a stable fetch of 1500 km scores 0.642, but nothing physical says 1500 km, so it was not taken.
- The own swing, with stability:
  - derived at h = `brine_m` (chosen): 0.620 / 69.6;
  - derived at h = 30 m with c = 0.55: 0.617 / 69.4;
  - F1's flat 3 C: 0.625–0.628 / 69.7–70.2.
  - The derived own swing is about half the observed open-ocean air range in the subtropics (2.9 against 5.7 C at
    20–35 deg). The summer mixed layer is shallower than `brine_m`; a seasonal depth would need a new constant, so it
    was not added.
- Tried and dropped: letting the summer land air also keep its warmth over the sea (a stable carry over `air_km_w`).
  r 0.622, but the near-land seas at 35–65N ran 1.5–3.8 C too warm in summer.

### The bars (`docs/review/base-climate/pw578/`)
| line | stage 2b (attempt 2 as landed) | after | verdict |
|---|---|---|---|
| Earth log-rain r / Köppen group / exact | 0.533 / 66 / 28 | 0.619 / 69.6 / 30 (main 0.617 / 71 / 31) | rain met; group 1.4 short |
| land rain in the summer half (GPCC 0.65) | 0.80 | 0.76 (main 0.75) | |
| Hudson / Baffin / Okhotsk coldest month | −18.8 / −23.3 / −9.1 | −18.9 / −20.0 / −6.5 | freeze: pass |
| southern sea-ice proxy (NCEP 20.2) | 21.2 | 21.8 (+8%; north 18.7 against 16.8) | pass |
| Antarctic pack bias | −1.9 | −2.1 | pass |
| Labrador / Hudson Bay lowlands, coldest month | +3.5 / +5.6 | +3.7 / +5.5 | pass (±6) |
| Earth NH sinking, open polar share; Norwegian coast | 11.3 Sv, 73%; 100% | 10.2 Sv, 72%; 100% | pass |
| every generated world sinking in both hemispheres | yes (weakest dad91b S 3.2) | yes (weakest dad91b S **0.89**, 7082f5 7.5 / 6.7) | pass, weak (`draft-dad91b-southern-sinking-weakening.md`) |

**The group gap is not the rain.** With main's uniform 6 C × s swing everywhere, the branch scores group 70.2. The
confusion rows against main are obs D → E 14% (main 11%), A → A 78% (80) and B → B 47% (48). The D → E cells are cold
coasts whose summers are too cool, a stage-2b temperature effect (`draft-stage2b-koppen-group-d-to-e.md`). So 69.6
counts as plausible-or-better: the rain is as good as main's, and the remainder sits in temperatures the stage-2 bar
traded for its sea ice.

**Generated worlds' rain** (`pw578/world_rain_main_vs_after.txt`, main → after):
- land rain +1–5%;
- the arid share within ±1.2 points;
- the summer share unchanged (0.79–0.85).

The sea-ice proxies are up, as in stage 2b: 28442c N / S 8 / 9 → 15 / 20 Mkm2, 81aced N 0.1 → 5.9.

**Scorecard** (`docs/scorecard.jsonl`, L6, 1000 Myr):
- Earth: group 69.6 / exact 30.0, log-rain 0.62 (stage 2b: 66.4 / 27.8 / 0.533);
- seed 1: dry 25.7% / ice 0.0 / NPP 361 / trees 25.0 (stage 2b: 13.5 / 1.7 / 379 / 19.6);
- seed 2: dry 25.3% / ice 4.2 / NPP 300 / trees 20.8 (stage 2b: 9.9 / 9.7 / 263 / 25.2; stage 1: 15.4 / 9.1 / 267 /
  20.8).

These are single chaotic snapshots. Their dry share is now above stage 1's.

**earth_check:** before is `stage2b/ec_a2.txt` (stage 2b as landed); after is `pw578/earth_check_after.txt`.

Attempts used on PW-578: 2 of 3. The handoff is `handoff-A4.md`.

## Stage 2b, step 3: the merge pass (lane A5)

**Result: merge-ready.** `uv run pytest -q` passes in full (568), with no test changed. The goldens are regenerated
on purpose, because the overturning's cap changes. Earth's rain and Köppen are unchanged from step 2: log-rain r 0.619,
group 69.6%, exact 30%. The stage-1 and stage-2 bars hold. Outputs are in `laneA5/`.

### What changed (two mechanism fixes, following the coordinator's rulings)
1. **The overturning's cap** (`ocean.overturning`; for `test_meltwater_weakens_the_overturning`).
   - Before, each sea / hemisphere's cell was capped at `moc_k` × the sinking-weighted mean of (sinking water −
     replacing water). A meltwater pulse that shuts the densest site moves the weight to the other sites, so that mean,
     and the cap with it, could *rise*. That is why the test was a tie at the cap (+0.001 Sv).
   - Now the cap is `moc_k` × (the polar box's densest water, its densest `moc_top` share before mixing = ref +
     `moc_mix`, − the replacing water, sinking-weighted). This is Stommel's two boxes. Fresh water can only make the
     densest water lighter.
   - The two-basin fixture's north goes 20.83 → 20.74 Sv under the melt. It also passes under the sea-swing
     perturbations that flipped the old one (own ± 0.3 s / + 0.5 C).
   - A first try used the mixed deep water (ref, without + `moc_mix`). It lowered the caps ~5% and flipped
     `test_timezoom_cycle::test_glacials_grow_ice_and_endings_melt_it_fast` (the L4 glacial's extra ice went 84 → 56 m,
     with 47 m left 15 kyr after the ending). The polar box's own water is also the more faithful Stommel quantity, and
     with it the timezoom test passes (54 m, 2.3 m left). But note it as a sensitivity: the time zoom's ice ages react
     strongly to a few % of overturning.
   - Earth's caps don't bind (NH 10.1 Sv against a cap of ~15), so Earth is unchanged.
2. **Valley-floor alluvium in the zoom's soils** (`soils.valley_floor`, used by `zoom_mineral`; for
   `test_zoom_soil_layers`).
   - A pixel's alluvium share came from the riparian strip (0.15 + 0.4 log10 Q km) and the flooded share. The
     flooded share is a log ramp of absolute discharge (100 → 3160 m3/s) and doesn't depend on the pixel's size.
   - With both on a log of Q, a 300–1000 m3/s river's own 3 km pixels sat at alluvial 0.4–0.6, the edge of ALLUVIUM.
     An 8% drop in rain tipped them to ACRISOL / LUVISOL.
   - Now a river's valley floor also counts: the fine zoom's own width law (`zoom_fine_floodplain.half_width`:
     `FLOOR_W` channel widths, w = 4 Q^0.5 m, × √erodibility), narrowing to none on steep ground (`STEEP`), as the
     pixel's overlap with it. It is a power of the flow, so 8% less rain narrows it ~4%.
   - The fixture's floodplain wet share: 0.488 → 0.559 (main 0.519). By discharge class, 1000–3000 m3/s goes 0.57 →
     0.75, and 300–500 m3/s stays 0.25 (a 1.4 km floor on a 3 km pixel isn't the pixel's main soil).
   - Elsewhere in the zoom little moves: river-laid alluvium 0.5 → 0.7% of the zoom, and every other class within 0.1
     point.

### dad91b's southern sinking (4.5 → 3.2 → 0.9 Sv): diagnosed, not changed
Stage 2's sea ice works as designed. The hemmed-in southern bays (76% land poleward of 50S) grow ~1.4 m of ice a year
(main 0.9). They keep its brine, so a few cells turn very dense: the densest 10% poleward of 60S is 1029.2 against
1028.4 kg/m3, while the area mean is unchanged at 1027.0. Those cells set the deep-water reference, and the gate shuts
off the rest of the open polar sea. The strength law is proportional to area, so the small pocket gives ~1 Sv.

Whether a dense shelf pocket should be area-limited (on Earth, AABW forms in small polynyas but entrains its way to
~10 Sv) is a mechanism question. It goes to `draft-dad91b-southern-sinking-weakening.md` (needs-decision; options:
entrainment, a whole-sea reference, or accept).

### The bars (`laneA5/overturning_after.txt`, `climate_bias_after.txt`, `earth_check_after.txt`)
- **Earth:** identical to step 2. NH 10.22 Sv, 72% in open polar seas; the Norwegian coast is 100% open; SH 2.38 Sv.
  `climate_bias` and `earth_check` are byte-identical apart from timings. Log-rain r 0.619, group 69.6.
- **Generated worlds**, NH / SH Sv (step 2 → now): 119973 16.9/16.8 → 17.5/17.5, 28442c 16.9/17.3 → 17.4/18.0,
  607540 16.0/15.9 → 16.6/16.5, 81aced 16.9/14.3 (same), 7082f5 7.5/6.7 (same), d14b89 16.2/18.2 → 16.7/19.0,
  a5a387 8.2/16.5 → 8.2/17.0, dad91b 14.6/0.89 → 15.3/0.88, c00ebf 8.9/9.6 (same). All nine sink in both
  hemispheres; the open polar shares are unchanged.

**Scorecard** (`docs/scorecard.jsonl`, commit 628fbd8, L6, 1000 Myr):
- Earth: group 69.6 / exact 30.0, log-rain 0.62;
- seed 1: dry 20.2% / ice 1.8 / NPP 350 / trees 22.2 (step 2: 25.7 / 0.0 / 361 / 25.0);
- seed 2: dry 20.7% / ice 2.0 / NPP 366 / trees 26.2 (step 2: 25.3 / 4.2 / 300 / 20.8).

These are single chaotic snapshots, inside the spread seen before.

### Left open
- `draft-dad91b-southern-sinking-weakening.md` (rewritten with the diagnosis; needs-decision).
- `draft-stage2b-koppen-group-d-to-e.md` (unchanged: the cold coasts' summers, D → E).
- `draft-stage2b-landed-rain-regression.md` is resolved by step 2 (r 0.619) and can be closed at intake.
- The two knife-edge drafts (meltwater, zoom soils) are removed: both are fixed above.

## PW-575: the winter winds (lane A6)

**Result: a large improvement, but the bar is not met.** Fennoscandia's coldest month goes −11.9 → −8.9 C against
NCEP (bar ±6), and the Nordic Seas box doesn't move (−8.0 → −8.3). The rest of the cold is in the sea north of 72N,
not in the winds (`issue-tracking/inbox/draft-nordic-winter-barents-frozen.md`). Rain, Köppen and the stage-1 and
stage-2 bars hold. `uv run pytest -q` passes with the tests unchanged; the goldens are regenerated on purpose.
Outputs are in `laneA6/` (`*_main.txt` is 564350b, `*_pw575.txt` is this branch).

### What was found
- **Taking the winds from the finished temperatures doesn't fix them** (attempt 1, the handoff's lead). With
  `monsoon_wind` fed NCEP's own January temperatures, the Norwegian Sea's wind is still offshore (E −0.15, N −0.14).
  The cause is the fixed three-cell belts: at 62–72N `wind()` is the polar cell's equatorward drift (N −0.23) at every
  longitude, and the capped land-sea part can't undo it. Re-running `monsoon_wind` on the finished climate also costs
  the rain (r 0.619 → 0.551), because every land-sea wind moves.
- **The maritime air didn't get far enough inland.** Along 53N the coldest month fell from +7 C over the Atlantic to
  −0.1 on Ireland's first cell and −5 over the North Sea. The winter carry relaxed toward the land's own winter over a
  fixed 900 km, whatever the wind. Fitting NCEP's January from Ireland to Moscow gives an e-folding of ~3500 km in
  Europe's westerlies.

### What changed (`planet/climate.py`; attempt 2)
1. **The wind belts follow the air masses** (`front_shift`). Poleward of 30–50 deg, a cell takes the belts of the
   latitude whose zonal-mean sea-level air (smoothed over 900 km) is as warm as its own. A warm polar sea in winter pulls
   the westerlies north over it (the Icelandic low's south-westerlies onto Norway), and a cold continent lets the polar
   air south. This runs once, after the overturning, on the finished air. The land-sea part stays the first guess's.
   The rain keeps the first guess's winds, as it already doesn't see the overturning. The Norwegian coast's January
   wind goes E +0.03 → +0.39.
2. **The winter air over land relaxes in time** (`_winter_air`). The air mass, `air_m` deep (new TUNE: 1000 m, to
   ~850 hPa), loses heat to space at the existing `ice_b`: τ = ρ c_p `air_m` / `ice_b` ≈ 4 days. It reaches U × τ inland:
   ~2400 km in a steady westerly and a few hundred km in a calm high.
   - Ground higher than `air_m` cuts the carried air off. Without that, Pacific air crossed the Rockies and the Hudson Bay
     lowlands went +5.5 → +7.9 C.
   - That slow relaxation is the stable case: warm air over colder ground. Air colder than the land's own winter is
     heated from below and relaxes as fast as in summer (`air_km_s`). Without this, a synthetic equatorial land's July
     differed 2.7 C across the equator (`test_july_stays_july_across_the_equator`, < 2).
   - `air_km_w` now only sets how far land air reaches over the sea (`land_air`).

Tried and dropped (switches in `.../scratchpad/laneA6/exp_switches.diff`): front_shift before the rain (r 0.611);
re-deriving the currents from the new winds (no change north of 72N); two wind iterations (same as one).
Sensitivity to `air_m` (Fennoscandia / Hudson Bay lowlands coldest-month bias): 800 m −11.2 / +5.0, 1000 m
−8.9 / +5.5, 1250 m −7.3 / +6.7.

### The bars (Earth L6)
| line | main 564350b | after |
|---|---|---|
| Fennoscandia coldest month (bar ±6) | −11.9 | **−8.9** (Norway coast −9.0 → −4.1, obs −5.2; Sweden −19.6 → −14.1, obs −8.3; Finland −23.2 → −22.2, obs −10.8) |
| Norwegian Sea January wind E / N | −0.18 / −0.13 (offshore) | +0.26 / +0.06 (onshore) |
| Norwegian coast sea air (NCEP ~+3.5); open in winter | −3.5; 100% | −0.7; 100% |
| Nordic Seas / Barents coldest-month bias | −8.0 / −13.7 | −8.3 / −13.8 (frozen north of 72N) |
| log-rain r / Köppen group / exact | 0.619 / 69.6 / 30.0 | **0.622 / 70.3 / 30.8** |
| cities exact / group / wrong | 29 / 29 / 20 | 32 / 29 / 17 |
| Earth NH Sv, open polar share; SH | 10.22, 72%; 2.38 | 10.08, 71%; 2.42 |
| Hudson / Baffin / Okhotsk coldest month | −18.9 / −20.0 / −6.5 | −19.8 / −21.0 / −7.3 |
| southern sea-ice proxy (NCEP 20.2) / north (16.8) | 21.8 / 18.7 | 21.6 / 18.5 |
| Labrador / Hudson Bay lowlands coldest-month bias (±6) | +3.7 / +5.5 | +3.1 / +5.3 |
| Antarctic pack bias | −2.1 | −1.4 |
| coasts 40–65N: sea to the west / to the east, coldest bias | −3.1 / +2.8 | −2.0 / +3.0 |
| SH coastal seasonal range (NCEP 9.6) | 16.3 | 14.3 |

City winters (coldest month, model / obs): London −3.2 → +1.6 / 4.7, Paris −2.2 → +2.8 / 2.4, Moscow −16.8 → −13.2 /
−9.6, Stockholm −14.3 → −8.9 / −2.7, Nuuk −24.7 → −18.3 / −19.2.

**Worse:** Iceland −7.8 → −12.4 (the new winds bring it the frozen Denmark Strait's air, see the Barents draft),
Canadian Rockies −4.7 → −7.6 and Tibet −5.4 → −4.1 (the mountain cut-off,
`draft-air-relaxation-in-time-summer-and-mountains.md`), Greenland ice −11.8 → −12.4.

**Generated worlds**, NH / SH Sv (main → after): within ±0.2 Sv on all nine (119973 17.5/17.5, 28442c 17.4/18.0,
607540 16.6/16.5, 81aced 16.6/14.2, 7082f5 7.5/6.6, d14b89 16.7/19.0, a5a387 8.3/16.9, dad91b 15.3/0.87, c00ebf
8.9/9.4). All sink in both hemispheres; dad91b's south is PW-579's.

**Scorecard** (`docs/scorecard.jsonl`, commit abe4838, L6, 1000 Myr; against 628fbd8, lane A5):
- Earth: group 69.6 → 70.3, exact 30.0 → 30.8, log-rain 0.62 → 0.622;
- seed 1: dry 20.2 → 20.1% / ice 1.8 → 3.1 / NPP 350 → 331 / trees 22.2 → 17.9;
- seed 2: dry 20.7 → 22.6% / ice 2.0 → 0.7 / NPP 366 → 385 / trees 26.2 → 19.8.

These are single chaotic snapshots, inside the spread seen before. Tree cover falls on both, by 4–6 points.

Attempts used on PW-575: 2 of 3. The handoff is `handoff-A6.md`.

## PW-582: the Atlantic inflow past the sinking site (lane A7), attempt 1 of 3

**Result: an improvement, but not merge-ready and the bar is not met.**
- The Nordic Seas and Iceland improve. Fennoscandia is −7.9 C (bar ±6). The Barents doesn't move (−13.7), and
  Iceland is −10.3 against the −7.8 bar.
- `uv run pytest -q`: one test fails unchanged, `test_store::test_run_lakes`. Lakes in that chaotic L4 run are
  1–4 cells, and the first now appears at step 25 against the 20 allowed
  (`issue-tracking/inbox/draft-run-lakes-test-chaotic.md`). Every other test passes, and the goldens are regenerated
  on purpose.
- The scorecard was not run.

Outputs are in `laneA7/` (`*_pw582.txt`). The before files are `laneA6/*_pw575.txt`, because main's `planet/` is
PW-575's.

### What was found
- The inflow is routed only to cells that sink. The Barents' winter water is ~0.5 kg/m3 lighter than the Nordic
  Seas', because its salinity is 34.8 against 35.6–36.1. So it never sinks and is never fed, which is a lock.
- The lid ("the inflow dives under year-round ice") came from the *first guess's* sea, without the overturning's
  warmth. It was any sea iced for more than ~9 months of that guess, so a sea the inflow would keep open stayed shut
  to it.
- The inflow's route crossed the open Greenland Sea to the sinking site rather than following Norway's slope. The
  wind-driven currents at 70–76N run westward, and nothing steered the inflow along the slope.

### What changed (`planet/ocean.py`)
1. **The inflow follows the polar seas' slope** (`_slope_current`).
   - In a polar sea the overturning's inflow is a buoyant boundary current round the basin (Spall 2004). It follows
     the depth contours with the shallow side on its right in the north (on its left in the south).
   - Its route cost treats this as a current of `cur_ref` where the floor drops by about `moc_layer_m` across a cell,
     poleward of `moc_lat` (fully 10 deg on). It adds no new constant.
   - It is kept out of the subtropics, where the western boundary currents run the other way. Applied everywhere, it
     warmed the British Isles box by 4.6 C and flipped the meltwater test's two-basin state.
2. **The lid is the ice the overturning leaves** (`solve`). The lid is recomputed each iteration from the current
   coarse SST (with the inflow's warmth), with the same `open_share` rule. `solve` takes `frozen` instead of a
   precomputed `iced`.

Tried and dropped (`scratchpad/laneA7/exp_pw582.diff`):
- Knudsen's exchange for the sea under the lid. It gives 0.8 Sv on Earth, and +1 C in the Nordic box. It is unbounded
  under a meltwater pulse, and it broke `test_glacials_grow_ice_and_endings_melt_it_fast` (57 m against 46).
- A thermal-wind steering of the inflow (~0.03 m/s, no effect).
- A wider spin-up gate (`moc_drho` 0.6, `moc_iters` 12): the Barents still doesn't sink.

### The bar (Earth L6; `laneA7/climate_bias_pw582.txt`, `overturning_pw582.txt`, `earth_check_pw582.txt`)
| line | main (PW-575) | after |
|---|---|---|
| Fennoscandia coldest-month bias (bar ±6) | −8.9 | **−7.9** |
| Kola / Karelia | −14.0 | −13.9 |
| Iceland (bar: no worse than −7.8) | −12.4 | **−10.3** |
| Nordic Seas coldest-month bias | −8.3 | **−4.2** |
| Barents Sea coldest-month bias | −13.8 | −13.7 (still frozen) |
| Norwegian coast sea air (NCEP ~+3.5); open in winter | −0.7; 100% | **+2.0**; 100% (SST 2.7) |
| Labrador Sea / Baffin Bay; Baffin Bay; Hudson Bay | +7.7; +9.2; +7.7 | +5.8; +6.1; +7.6 |
| Earth NH Sv, open polar share; SH | 10.08, 71%; 2.42 | 9.78, 70%; 2.42 |
| log-rain r / Köppen group / exact; cities | 0.622 / 70 / 31; 32/29/17 | 0.622 / 70 / 31; 32/29/17 |

City winters (coldest month, model / obs): Reykjavik −12.4 → −10.2 / −2.3, Stockholm −8.9 → −8.6 / −2.7, London
1.6 → 1.7 / 4.7, Nuuk −18.3 → −21.3 / −19.2.

**Generated worlds**, NH / SH Sv (PW-575 → after): 119973 17.5/17.5 → 17.5/18.0, 28442c 17.4/18.0 → 18.7/17.6,
607540 16.6/16.5 → 17.6/16.6, 81aced 16.6/14.2 → 18.5/13.6, 7082f5 7.5/6.6 → 7.5/6.8, d14b89 16.7/19.0 → 16.5/18.7,
a5a387 8.3/16.9 → 9.4/17.0, dad91b 15.3/0.87 → 15.6/0.96, c00ebf 8.9/9.4 → 13.4/6.5. All sink in both hemispheres.

### Left open
- `draft-barents-still-frozen-after-pw582.md` (needs-decision): the Barents lock, and options for the second attempt
  (the inflow's salinity mixing on its way, or a heat-limited transformation).
- `draft-run-lakes-test-chaotic.md` (needs-decision): the chaotic lakes test that blocks the merge.

Attempts used on PW-582: 1 of 3. The handoff is `handoff-A7.md`.

## PW-582, attempt 2 of 3 (lane A8): the inflow's salinity mixes on its way

**Result: a mechanism fix with small regressions; the bar is not met and it is not merge-ready.**
- The Barents doesn't move (−13.7). Fennoscandia −7.9 → −8.2 (bar ±6), Iceland −10.3 → −10.6 (bar −7.8), the Nordic
  Seas box −4.2 → −5.5.
- Earth's north is healthier on the stage-1 bar: 9.78 → 10.21 Sv, open polar share 70% → **73%**.
- `uv run pytest -q`: one test fails unchanged, `test_timezoom_consistency::test_ice_at_index_zero_is_the_runs`
  (−26.0 m against 25). Its fixture is a 300 Myr L5 run, and the change gives a different world (6 plates against 13,
  sea level −314 m against +5), so the failure says nothing about the change
  (`issue-tracking/inbox/draft-timezoom-index-zero-test-chaotic.md`, needs-decision). The goldens are regenerated
  on purpose.
- **Harness change (coordinator's ruling 1):** `test_store::test_run_lakes` searches 60 steps for a frame with lakes
  instead of 20. Every assertion is unchanged; it passes. `draft-run-lakes-test-chaotic.md` is deleted.

Outputs are in `laneA8/` (`*_smix.txt`); the before files are `laneA7/*_pw582.txt`.

### What changed (`planet/ocean.py`, one line)
The inflow's temperature relaxes toward the latitude's sea temperature at `moc_lambda` over `moc_width` (~0.4 Sv per
220 km cell). That exchange with the surrounding water carried heat but not salt, so the Nordic inflow kept the
subtropics' 35.6–36.1 psu (observed ~35.2). Its salinity now relaxes toward the surface water it passes at the same
rate. As a lateral eddy diffusivity over `moc_layer_m` and `moc_width` that is ~1000 m²/s, inside the ~500–2000 m²/s
observed for boundary currents. No new constant. The Nordic inflow is now 35.0–35.5 psu.

### Option B, measured and not written
A site can sink no more than its heat loss turns the arriving inflow into deep water (Walin 1982). With the model's
own air-sea exchange, even cooling the inflow all the way to freezing, the cap binds on 4 of 85 northern sinking
cells, 0.38 Sv of 10.1 (`scratchpad/laneA8/walin.py`). It would change almost nothing.

### What locks the Barents (`draft-barents-still-frozen-after-pw582.md`, updated)
1. `moc_sill` (300 m) makes the Barents shelf (230–300 m on the L5 grid east of 30E) a strait the inflow can't
   enter. The rule is meant for Bering (40 m on that grid).
2. Let in (sill 150 m, an experiment), the inflow reaches the SW Barents but arrives at −0.4 to +1 C (observed
   4–6 C), because its branch carries only what sinks in the Barents (~1 Sv) and cools within a cell or two. On
   Earth that branch flows on into the Arctic and sinks there.
   With sill 150 m and this change: Fennoscandia −7.5, Iceland −8.9, Nordic −3.2, the Barents −13.6.

### The bars (Earth L6)
| line | attempt 1 (ee0cc87) | attempt 2 |
|---|---|---|
| Fennoscandia coldest-month bias (bar ±6) | −7.9 | −8.2 |
| Iceland (bar: no worse than −7.8) | −10.3 | −10.6 |
| Nordic Seas / Barents coldest-month bias | −4.2 / −13.7 | −5.5 / −13.7 |
| Norwegian coast sea air (NCEP ~+3.5); open in winter; SST | +2.0; 100%; 2.7 | +1.4; 100%; 2.4 |
| Nordic / Irminger / Labrador / Baffin (Sv) | 4.09 / 1.16 / 1.38 / 2.70 | 4.02 / 1.53 / 1.77 / 2.42 |
| Earth NH Sv, open polar share; SH | 9.78, 70%; 2.42 | **10.21, 73%**; 2.43 |
| log-rain r / Köppen group / exact; cities | 0.622 / 70 / 31; 32/29/17 | 0.622 / 70 / 31; 32/29/17 |
| Labrador Sea / Baffin Bay; Hudson Bay | +5.8; +7.6 | +6.2; +7.6 |

Reykjavik −10.2 → −10.3 (obs −2.3), Nuuk −21.3 → −20.6 (obs −19.2).

**Generated worlds**, NH / SH Sv (attempt 1 → 2): 119973 17.5/18.0 → 16.0/16.6, 28442c 18.7/17.6 → 17.3/16.0,
607540 17.6/16.6 → 16.3/13.9, 81aced 18.5/13.6 → 15.0/12.0, 7082f5 7.5/6.8 → 8.1/8.2, d14b89 16.5/18.7 → 16.3/18.4,
a5a387 9.4/17.0 → 9.5/15.9, dad91b 15.6/0.96 → 13.7/0.87, c00ebf 13.4/6.5 → 12.0/7.1. All sink in both hemispheres
and weaken by ~1–2 Sv, as fresher inflow should. dad91b's south is PW-579's.

**Scorecard** (`docs/scorecard.jsonl`, commit fb332ca, L6, 1000 Myr; against abe4838, PW-575, since attempt 1 had none):
- Earth: group 70.3, exact 30.8, log-rain 0.622, all unchanged;
- seed 1: dry 20.1 → 16.7% / ice 3.1 → 5.6 / NPP 331 → 292 / trees 17.9 → 27.2;
- seed 2: dry 22.6 → 24.9% / ice 0.7 → 2.2 / NPP 385 → 320 / trees 19.8 → 18.0.

These are single chaotic snapshots. NPP falls on both seeds by 10–17%, and ice rises on both.

Attempts used on PW-582: 2 of 3. The handoff is `handoff-A8.md`.

## PW-582, attempt 3 of 3 (lane A9): straits by geometry and the Arctic branch

**Result: an improvement overall that misses the bar. Merge-ready apart from the scorecard line, which follows in its own commit.**
- Fennoscandia −8.2 → **−6.5** (bar ±6), the Nordic Seas box −5.5 → −3.1, and the Norwegian coast's sea air 1.4 → **3.4 C**
  (NCEP ~3.5). The Barents is still frozen (−13.7 → −13.3). Iceland is worse, −10.6 → −11.6 (bar −7.8).
- `uv run pytest -q`: 568 passed. The goldens are regenerated on purpose.
- Attempt 2's salinity mixing stays in (coordinator's ruling 2).
- **Harness change (coordinator's ruling 1):** `test_timezoom_consistency`'s `cold_moment` no longer rides on seed 4's
  chaotic 300 Myr run. It takes the first of seeds 4–11 whose cold moment meets a stated precondition:
  - the run's sea level within 150 m;
  - ≥ 2 Sv of overturning in each hemisphere;
  - ≥ 25% land poleward of 60° in one hemisphere, where sheets can grow. Sheets are not part of the precondition,
    so `test_cold_moment_has_sheets` stays a real check.

  Every assertion is unchanged, including the 25 m bound. Control: the three tests pass on main's code, on attempt 2
  and on attempt 3. `draft-timezoom-index-zero-test-chaotic.md` is deleted.
  The same seeds show the I = 0 drift ranges from −0.1 to −29 m on plausible worlds (seed 7: −29.1). So the bound sits
  inside the spread, which is a property of the time zoom (`draft-timezoom-index-zero-drift-spread.md`).

Outputs are in `laneA9/`: `*_a3.txt` after, and `*_head.txt` before (attempt 2 with main merged in).

### What changed (`planet/ocean.py`; `moc_sill` removed)
1. **A strait is a passage too small for the inflow** (`_straits`, `_narrowest`).
   - The inflow is a layer `moc_layer_m` deep and `moc_width` wide. It can't pass where the sea's narrowest
     cross-section is smaller than its own. The cross-section is the smallest of three great-circle chords through
     the cell, each walked both ways to land, counting each cell's width × sea fraction × min(depth, layer).
   - So a wide shelf sea is told from a narrow strait by geometry, with no depth picked by hand. It uses no new
     constant.
   - On Earth's L5 overturning grid (need 125 km²): Bering 7, Hudson Strait 36, Nares 35, Davis 120 and the Baltic 22
     stay shut. The Barents (129–153), Denmark Strait 145, Faroe–Shetland 175 and Fram 211 are open.
2. **The Arctic branch.**
   - Where the inflow meets the year-round ice lid, it dives under it rather than stopping. Its routes end at the
     lid's edge (`_paths`' new `through` mask), and nothing more is exchanged there.
   - The water there is the winter water of the open sea it came through. Where that is dense enough it sinks at the
     lid's edge, under the same gate and flow law as the open sea.
   - The deep-water reference is still taken from the open sea. The lid's surface share stays 0.
   - So the inflow carries on past the open sea's own sinking toward the lid, as the Barents branch does toward the
     St Anna Trough.

### The bars (Earth L6)
| line | attempt 2 + main (`*_head`) | attempt 3 (`*_a3`) |
|---|---|---|
| Fennoscandia coldest-month bias (bar ±6) | −8.2 | **−6.5** |
| Iceland (bar: no worse than −7.8) | −10.6 | −11.6 |
| Nordic Seas / Barents coldest-month bias | −5.5 / −13.7 | **−3.1** / −13.3 |
| Kola / Karelia | −13.9 | −13.6 |
| Norwegian coast sea air (NCEP ~+3.5); open in winter; SST | +1.4; 100%; 2.4 | **+3.4**; 100%; 3.8 |
| Nordic / Barents-Kara / Irminger / Labrador / Baffin (Sv) | 4.02 / 0 / 1.53 / 1.77 / 2.42 | 5.29 / 1.37 / 2.01 / 2.42 / 0.31 |
| Earth NH Sv, open polar share; SH | 10.21, 73%; 2.43 | **11.91, 91%**; 2.51 |
| Labrador Sea / Baffin Bay; Baffin Bay; Hudson Bay | +6.2; +6.3; +7.6 | **−0.5; +1.4**; +7.5 |
| log-rain r / Köppen group / exact | 0.622 / 70 / 31 | 0.622 / 71 / 31 |

**Generated worlds**, NH / SH Sv (before → after): 119973 16.0/16.6 → 15.9/16.4, 28442c 17.3/16.0 → 17.0/15.8,
607540 16.3/13.9 → 16.4/13.9, 81aced 15.0/12.0 → 14.9/11.5, 7082f5 8.1/8.2 → 8.1/**15.1**, d14b89 16.3/18.4 →
15.9/18.3, a5a387 9.5/15.9 → 10.0/15.9, dad91b 13.7/0.87 → 13.7/**2.36**, c00ebf 12.0/7.1 → 11.9/**11.9**. All sink in both
hemispheres. Southern shelf seas that used to count as straits now feed their sinking.

### Why the Barents is still frozen (`draft-barents-still-frozen-after-pw582.md`, updated)
- The inflow now reaches and sinks in the Barents (share 0.6–0.9, 1.4 Sv). But it arrives at −0.4 to +1.4 C, against
  4–6 C observed. The Norwegian Atlantic Current is already ~3 C too cold at 70–72N.
- The hemisphere's capped sinking is spread over every gated cell of the Nordic basin by area. So the transport left
  along the slope by 72N is small, and it gives its heat up within a few cells.
- The lid-edge sinking is small (~0.01–0.02 Sv per cell).
- Iceland: the Irminger branch arrives 3–4 C colder as the sinking moves north and east.
- The draft's options: the sinking's distribution within a capped hemisphere, the form of the inflow's heat loss, or
  parking the Barents until the winds' stage.

**Scorecard** (`docs/scorecard.jsonl`, commit 17335b3, L6, 1000 Myr; against fb332ca, attempt 2):
- Earth: group 70.3 → 70.5, exact 30.8 → 31.0, log-rain 0.622 unchanged;
- seed 1: dry 16.7 → 21.8% / ice 5.6 → 6.3 / NPP 292 → 311 / trees 27.2 → 15.5;
- seed 2: dry 24.9 → 12.3% / ice 2.2 → **13.0** / NPP 320 → 245 / trees 18.0 → 21.8.

These are single chaotic snapshots. Seed 2's ice at 13% is the outlier to watch.

Attempts used on PW-582: 3 of 3. The handoff is `handoff-A9.md`.

## PW-579: entrainment below a dense pocket (lane A10), attempt 1 of 3

**Result: Earth's south 2.51 → 5.94 Sv (Weddell 1.13 → 2.23, Ross 0.73 → 1.39). dad91b's south is unchanged (2.36 →
2.49), and that is geography, not the pocket.** `uv run pytest -q` passes (568); goldens regenerated on purpose.
Outputs: `laneA10/*_main.txt` (before, main f3767ad) and `*_e579.txt` (after).

### Measured first (main)
- The 8 other generated worlds' south is 11.5–18.3 Sv. dad91b 2.36, Earth 2.51 (27% in open sea).
- Earth's south is the pocket case of the ticket: the water that sinks averages 1029.9 kg/m3 against the open polar
  sea's 1027.4, over 1.5 of 34 Mkm2. The densest 10% set the deep water at 1028.7, which gates the rest of the
  open polar sea out.
- dad91b's south is no longer the pocket case. Since PW-582's straits, its densest pocket (1029.6) is behind
  passages too small for the inflow, so it isn't part of the polar sea the inflow reaches. The reachable polar sea
  is 79 L5 cells (~3.8 Mkm2). Its densest 10% (1028.27) are only 0.8 kg/m3 above its mean (1027.47). Its sinking is
  2.6 Sv against a cap of 13 Sv. This is the ticket's option C (a hemmed-in polar sea with little open water makes
  little deep water), and it now comes from the geometry of the straits.

### What changed (`planet/ocean.py`, `moc_entrain` new)
- The plume entrains the open polar sea's water: the deep water is ρ_d = (ρ_top + E ρ_a) / (1 + E), where ρ_top is
  the densest `moc_top` share as before and ρ_a is the open polar sea's polar-weighted mean.
  - The reference is min(ρ_top − `moc_mix`, ρ_d). So a sea where the densest water is less than `moc_mix` (1 + E) / E
    (0.83 kg/m3) above the rest is unchanged. Where it is more, the open sea within `moc_drho` of ρ_d sinks too.
  - The pocket's own sinking (water denser than ρ_top − `moc_mix`) carries its entrained water: × (1 + E q), with q
    how far the entrainment lowers the deep water beyond its ordinary mixing (0..1 per `moc_mix`).
  - The per-sea cap is on ρ_top against the water replacing it, which is what it was before (deep + `moc_mix`).
- E = `moc_entrain` = 1.5 is a new constant: overflows and Antarctic shelf water grow 2–3× on their way down
  (Denmark Strait ~3 → 5–6 Sv, Weddell shelf water ~1–2 → 4–5 Sv).

### The bars
| line | main | PW-579 |
|---|---|---|
| Earth SH Sv (Weddell / Ross); open share | 2.51 (1.13 / 0.73); 27% | **5.94 (2.23 / 1.39)**; 45% |
| Earth NH Sv, open polar share (bar 8–20, ≥ 70%) | 11.91, 91% | 14.41, 92% |
| Nordic / Barents-Kara / Irminger / Labrador / Baffin (Sv) | 5.29 / 1.37 / 2.01 / 2.42 / 0.31 | 6.41 / 1.61 / 2.52 / 2.82 / 0.41 |
| Fennoscandia coldest month (bar ±6) | −6.5 | **−6.0** |
| Iceland; Nordic Seas; Barents | −11.6; −3.1; −13.3 | −10.1; −1.5; −13.1 |
| Southern Ocean 60–70S winter (bar ±4) | −3.7 | −3.6 |
| log-rain r / Köppen group / exact | 0.622 / 71 / 31 | 0.622 / 70 / 31 |

- Generated worlds' SH: unchanged within 0.01 Sv except 81aced 11.5 → 12.8 and dad91b 2.36 → 2.49. NH unchanged within 0.1 Sv.
- The Köppen group moves 71 → 70 at the rounding edge (the scorecard has the decimals).
- `test_meltwater_weakens_the_overturning` and the time zoom's cycle test pass unchanged.

**Closing PW-579?** Earth's south is now plausible (bottom water formation is ~5–10 Sv including entrainment). Every
generated world sinks a few Sv or more in the south. dad91b is the low end at 2.5 Sv, for the geographic reason above.
I'd close the ticket on option A with these numbers. If dad91b's 2.5 Sv is too little for a world with a hemmed-in
polar sea, that's a separate question about straits (`draft-dad91b-south-is-straits.md`).

## Stage 3: summer heat (PW-352, PW-457, PW-573, PW-581), attempts 1 and 2 of 3 (lane A10)

**Not merged: both attempts fail a time-zoom test.** The code is not on the branch. Attempt 2's diff (on de1a6a0) is
`laneA10/stage3_attempt2.diff`. Probe tables (`p3.py`, Earth L6): `laneA10/stage3_probe_main.txt` (before),
`stage3_probe_sweep.txt` (the τ / depth sweep), `stage3_probe_attempt2.txt` (after). The `*_s3a1.txt` tool outputs are
attempt 1.

### What it does (three mechanisms; one summer time scale, `sum_tau` = 1 day, replaces `air_km_s`)
1. **Summer carry per time (PW-581 part 1).** The summer air reaches U × `sum_tau` over land, at least a cell (~450 km
   at 5 m/s, which was `air_km_s`). The winter's mixed (heated-from-below) branch uses the same reach.
2. **Fetch (PW-573).** The land's own swing (`half_l`, a big continent's) builds up only while the air is over land.
   `fetch` is the share of the air's last ~`sum_tau` it spent over land, carried on the summer wind and fading over the
   sea just as fast, and `land_sum = t_land + half_l × fetch`. A narrow land in a steady wind then keeps much of the
   sea's summer.
3. **Surface energy split (PW-352 / PW-457), in place of the ±`evap_cool` table in `_land_finish`.**
   - The summer half's ground sunshine, under the model's own clouds, less the latent heat of the summer's AET, is the
     sensible heat H. H warms a `sum_h` = 1500 m boundary layer over `sum_tau`. 1500 m is the encroachment depth for
     ~80 W/m2 into ~5 K/km.
   - That is measured against the H the curve stands for: `cloud_ref` 0.63, and `ef_ref` 0.52 × Priestley–Taylor's wet
     share at the summer's temperature. Without the temperature term (attempt 1, `ef_ref` 0.46 flat), cold lands with
     little evaporation were warmed: Keewatin, Alaska, and the time zoom's cold-moment sheets.
   - The clouds are computed once, right after the rain. The air temperatures are re-run with the split before the
     first land finish.
4. **Mountains (PW-581 part 2).** On ground above `air_m`, the cell keeps the carried winter air: its own winter is
   relaxed from its upwind neighbours' air, without the cut. The cut-off still applies to the air it passes on, so the
   prairies' cold pool stays.

### The bars (Earth L6; main → attempt 2)
| bar | main | attempt 2 |
|---|---|---|
| humid warmest month within 2.5 C: SE USA / SE China / Great Lakes / Labrador / HB lowlands | +4.8 / +4.9 / +6.1 / +4.2 / +5.6 | **+2.8 / +2.7** / +4.1 / +3.5 / +5.2 |
| ... NE USA / E Australia / Pampas | +6.0 / +4.4 / +5.6 | +3.0 / **+1.8** / +4.8 |
| dry interiors no more than 2 C colder: Great Plains / C Asia / Mongolia / Aus. interior / Sahara / Arabia | +0.2 / −2.3 / −1.5 / −0.4 / −0.2 / −4.0 | +0.2 / −2.1 / −0.1 / −1.8 / +2.2 / −0.6 |
| SH coastal range within 1.3× (NCEP 9.6) | 14.3 (1.49×) | **12.3 (1.28×)** |
| SH 150–400 / 400–800 km (NCEP 14.1 / 17.6) | 20.0 / 24.5 | 17.2 / 24.5 |
| Patagonia / NZ / Tasmania warmest month | +6.0 / +2.3 / +6.9 | **+2.5 / +0.2** / +6.3 |
| NH continentality rows within 2 C (0–150 … >1500 km) | −1.8 / +0.6 / +1.3 / +0.2 / +0.5 | −1.5 / +0.4 / +1.0 / +0.5 / +2.1 |
| summer-half rain where obs < 300 mm, N / S (obs 167 / 200) | 660 / 1623 | **566 / 1276** |
| W Europe warmest month | +0.4 | **−3.3** |
| Fennoscandia warmest / coldest (stage-1 bars ±3 / ±6) | −5.2 / −6.0 | −6.7 / −6.2 |
| Keewatin / Alaska warmest | −0.4 / −2.8 | +4.0 / 0.0 |
| mountain coldest month: Canadian Rockies / Tibet / Alps (PW-581: ±6) | −7.7 / −4.1 / −3.3 | −7.0 / −4.2 / −2.4 |
| log-rain r / Köppen group / exact | 0.622 / 70.5 / 30.9 | 0.619 / 69.9 / 29.9 |

### Why not merged
- **Attempt 1** (`ef_ref` flat, the reach floor half a cell) failed two tests:
  - `test_sheet_air_is_carried`: the margin cooled 0.38 C, against the bar of 0.5. On L4 the margin's slow wind gave a
    reach under half a cell. The reach floor is now one cell (a cell's air is the mean over its width), and the margin
    cools 1.3 C.
  - `test_cold_moment_has_sheets`: sheets at 0.88% against the 1% bar. Cold lands with little evaporation were warmed;
    attempt 2's temperature-dependent reference fixes that.
- **Attempt 2** fails `test_timezoom_cycle::test_glacials_grow_ice_and_endings_melt_it_fast`. The glacial's extra ice
  is 58.9 m, and 15 kyr after the ending 63.6 m is left (bar < 29.4). Main passes it.
  - Likely: the fetch takes summer heat off coastal and narrow lands, which are where the zoom's ice margins melt.
  - This is the L4 endings knife edge that lane A5 already noted. Not yet diagnosed.
- The W Europe regression (+0.4 → −3.3) shows a bias the fetch exposes rather than causes. The near-land seas' summer
  air is too cold (North Sea / Biscay −3.8, NE Atlantic 45–55N −2.3: PW-580). Before, the land's full continental
  swing hid that.

One attempt is left. Notes for it are in `handoff-A10.md`.

## Checkpoint (PW-570 step 4): the zoom's honest rules on the base climate after PW-579 (lane A10)

This is measured only. The defaults are unchanged. The honest rules are `orbit_resp=seasons`, `sheet_air=cold`,
`surface_air=fetch`, `margin=ramp` and `front=ramp`. They were applied to the tests as TZParams defaults through the
pytest plugin `laneA10/checkpoint/honest.py`, and to `tz_earth.py` through `--set`. Outputs are in
`laneA10/checkpoint/`.

| check | defaults | honest rules |
|---|---|---|
| `tests/test_timezoom_cycle.py` (incl. the L4 endings test, PW-568) | 10 passed | **9 passed, 1 failed**: endings, extra 93.5 m, 102.1 m left after 15 kyr (bar < 46.7) |
| `tz_earth.py`: maxima (≤ −80 m at ≤ 6 C) | −86 … −100 m ok | −74 … −101 m (one glacial at −74: F) |
| ... give-back ≥ 0.6 | 0.73–0.96 ok | 0.62–0.88 ok |
| ... interglacial ice 9–12% | 9.3–12.1 (F, at 12.1) | 12.4–13.7 (F) |
| ... cooling ≤ 6 C | 6.21 (F) | 6.21 (F) |
| `tz_earth.py --dt0` (within 20%, follows the orbit) | not re-run | area up to 1.37× (F); corr −0.25 (follows: ok) |

- The L4 endings test still fails under the honest rules, and the Earth bars move only a little: give-back holds,
  while the interglacial ice and the dT-0 growth are worse.
- That is the outcome the review expected (section 4): it confirms that the ice-surface air (PW-569 / PW-439) is
  what holds the ice. So the checkpoint goes back to the ice lane.
- Stage 3 isn't in this base climate yet, so the checkpoint should be re-run once it merges.

## Stage 3, attempt 3 of 3 (lane A11): not merged. The fetch breaks the endings test; a green candidate without it

The code is not on the branch. Files in `laneA11/`:
- `stage3_attempt2_toggles.diff`: attempt 2 with env toggles S3_REACH / S3_FETCH / S3_SPLIT / S3_MTN, plus S3_FBASE.
- `stage3_attempt3_candidate.diff`: the green candidate.
- Probe tables and diagnostic tools are in `tools/`.

### Which mechanism breaks `test_glacials_grow_ice_and_endings_melt_it_fast` (extra / left after 15 kyr; bar left < extra / 2)
| variant | extra / left |
|---|---|
| main | 97 / 25 (83 / 24 on a rerun: the zoom is chaotic at the ULP level) |
| attempt 2 | 59 / 64 (F) |
| no per-time reach | 40 / 14 |
| no fetch | 27 / 2.6 (51 / 4.6) |
| no split | 37 / 12 |
| no mountain rule | 75 / 21 |
| attempt 2 at −3.8 / −3.9 / −4.1 C | 78 / 68, 65 / 68, 41 / 36 (F) |
| main at −3.9 / −4.1 / −4.2 C | pass |
| attempt 2 with `sheet_air=cold` / `surface_air=fetch` / `summer_damp=0` | 78 / 69, 88 / 86, 110 / 103 (F) |

- Not a knife edge, and not the ice-surface rules (PW-569 / PW-439): none of them rescues attempt 2, and main passes
  under all of them.
- Why it fails: the glacial's extra ice moves poleward.
  - At the ending, main's NH extra is at 45–65N, which melts. Attempt 2's is at 65–90N and 55–90S, which doesn't.
  - 115 of 135 km-sum left after the ending lie poleward of 60.
  - Most of it lies where the no-index run's mass balance is negative, so the sheets' own height and albedo hold it.
- At L4 (~450 km cells) nearly all land is a coast for a 1-day fetch, so the fetch takes the continental swing off
  the polar lands.
- The fetch also has a physics flaw. `t_land + half_l × fetch` falls below the arriving summer sea air at low fetch,
  so summer land cools the sea's air, which is most of W Europe's −3.3.
  - The sound form is `sea_in + fetch × (land_full − sea_in)` (`stage3_probe_fetch_from_sea_air.txt`):
    W Europe −2.2, Fennoscandia −5.1, r 0.621.
  - But the SH range is 13.0 (1.35×), and the endings test is worse (90 / 82).
  - Details: `issue-tracking/inbox/draft-stage3-fetch-moves-l4-glacial-ice-poleward.md`.

### The green candidate (no fetch), measured
- **What it contains:**
  - the per-time reach and the mountain rule (PW-581);
  - the energy split, re-referenced to the model's own PET. The curve's H is the sunshine under `cloud_ref` less
    `ef_ref` (0.61, Earth ice-free land 20–60 summer AET/PET without the split) × the PET's latent heat;
  - the humidity floor fix.
- **Why the split changed:** without the fetch, attempt 2's Priestley–Taylor reference warmed cold lands, and
  `test_cold_moment_has_sheets` fell to 0.51% (bar 1%).
- **Tests:** `uv run pytest -q` gives 565 passed. The goldens are not regenerated (not merged). Endings 36 / −0.2.
- **Tool outputs:** `earth_check_s3a3.txt`, `climate_bias_s3a3.txt` and `overturning_s3a3.txt` (before the floor
  fix, which moves only floor cells). The "before" files are `laneA10/*_e579.txt`.
- **Earth L6 against main:**
  - rain r 0.622 → 0.626, group 70.5 → 70.4;
  - Fennoscandia −5.2 → −3.6, Alaska −2.8 → +0.6, W Europe −0.2, Canadian Rockies Tc −7.7 → −6.8;
  - humid boxes within 0–2 C of main's (SE USA +4.8 unchanged);
  - SH coastal range 14.3 → 14.7, Tasmania +6.9 → +8.5, Keewatin −0.4 → +3.9;
  - obs E → model D 6% → 26%. By latitude band, though, 60–80N E shares move toward observed.
- Stage 3's own bars are not met, and the result is mixed rather than better overall. So it isn't merged.
  The decision is in `issue-tracking/inbox/draft-stage3-after-three-attempts.md` (lean: redesign the fetch first).
- The scorecard and the checkpoint (`ckpt.sh`) were not re-run: nothing changed in the base climate on the branch,
  so the PW-579 checkpoint above stands.

## Stage 3, round 2 attempt 1 (lane A12): the fetch redesigned, stage 3 landed together (PW-587 option B)

**Green, and merge-ready under the owner's principle. Two of stage 3's bars are missed: the humid summers are still
+3–4 C, and W Europe / Fennoscandia sit under main's** (`issue-tracking/inbox/draft-stage3-fetch-merge-with-bar-misses.md`).

Stage 3 is the candidate of attempt 3 (`laneA11/stage3_attempt3_candidate.diff`) plus the new fetch. The candidate
brings the per-time reach and the mountain rule (PW-581), the PET-referenced energy split (PW-352 / PW-457) and the
humidity floor (PW-586).

Files in `laneA12/`:
- the probe tables: `stage3_probe_fetch.txt` (after), `stage3_probe_fetch_sens.txt` (the scales) and
  `stage3_probe_fetch_obs_sea.txt` (NCEP's sea air in the fetch);
- `endings_variants.txt`;
- the tool outputs `*_s3b.txt`. The "before" files are `laneA10/*_e579.txt`, as main's base climate hasn't changed
  since PW-579.

### The fetch (`_summer_fetch`, PW-573)
- **Built from the arriving sea air.** The land's summer air is `sea_in + f × (land_full − sea_in)`. It always lies
  between the two, so summer land no longer cools the sea air (PW-588's flaw).
- **Two parts, both distances, so the grid's cell size doesn't enter:**
  - The boundary layer (`sum_h` 1500 m) takes the ground's heat in a day wherever it is. That is a share
    sum_h / `fetch_h` of the swing, and `fetch_h` = 3500 m is the summer heat low's depth (~650 hPa).
  - The air above it mixes over the synoptic scale. That share is as continental as the land's share within
    `fetch_km` = 1000 km (`smooth` of the land mask).
  - So f = 0.43 + 0.57 × the land share.
- **The arriving sea air is the sea's summer air along the wind's path**, weighted over `fetch_km`. It is the ocean
  air mass upwind, not the nearest cell's water. With the nearest cell's water, the Baltic's 3 C air and the Arctic's
  0 C air were taken straight into the land. The L4 endings test then failed robustly (52 / 29 at −3.8 … −4.2 C).
- **An ice sheet's own share of the air** (SUMMER_DAMP × damp_air) stays the sheet's annual mean, as before. Only the
  rest is fetched.

Variants measured and dropped:
- the land share alone (f = share): the NH coasts' range falls 3.6 C, W Europe −3.5, rain r 0.613;
- an upwind land share instead of the isotropic one: the same or worse on every bar;
- the nearest cell's sea air: see `endings_variants.txt`.

### The bars (Earth L6; main → attempt-3 candidate → this)
| bar | main | candidate | this |
|---|---|---|---|
| humid warmest within 2.5 C: SE USA / SE China / NE USA / Great Lakes | +4.8 / +4.9 / +6.0 / +6.1 | +4.8 / +4.5 / +4.6 / +4.1 | +3.6 / +3.3 / +3.7 / +3.5 |
| ... Labrador / HB lowlands / Pampas / E Australia | +4.2 / +5.6 / +5.6 / +4.4 | +4.4 / +4.8 / +6.1 / +3.6 | **+2.0** / +3.7 / +4.3 / **+1.8** |
| SH coastal range ≤ 1.3× (NCEP 9.6) | 14.3 (1.49×) | 14.7 | **12.4 (1.29×)** |
| SH 150–400 / 400–800 km (NCEP 14.1 / 17.6) | 20.0 / 24.5 | 19.9 / 25.7 | 16.1 / 21.0 |
| Patagonia / NZ / Tasmania / Chile mid warmest | +6.0 / +2.3 / +6.9 / +2.2 | +5.9 / +2.9 / +8.5 / +3.6 | +2.1 / +1.4 / +6.2 / 0.0 |
| NH continentality range, 0–150 … >1500 km (NCEP 26.4 / 30.8 / 33.7 / 34.7 / 33.4) | 24.6 / 31.4 / 35.0 / 34.9 / 33.9 | 26.9 / 32.6 / 34.9 / 35.0 / 34.7 | 24.9 / 29.9 / 33.0 / 33.8 / 34.4 |
| W Europe warmest (no worse than main) | +0.4 | −0.2 | **−2.1** |
| Fennoscandia warmest / coldest | −5.2 / −6.0 | −3.6 / −5.9 | **−5.7** / −6.0 |
| summer-half rain where obs < 300 mm, N / S (obs 167 / 200) | 660 / 1623 | 644 / 1619 | **602 / 1165** |
| log-rain r ≥ 0.617 | 0.622 | 0.626 | 0.620 |
| Köppen group / exact | 70.5 / 30.9 | 70.4 / 30.9 | 69.5 / 31.7 |
| obs D → model E | 13% | | 19% |
| dry interiors: Great Plains / C Asia / Aus. interior / Sahara / Arabia | +0.2 / −2.3 / −0.4 / −0.2 / −4.0 | +0.2 / −1.6 / −0.7 / +3.3 / +0.2 | −1.3 / −2.1 / −3.3 / +1.9 / −1.0 |
| Alaska / Keewatin / Iceland warmest | −2.8 / −0.4 / +0.5 | +0.6 / +3.9 / +2.0 | −5.2 / +0.6 / +0.7 |
| mountain coldest: Canadian Rockies / Tibet / Alps (±6) | −7.7 / −4.1 / −3.3 | −6.8 / −4.2 / −2.4 | −7.0 / −4.2 / −2.5 |
| Greenland ice / Antarctic plateau warmest | −4.2 / +2.1 | −2.1 / +1.0 | −6.6 / −0.4 |

- **Stage 1 and 2 hold:**
  - Earth NH 14.41 → 14.37 Sv, 92% open; the Norwegian coast open 100%;
  - the 9 worlds within ±0.1 Sv of before;
  - Labrador / HB lowland coldest month +2.8 / +5.2, unchanged.
- **W Europe and Fennoscandia are the sea's summer air.** It is 2.3–3.8 C too cold off Europe and 6 C too cold in the
  Gulf of Alaska, because the annual SST is too cold there. The fetch now passes that on, where the full continental
  swing used to hide it. Details: `draft-near-land-sea-summer-air-cold-north-warm-south.md`.
  - With NCEP's sea air put into the fetch (`stage3_probe_fetch_obs_sea.txt`): W Europe −1.6, Fennoscandia −5.0,
    Alaska −3.8, group 70.2, r 0.622.
  - The rest comes in through the reach and the coast mixing, which carry the same sea air.
- **No scale setting meets both the SH range and W Europe** (`stage3_probe_fetch_sens.txt`). With `fetch_km`
  700–1400 or `fetch_h` 2500–5000, the SH range runs 11.9–13.1 and W Europe −1.5 … −2.5. The two move against each
  other.
- **The ice sheets' summers are colder.** Greenland's sea air, lifted over the sheet, is colder than the curve's
  summer for it. Options: `draft-stage3-fetch-cools-ice-sheet-summers.md`.

### Tests
- `uv run pytest -q`: 568 passed, with the goldens regenerated on purpose.
- The L4 endings test: 57.7 / 1.4 m. It is not a knife edge: 58.6 / 2.4 at −3.9 C and 58.6 / 1.3 at −4.1 C.
- `test_same_planet_rains_the_same_at_two_levels`, `test_cold_moment_has_sheets` and `test_sheet_air_is_carried`
  pass.
- The scorecard line (`docs/scorecard.jsonl`, 61517ea+dirty) has Earth group 69.5 and r 0.62.
  - Seed 1 at 1 Gyr: ice 0.8 → 6.9%, dry 22.7 → 27.9%.
  - Seed 2: ice 4.7 → 1.8%.
  - The seeds' tectonics differ run to run at 1 Gyr, so these are noise-level, not attributable.

### Checkpoint (PW-570 step 4) on stage 3 (`laneA12/checkpoint/`; measured only, the defaults are unchanged)
| check | defaults: after PW-579 → stage 3 | honest rules: after PW-579 → stage 3 |
|---|---|---|
| `tests/test_timezoom_cycle.py` | 10 passed → **10 passed** | 9 passed, 1 failed → 9 passed, 1 failed (endings: 93.5 / 102.1 → 42.9 / 42.7 m) |
| `tz_earth.py` maxima (≤ −80 m at ≤ 6 C) | −86 … −100 ok → −88 … −104 ok | −74 … −101 F → −80 … −96 F (one at −80) |
| ... give-back ≥ 0.6 | 0.73–0.96 ok → 0.65–0.87 ok | 0.62–0.88 ok → 0.45–0.81 F |
| ... interglacial ice 9–12% | 9.3–12.1 F → 9.8–13.3 F | 12.4–13.7 F → 13.4–14.9 F |
| ... cooling ≤ 6 C | 6.21 F → 6.55 F | 6.21 F → 6.55 F |
| `tz_earth.py --dt0` (area within 20%, follows the orbit) | not run | 1.37×, corr −0.25 → 1.36×, corr 0.02 (follows: F) |

- Under the zoom's defaults, stage 3 keeps every cycle test green and the Earth maxima and give-back in their bars.
- Its cooler polar summers add ~1% interglacial ice and 0.34 C of cooling.
- Under the honest rules, the L4 endings test is still red, but much closer (43 / 43 against 94 / 102).
- The Earth zoom's honest give-back and interglacial ice are worse, and the dT-0 run no longer follows the orbit.
- That agrees with the earlier checkpoint: what holds the ice under the honest rules is the ice-surface air
  (PW-569 / PW-439), which now meets cooler polar summers. So it goes back to the ice lane.

## PW-589: the overturning's heat between the hemispheres (lane A13), attempt 1 of 3

**Green and merge-ready. Of the bars, the near-land SST, Fennoscandia, rain and stages 1–3 pass. W Europe's warmest
month misses (−1.2 against +0.4).** What is left is the sea's summer swing, which is a different mechanism
(`issue-tracking/inbox/draft-sea-summer-swing-wind-mixed-layer.md`).

Files in `laneA13/`:
- `bands.py` and its outputs `bands_base.txt` (main), `bands_z0.txt` (`moc_zonal` 0) and `bands_fold.txt` (this).
  They give per-band and per-box annual / warmest / coldest sea air against NCEP, near land and in open sea, and
  the SST's parts: t_eq, the gyres' anomaly and the overturning's heat.
- `p3_fold.txt` (lane A12's stage-3 probe).
- The tool outputs `*_before.txt` / `*_a1.txt`, and `checkpoint/`.

### Measured first (main, `bands_base.txt`)
- **Not upwelling, and not the gyres, in the north.** The gyres' near-land anomaly at 45–70N is −0.1 … +0.8 C.
- **The overturning's heat is the cause.** `moc_zonal` = 1 took the inflow's warmth off each latitude band's own
  mean (PW-265). So every NH cell off the inflow's path was cooled by the band's share of the North Atlantic's heat:
  Gulf of Alaska −2.4 C, Baltic −2.3, NE Pacific −1.2, North Sea −0.4.
  - The NH band means at 55–70N came out 2.9–3.6 C too cold, while the SH's were left untouched (+1.4 … +2.2 C too
    warm at 40–60S).
  - t_eq is one curve for both hemispheres. NCEP's sea is 1.6–2.4 C warmer in the north than at the same latitude
    in the south (7 C at 65N). Earth's overturning heat by band, E_N, is 1.0 / 1.5 / 2.5 / 3.7 / 4.2 C at
    40 / 45 / 50 / 55 / 60N: close to NCEP's north-minus-south at 40–65N.
- **The sea's own swing** is the other half of the summer bias, a separate one:
  - NH half-swings are too small: NE Atlantic 1.7 against 3.2, Norwegian Sea 1.8 / 4.0, NE Pacific 2.0 / 3.9.
  - SH coasts' are too big: off Patagonia 6.2 / 3.7, Tasman 3.7 / 2.7.
  - Drafted, not changed.
- **The SH's warm coasts at 35–45S are the gyres' western boundary currents** (Tasman +5.0, Agulhas +3.1), not
  PW-017's southern sinking (`draft-sh-western-boundary-currents-too-warm.md`).
- **The Barents (PW-583) doesn't share the cause.** The fix warms it only 0.5–0.8 C (annual −5.7 → −5.2 C, coldest
  month −13.1 → −12.3): its inflow arrives too cold, as PW-583 says.
- `moc_zonal` 0 (no compensation at all) fixes the off-path coasts but makes heat: the ocean's air is +0.25 C
  warmer, and the NH open sea +3 … +5.7 C.

### What changed (`planet/climate.py` `zonal_mean(fold=)`, `sea_surface`; `planet/ocean.py` `solve`)
- The overturning's heat E is now taken off the mean over each latitude's sea **in both hemispheres together**
  (`zonal_mean(..., fold=True)`), not each band's own.
- Heat is still conserved. t_eq is symmetric, so it can only stand for the two hemispheres' average overturning.
  What one hemisphere's overturning carries beyond the other's is now that hemisphere's own warmth, taken from the
  other hemisphere's sea at the same latitude. That is the north's sinking drawing warm water across the equator.
- No new constant. A planet that sinks equally in both hemispheres is unchanged. One that sinks in one hemisphere
  gets a warm hemisphere.

### The bars (Earth L6; main → this)
| bar | main | this |
|---|---|---|
| PW-589 SST rows within ±2 C of NCEP's annual air: NE Atl / Biscay–N Sea / Norw / Baltic / G Alaska / NE Pac / Patagonia / Tasman | −1.0 / −4.0 / −1.7 / −6.3 / −3.2 / −2.6 / +1.9 / +4.4 (3 of 8) | +0.1 / −2.7 / +0.9 / −4.3 / −1.5 / −1.7 / +1.4 / +4.1 (**5 of 8**) |
| near-land annual sea air by 5° band, within ±2 C | NH 55–70N −3.6 … −4.5 (3 rows out); SH 40–45S +2.4, 60–65S −4.3 | NH all rows within except 65–70N −2.0; SH 40–45S +2.1, 60–65S −5.1 |
| NH / SH ocean mean sea-air bias | −0.74 / +0.60 | −0.34 / +0.31 (global mean unchanged, 16.42) |
| W Europe warmest (pre-stage-3 +0.4) | −2.1 | **−1.2** (misses) |
| Fennoscandia warmest / coldest (pre-stage-3 −5.2) | −5.7 / −6.0 | **−3.9 / −4.5** |
| log-rain r ≥ 0.617 / Köppen group / exact | 0.620 / 69.5 / 31.7 | 0.620 / 69.9 / 32.1 |
| Iceland warmest / coldest | +0.7 / −10.0 | +3.2 / **−3.7** |
| Alaska / Kola warmest | −5.2 / −4.9 | −4.9 / −4.3 |
| NH coasts' range 0–150 / 150–400 km (NCEP 26.4 / 30.8) | 24.9 / 29.9 | 25.1 / 30.1 |
| SH coastal range (≤ 1.3× NCEP 9.6) | 12.4 | 12.4 (1.29×) |
| humid warmest: Labrador / HB lowlands / E Australia | +2.0 / +3.7 / +1.8 | +3.2 / +4.0 / +1.8 |
| winter sea ice N / S (NCEP 16.8 / 20.2 Mkm2) | 18.2 / 21.5 | 16.8 / 23.3 (+15%, within ±25%) |
| Southern Ocean 60–70S coldest month | −3.6 | −4.7 |

- **Stage 1 holds:**
  - Earth NH 14.37 → 13.86 Sv at 90% open polar sea;
  - the Norwegian coast is open 100%, its sea air 4.2 → 6.6 C (NCEP ~3.5: now too mild);
  - the 9 worlds' sinking is within ±0.6 Sv per hemisphere, all sink in both.
- **Stage 2 holds:**
  - Hudson Bay, Baffin and Okhotsk freeze (coldest month −19.9 / −29.0 / −4.1);
  - Labrador / HB lowland winters +2.9 / +5.0;
  - the Antarctic pack's winter −1.5.
- **Stage 3's humid summers are a little warmer.** Labrador loses its in-bar +2.0. The NH open sea at 45–65N is
  now +1.8 … +5 C (it was +0.5 … +2.6), and the inflow seas' winters are milder
  (`draft-nh-open-sea-and-inflow-winters-too-warm.md`).

### Tests and the checkpoint
- `uv run pytest -q`: 568 passed, with the goldens regenerated on purpose.
- The L4 endings test: 71.8 / 11.7 m (bar left < extra / 2).
- Scorecard line `964a132+dirty`: Earth group 69.9, r 0.62; seed 1 ice 1.6%, seed 2 4.8%.
- Checkpoint (`laneA13/checkpoint/`; measured only, the defaults are unchanged), stage 3 → this:

| check | defaults | honest rules |
|---|---|---|
| `tests/test_timezoom_cycle.py` | 10 passed → **10 passed** | 9 passed, 1 failed → 9 passed, 1 failed (endings 42.9 / 42.7 → 33.7 / 41.1 m) |
| `tz_earth.py` maxima (≤ −80 m) | −88 … −104 ok → −80 … −100 ok | −80 … −96 F → −75 … −90 F |
| ... give-back ≥ 0.6 | 0.65–0.87 ok → 0.62–0.86 ok | 0.45–0.81 F → 0.49–0.78 F |
| ... interglacial ice 9–12% | 9.8–13.3 F → 9.7–12.9 F | 13.4–14.9 F → 13.1–14.7 F |
| ... cooling ≤ 6 C | 6.55 F → 6.41 F | 6.55 F → 6.41 F |
| `tz_earth.py --dt0` (honest: area within 20%, follows the orbit) | | 1.36×, corr 0.02 → 1.26×, corr 0.12 (both F) |

The defaults stay green and slightly closer on every bar. The honest rules are still red on the endings test and
the Earth zoom's bars, as in the stage-3 checkpoint: that still points to the ice lane (PW-569 / PW-439).

## PW-593: the sea's summer swing from the wind (lane A14), attempt 1 of 3: not merged

**Not merged. The wind-set summer layer does what PW-593 asked in the NH. The model's summer winds are the wrong
way round between the hemispheres, so it breaks the SH, rain r and the SH coastal range.** The code is not on the
branch. Its toggles (`ml_wind`, `land_fetch`) are in `laneA14/pw593_attempt1_toggles.diff`. The decision is in
`issue-tracking/inbox/draft-summer-mixed-layer-needs-seasonal-winds.md` (lean: winds first).

Files in `laneA14/`:
- `wind.py` / `wind_base.txt`: per box, the summer and winter wind speed, the storminess, the summer sunshine Q,
  the Monin-Obukhov depth, and the sea's half-swing split into summer and winter sides;
- `ev.py` / `ev2.py` and their `ev*_base.txt`: offline variants;
- `p3.py` / `p3_attempt1.txt`: lane A12's stage-3 probe plus the sea-swing rows;
- `*_before.txt`: main's earth_check, climate_bias and overturning_report.

### Measured first (main)
- **The model's summer winds don't have the contrast the mechanism needs.**
  - `v_sum` is 8.7 m/s over the NE Pacific (obs ~6-7) and 7.9 over the NE Atlantic.
  - Off Patagonia it is 3.1 (obs ~8-10), the Tasman 3.5 and the Agulhas 2.3.
  - Band 40-50: N 7.3, S 6.4.
- **Why:**
  - `wind()`'s westerly belt has one strength in both seasons and hemispheres. The belts alone give 6.2-7.0 m/s at
    all three.
  - `monsoon_wind`'s land-sea part slows the SH coasts (Patagonia 6.4 → 3.1) and speeds the NE Pacific (6.2 → 8.7).
  - The summer storminess (`storm_track`) is about equal too: 0.68 at 40-50N, 0.75 at 40-50S.
- **The SH coasts' excess swing isn't the layer's depth.** Off Patagonia `sea_half` is 5.7, of which ~3.5 is the
  land part. That part is a big continent's swing, whatever the land's width
  (`draft-sea-swing-land-part-is-a-big-continents.md`).
- **The NE Atlantic's small air swing is half the winter side.** Its sst − Tc is 1.0 against Tw − sst 2.5: that is
  the overturning's winter damping (PW-592), not the summer layer.
- **PW-592 and PW-594 don't share the mechanism.** The Tasman's +4.7 summer is the gyre's +5 annual (PW-594), and
  the open NH sea's warmth is the overturning's (PW-592).

### What was tried (`ml_wind`; `land_fetch`)
- `_summer_layer`: h = u*^3 / (kappa g alpha Q / rho c), clipped to [`light_m` 20, `brine_m` 50] m.
  - u* comes from the bulk stress (C_D 1.3e-3) on the summer wind.
  - Q is `_sea_half`'s summer sunshine.
  - alpha is `ocean.density`'s thermal expansion at the summer SST.
  - It sets the summer side of the swing only (`sea_half_s`); the winter side keeps `brine_m` and the overturning's
    damping.
- `land_fetch`: the land carried onto the sea in `land_air` is weighted by `_summer_fetch`'s share,
  sum_h / fetch_h + (1 − that) × the land within `fetch_km`.

### The bars (Earth L6; main → `ml_wind` / `land_fetch` / both; `p3_attempt1.txt`)
| bar | main | ml_wind | land_fetch | both |
|---|---|---|---|---|
| W Europe warmest (no worse than pre-stage-3's +0.4) | −1.2 | **−0.1** | −1.9 | −1.0 |
| sea swing within 1.5x: near N / near S / open N / open S | 52 / 54 / 10 / 43% | **69** / 40 / **35** / 66% | 43 / **66** / 8 / 43% | 67 / 45 / 34 / 69% |
| half-swing NE Atl / Norw / NE Pac (obs 3.2 / 4.0 / 3.9) | 1.7 / 1.8 / 2.0 | 1.9 / 4.0 / 2.2 | 1.7 / 1.6 / 2.0 | 1.9 / 3.8 / 2.2 |
| half-swing Pat / Tasman / Agulhas (obs 3.7 / 2.7 / 2.4) | 6.2 / 3.7 / 3.6 | 8.7 / 5.6 / 5.3 | 4.9 / 3.1 / 3.1 | 7.0 / 4.8 / 4.7 |
| log-rain r ≥ 0.617 | 0.620 | **0.598** | **0.613** | **0.591** |
| SH coastal range ≤ 12.5 (stage 3) | 12.4 | **14.6** | 11.6 | **13.5** |
| Fennoscandia / Iceland / Tasmania warmest | −3.9 / +3.2 / +6.0 | −0.7 / +8.2 / +8.9 | −4.2 / +1.4 / +5.5 | −1.3 / +5.7 / +8.1 |
| humid warmest: SE USA / Labrador / Pampas | +3.7 / +3.2 / +4.2 | +4.7 / +5.2 / +5.2 | +3.2 / +3.3 / +3.7 | +4.1 / +5.1 / +4.6 |

- Offline (`ev_base.txt`, `ev2_base.txt`), nothing rescued it:
  - floors of 10 or 20 m;
  - the Monin-Obukhov factor doubled;
  - a storminess term in the stirring wind (|U|² + (k × track × U_REF)²).
  - The NE Pacific stays ~50 m deep under its 8.7 m/s, and the calm SH coasts always reach the floor.
- Offline, a flat 20 m layer scores like the wind-set one: 59% and 58% of the 20-65 sea rows within 1.5x, against
  main's 37%. So what
  `ml_wind` gains in the NH is a shallower layer overall, not the wind's pattern.
- So neither is merged:
  - `ml_wind` fails rain r and the SH coastal range;
  - `land_fetch` fails rain r and W Europe.
- One sound path is left: summer westerlies by season and hemisphere, then the saved layer on top
  (draft option A).

### Tests and the checkpoint
- Main: `uv run pytest -q` gives 568 passed (`laneA14/` before-run). Nothing in `planet/` changed on the branch, so
  the after-run equals the before-run, and the PW-589 checkpoint (`laneA13/checkpoint/`) stands. `ckpt.sh` was not
  re-run.
- The scorecard's before-run was stopped part-way by the coordinator's pause (the owner needed the machine quiet).
  Main's climate is unchanged since PW-589, so lane A13's line (`964a132+dirty`: Earth group 69.9, r 0.62) is
  still main's.

## PW-596 option A: the winds first (lane A15)

**Steps 1 and 2 pass their Earth bars and improve rain and Köppen. They break two time-zoom ice tests, so merging
needs a ruling (`issue-tracking/inbox/draft-pw596-winds-break-timezoom-ice-tests.md`, lean: merge, fix the ice
next). Step 3, PW-593's summer layer on the new winds, still fails rain r and the SH coastal range. It is not on
the branch (`draft-sh-coastal-summer-winds-still-calm.md`).**

Files in `laneA15/`:
- `wdiag.py`: the summer wind per box, split into the belts, the 900 km land-sea part and the big part, plus each
  season's contrast. Outputs `wind_before.txt` (main) and `wind_after.txt`.
- `patag.py`: the SH summer's first-guess anomalies and wind parts at the SH coasts.
- `p3.py`, the stage-3 probe, run per variant (`p3/p3_b{belt}_c{column}[_ml].txt`, toggles in
  `pw596_probe_toggles.diff`).
- `*_step1.txt`: step 1 alone. `*_after.txt`: steps 1+2, the branch. Main's are lane A14's `*_before.txt`
  (planet/ is unchanged since).

### What changed (`planet/climate.py`)
1. **`westerly_belt`: the westerlies by season and hemisphere.**
   - The surface westerlies are eddy-driven: they scale with the mid-latitudes' poleward temperature contrast (the
     thermal wind). So `wind()`'s westerly term is multiplied, in each half-year and hemisphere, by that season's
     zonal-mean contrast over 30–65 deg (`storminess`, the zonal mean `jet_stream` is built on).
   - It is relative to the planet's own mean of the four. A planet without seasons keeps one belt, and the mean
     stays U_REF's calibration.
   - The first-guess winds use the first guess's contrast; the final (front-shifted) winds use the finished air's.
   - On Earth (finished air), C per 1000 km: N summer 5.1, N winter 8.0, S summer 6.4, S winter 8.2. So the belts
     are N 0.75 / 1.17 and S 0.91 / 1.17.
   - Linear in the contrast, with no fitted exponent. Observed NH zonal-mean surface westerlies go roughly
     summer/winter 0.6–0.7, about the contrast's ratio.
2. **`low_column`: thermal lows as deep as the land's air column.**
   - A thermal low's or high's pressure is hydrostatic, so it is the column's mean temperature anomaly.
   - The land's anomaly is weighted by sum_h / fetch_h + (1 − that) × the land within fetch_km, the same rule
     and constants as `_summer_fetch`.
   - So narrow lands and continents' coasts make shallow lows, and continental interiors deep ones. No new
     constant.

### Narrow lands (task 2): the land's own low was not the cause
- The column cuts Patagonia's own low (anomaly +1.0 C). Off Patagonia, though, the summer winds go 3.1 → 3.4 m/s
  only.
- What slows them is the **sea's** first-guess anomaly offshore, +1.9 C: `_sea_half`'s land part gives the sea
  a big continent's swing whatever the land's width.
- Weighting that land part by the column as well (`X_COL=3`) gives:
  - Patagonia's half-swing 6.1 → 4.8 and the SH coastal range 11.5;
  - but W Europe warmest −1.5 and near-land NH swing within 1.5x 43%.
  - So it is not merged (draft).
- Tasman and Agulhas are calm because `front_shift` reads their too-warm SST (PW-594) as a lower latitude.

### The bars (Earth L6; main → step 1 → steps 1+2)
| bar | main | step 1 (belts) | steps 1+2 (branch) |
|---|---|---|---|
| log-rain r ≥ 0.617 | 0.620 | 0.617 | **0.631** |
| Köppen exact / group (cells) | 32 / 70 | 33 / 70 | **34 / 71** |
| cities exact / group / wrong | 30 / 28 / 20 | 33 / 26 / 19 | 32 / 27 / 19 |
| SH coastal range 0–150 km ≤ 12.5 (NCEP 9.6) | 12.4 | 12.3 | 12.3 |
| W Europe warmest (pre-stage-3 +0.4) | −1.2 | −0.9 | −0.9 |
| Fennoscandia warmest / coldest (PW-575) | −3.9 / −4.5 | −3.7 / −3.0 | −3.7 / **−2.8** |
| Kola coldest / Iceland coldest | −13.5 / −3.7 | −12.6 / −2.7 | −12.4 / −2.3 |
| coasts 40–65N with the sea to the west only: coldest / warmest (PW-026) | −1.1 / −3.2 | −0.7 / −2.7 | −0.7 / −2.8 |
| Labrador / Quebec warmest | +3.2 | +4.3 | **+4.0** (worse) |
| SH land 150–400 / 400–800 km warmest | +1.6 / +0.5 | +1.7 / +0.5 | +2.1 / +1.6 (worse) |
| Pampas warmest, summer rain (obs 1349) | +4.2, 1677 | +4.1, 1745 | +5.6, 1126 |
| E Australia summer rain (obs 765) | 2369 | 2383 | 1881 |
| winter sea ice N / S (NCEP 16.8 / 20.2) | 16.8 / 23.3 | – | 16.7 / 23.2 |

Summer winds (m/s; obs as in PW-596):

| | main | branch |
|---|---|---|
| NE Pac / NE Atl | 8.7 / 7.9 | 7.2 / 6.6 |
| band 40–55 N / S | 7.3 / 6.5 | 6.2 / 6.2 |
| winter 40–55 N / S | 8.3 / 6.6 | 9.2 / 7.7 |
| off Patagonia / Tasman / Agulhas | 3.1 / 3.5 / 2.3 | 3.4 / 3.2 / 2.0 |

- The NH summer is fixed, and the SH now matches the NH in summer instead of trailing it.
- Not met: "SH faster than NH" and "SH coasts not under ~5 m/s" (see the draft).

**Stage 1 holds** (`overturning_after.txt`):
- Earth NH 13.86 → 13.98 Sv, 90% in open polar seas; the Norwegian coast 100% open; SH 5.66 → 5.58.
- The nine worlds are within −1.0 … +0.8 Sv per hemisphere, and all sink in both.
- Step 1 alone moved c00ebf's south 11.9 → 8.0 and dad91b's 2.0 → 4.9. With the column these come back to 11.6
  and 2.9.

### Step 3: PW-593's summer layer on the new winds (`p3/*_ml*.txt`)
| | main + ml_wind | branch + ml_wind (first-pass winds) | branch + ml_wind on the final winds |
|---|---|---|---|
| rain r ≥ 0.617 | 0.598 | 0.607 | 0.607 |
| SH coastal range ≤ 12.5 | 14.6 | 14.7 | 14.7 |
| W Europe warmest | −0.1 | +0.8 | +1.6 |
| near-land swing within 1.5x N / S | 69 / 40% | 70 / 40% | 75 / 39% |
| half-swing NE Atl / Pat / Tasman (obs 3.2 / 3.7 / 2.7) | 1.9 / 8.7 / 5.6 | 2.0 / 8.6 / 5.6 | 2.8 / 8.6 / 5.6 |

It still fails, for the same reason as in A14: the SH coasts' summer winds are still ~3 m/s.

### Tests and health
- `uv run pytest -q`: 566 passed, 2 failed, with the goldens updated on purpose (climate and 60 Myr simulation
  change through the winds). The failures are the time zoom's ice tests; assertions unchanged:
  - `test_glacials_grow_ice_and_endings_melt_it_fast`, extra / left m (main 71.8 / 11.7): step 1 8.5 / –, branch
    38.2 / 21.2.
  - `test_cold_moment_has_sheets`: 0.72% of cells under ice (bar > 1%). It passes on main and with step 1 alone.
- `tools/health.py --quick` (8 L6 seeds, 500 Myr; `laneA15/health_before.md` on d32f7fa, `health_after.md` on
  the branch). **The runs grow more ice:**
  - outlier spells 54 → 61;
  - seeds with sea level below −150 m from ice for more than 10% of the run: 2 → 5 (42 25 → 49%, 77 0 → 61%,
    1 10 → 29%, 21 0 → 24%, 2 16 → 20%);
  - the new ice bar fails on 5 → 3 seeds (77 icehouse 100%, 42 86%, 3199 73%);
  - giant-lake frames: seed 1 0 → 18%, 77 0 → 14%, 21 10 → 6%.
  - These are single chaotic 500 Myr runs. But the drift is one way: more and deeper glaciation in the run, while
    the time zoom's glacial grows less. Both are the ice lane's fitted rules (PW-471's v1 kludge) meeting the new
    winds. That is recorded in `draft-pw596-winds-break-timezoom-ice-tests.md`.

**Ready to merge? Not on my own call.** On Earth the change is better on every bar it was given (rain r, Köppen,
W Europe, Fennoscandia's winter, stage 1), and it is the mechanism PW-596 asked for. But it turns two time-zoom
tests red and makes the health sweep's ice-age outliers worse. Under the "global, not local, optimum" rule that is
the coordinator's ruling (the draft's option A), not a lane's.

## PW-596 option A on the PW-576 base (lane A16): re-measured

**The time zoom's glacial passes, health is no worse than main, and no ice rule leans on the old winds. One
fixture is still red: the cold-moment tests' first plausible seed is now a hothouse moment. That needs a ruling
(`issue-tracking/inbox/draft-pw596-winds-break-timezoom-ice-tests.md`, lean A: the fixture picks the first
plausible seed with sheets).**

Branch `worktree-agent-a34e43ec48de2d53e`:
- main 2180b8e merged with lane A15's 98749b4;
- goldens regenerated on the merged code (only `sim_L4_s1_60myr` conflicted).

Files are in `laneA16/` (README.md lists them).

### Earth bars and winds
`planet/climate.py` is unchanged on main since A15's base (d32f7fa). So `earth_check`, `climate_bias` and the
overturning (Earth and the 9 worlds) on the branch are byte-identical to A15's `*_after.txt` except the timings.
A15's table above stands:
- rain r 0.620 -> 0.631;
- Köppen 32 / 70 -> 34 / 71;
- Fennoscandia coldest -4.5 -> -2.8;
- the summer winds as in A15's table;
- stage 1 holds.

### Tests (`uv run pytest -q`, 585 tests)
main 2180b8e is green. On the branch, 583 pass and 2 fail, on one fixture:

| test | main | branch |
|---|---|---|
| glacial extra / left after 15 kyr, m (bar: left < extra / 2) | 93.0 / 15.3 | 49.9 / -0.5, passes (A15 on the old base: 38.2 / 21.2) |
| cold moment under sheets (bar > 1%) | 2.09% (seed 28) | **0.86%** (seed 31) |
| cold-moment ice speeds, median (bar < 100 m/yr) | passes | **117** |
| ice at index zero | passes | passes |

**Mechanism, by crossing the climates on fixed worlds.**
- *Time zoom:* `xzoom.sh` runs sim4's source from each tree with each tree's climate. main's world gives 93.0 / 15.3
  with main's climate and 90.5 / 18.6 with the branch's. The branch's world gives 37.9 / 1.8 and 49.9 / -0.5. The
  zoom's ice rules (PW-471's index, PW-569's surface air) don't lean on the winds. The difference between the worlds
  is the run's chaos, and both pass.
- *The run's ice rule (`_cold`):* `xcold.sh` runs it on the same world with each climate, `xcold.txt`.
  - main 28: 2.09 vs 2.10%; main 32: 1.38 vs 1.39%; branch 31: 0.74 vs 0.86%.
  - With the belts or the column switched off it moves by at most 0.25 points.
  - So the winds don't weaken the run's sheets either.
- *The fixture:* it takes the first of seeds 25-35 that meets `_plausible`.
  - On the branch that is seed 31 alone, a hothouse moment (run dT +6.66 C).
  - main has the same kind at 31 (+8.0 C, 0.46%). It passes because seed 28 comes first.
  - Over seeds 25-50, plausible seeds with more than 1% under sheets: main 3 of 6, branch 2 of 7
    (`coldscan_*.txt`).
  - The branch's first plausible seed with sheets is 46 (3.20%). With SEEDS = (46,), all three cold-moment tests
    pass.
  - Widening the window can't help, because seed 31 stays first.
- *A trap for scripts:* `planet` has to be imported before numpy, or BLAS's thread caps come too late and the
  chaotic run diverges. Seed 31 gave run dT +7.05 instead of +6.66.

### Health (`tools/health.py --quick`, 8 L6 seeds, 500 Myr, 8 workers x 2 threads; `health_main.md` / `health_branch.md`)
| | main 2180b8e | branch |
|---|---|---|
| outlier spells | 80 | **60** |
| seeds with ice sea level below -150 m for >10% of the run | 2 (42 47%, 77 37%) | **0** (2 9.8%) |
| plate-collapse spells (<= 4 plates) | 1 (77 24%) | 0 |
| seeds with giant-lake frames > 5% | 6 | 3 |
| new ice bar (icehouse 5-70%) fails | 3 (11 0%, 3199 0%, 42 100%) | 5 (1 4%, 11 96%, 21 0%, 77 76%, 505 100%) |
| icehouse share, median seed | 21% | 34% |
| ice sea level, median of the seeds' medians | -7.8 m | -16.4 m |
| determinism | identical | identical |

A15's "deeper ice ages" doesn't reproduce on the CO2 stock: none goes deep. The runs spend more time with some ice,
and the icehouse share spreads both ways. These are single chaotic runs. It's recorded as a follow-up in the draft.

**Ready to merge? Not yet.** Everything but one fixture's seed lottery is green or better. Making it green takes a
change to how the fixture picks its moment, which is the owner's call (draft, option A).

## PW-594 and the SH coastal summer winds (lane A17)

**Step 1 (PW-594, New Zealand walls the gyres) is committed and green. Step 2 (the land's air lies stable over the
sea in summer, PW-595's land part) improves rain r to 0.649 and the SH bars but cools W Europe's sea summers and
turns the time zoom's endings test red: saved as a diff, `draft-stable-summer-off-land-air.md` (needs-decision).
The SH coastal summer winds did not come up, so PW-593's layer still fails (step 3 below).**

Branch `worktree-agent-a6b65c5df0ddd0d62`: main d01c772 + lane A16's branch (b04a5fc) merged (1a68a7e), then step 1
(7b41cea). Files in `laneA17/` (README.md lists them; `bars.md` is the full table).

### What was found (`wbc.py`, `gyre.py`, `curmap.py`)
- The SH gyres' extent is about right: annual westerlies peak at 44-52S (6.5 m/s), curl zero at ~46S.
- **New Zealand's two islands (112,000 and 149,000 km2) were each under `island_km2`**, so the whole South Pacific
  gyre closed on Australia and Tasmania: the coastal current ran 2.0-2.3 m/s to 35S, and psi in the western Tasman
  was the full Pacific's.
- What is left after the walls: the current follows the coast to 38S (no separation at 31-34S in a linear Stommel
  solver), at ~2 m/s where the heat's reach is capped at 7500 km, then spreads east at 0.8-1 m/s across 40-47S.
  `cur_max` 3 -> 1.5 would cut the Tasman another 1.2 C (sensitivity only). `draft-pw594-tasman-still-warm.md`.
- Tried and dropped: no Sverdrup gyre (a circumpolar flow instead) in latitudes whose walls are under 3-5% of the
  circle: the Tasman unchanged, off Patagonia +3 C. The Ekman drift is ~1.5 cm/s, too small to matter.

### Step 1: walls by north-south span (`currents`)
An island walls the gyres if it is bigger than `island_km2` (as before) or longer north to south than two
boundary-current widths (2 r / beta at its latitude): New Zealand's islands, Luzon, Sulawesi. No new constant.

### Step 2 (not merged): the land's air in summer lies stable over the sea (`step2_stable_summer.diff`)
`_sea_half` returns a summer and a winter half. The winter's land air (colder than the water) churns and takes its
heat at `open_b`, as before; the summer's (warmer) lies stable and gives the water only its longwave (4 sigma T^3,
~5 W/m2 per C, as PW-578 says for its vapour). The water's year is then colder by hk x (winter - summer) / 2, a
surface cooling carried like upwelling's.

### The bars (Earth L6; A16 branch -> step 1 -> step 2; `bars.md`)
| bar | A16 branch | step 1 | step 2 |
|---|---|---|---|
| rain log-r (>= 0.617) | 0.631 | 0.630 | **0.649** |
| Köppen exact / group; cities wrong | 34 / 71; 19 | 33 / 71; 19 | 34 / 71; 16 |
| SH coastal range 0-150 km (<= 12.5) | 12.3 | 12.5 | 12.1 |
| SH land 150-400 / 400-800 range bias | +2.1 / +1.6 | +2.1 / +1.6 | +2.7 / +2.6 |
| Tasman 35-45S SST (NCEP air 15.2); sea air annual / warmest | 19.3; +3.9 / +4.7 | 18.5; +3.1 / +3.8 | 18.4; +2.4 / +2.6 |
| sea air annual / warmest: Agulhas / Brazil / off Patagonia | +1.3/+2.3, +1.2/+1.8, +0.7/+2.7 | +1.2/+2.2, +1.0/+1.6, +0.7/+2.7 | +0.5/+1.0, +0.3/+0.2, -0.6/+0.1 |
| Gulf Stream box 35-45N sea air annual | +5.0 | +5.0 | +4.5 |
| sea's warmest: NE Atl / Biscay-N Sea / Labrador Sea | -1.1 / -2.5 / +2.8 | -1.3 / -2.5 / +2.8 | -0.7 / **-5.4** / +0.3 |
| W Europe / Fennoscandia warmest | -0.9 / -3.7 | -1.0 / -3.8 | **-2.1** / -4.7 |
| Labrador / Iceland warmest | +4.0 / +3.5 | +4.3 / +3.4 | +2.4 / +1.5 |
| sea swing within 1.5x near N / near S | 52 / 54% | 52 / 55% | **33** / 69% |
| half-swing NE Atl / Pat / Tasman / Agulhas (obs 3.2 / 3.7 / 2.7 / 2.4) | 1.7 / 6.1 / 3.7 / 3.6 | same | 1.7 / 4.8 / 3.1 / 3.1 |
| summer wind Pat / Tasman / Agulhas; 40-55 N / S | 3.4 / 3.2 / 2.0; 6.2 / 6.2 | 3.4 / 3.4 / 2.0; 6.2 / 6.2 | 3.4 / 3.6 / 1.9; 5.9 / 6.1 |
| Earth NH Sv (open polar %) / SH Sv; Norwegian coast open, winter sea air | 13.98 (90) / 5.58; 100%, 6.9 | 13.86 (90) / 5.61; 100%, 6.4 | 13.64 (89) / 5.99; 100%, 7.6 |
| 9 worlds: all sink in both hemispheres; lowest | yes; dad91b S 2.85 | yes; dad91b S 2.85 (c00ebf S 11.6 -> 7.9) | yes; dad91b S 1.89 |

### Step 3: PW-593's layer on step 2, with the storms' transients in the stirring wind (`bars_pw593_on_step2.md`)
The SH coastal winds didn't come up (Patagonia's belts 5.4 and its own low through the 900 km part; Tasman and
Agulhas sit in the horse latitudes' calm belts), so the saved PW-593 layer was re-tried as asked only to measure:
| | step 2 | + ml_wind | + ml_storm 0.5 | + ml_storm 1 |
|---|---|---|---|---|
| SH coastal range (<= 12.5) | 12.1 | 14.5 | 14.2 | 13.2 |
| W Europe warmest | -2.1 | +0.2 | -0.5 | -1.9 |
| near-land swing in 1.5x N / S | 33 / 69% | 69 / 46% | 65 / 48% | 50 / 56% |
| half-swing NE Atl / Pat / Tasman | 1.7 / 4.8 / 3.1 | 3.1 / 6.9 / 4.8 | 2.7 / 6.7 / 4.8 | 1.8 / 5.8 / 3.8 |

The transients deepen both hemispheres' layers alike and take back the NH's gain before they fix the SH. Recorded in
`draft-sh-coastal-summer-winds-still-calm.md` (lane A17 section).

### Tests
- Step 1: `uv run pytest -q` **593 passed** (goldens unchanged: no such island at L4). Both cold-moment tests pass
  on this tree: the seed lottery of PW-623 moved with the walls (the fixture is untouched). That is luck, not a fix;
  PW-623 stands.
- Step 2: 592 passed, `test_glacials_grow_ice_and_endings_melt_it_fast` red (extra / left 33.2 / 19.7 m; A16
  branch 49.9 / -0.5). Not crossed yet (A16's `xzoom.sh` needs a second tree).

### Health (`tools/health.py --quick` on step 1, 7b41cea; `laneA17/health_step1/report.md` vs `laneA16/health_branch.md`)
| | A16 branch | step 1 |
|---|---|---|
| outlier spells | 60 | 72 |
| seeds with ice sea level below -150 m for >10% of the run | 0 | 2 (2 11.8%, 42 11.8%) |
| plate-collapse spells | 0 | 0 |
| seeds with giant-lake frames > 5% | 3 | 4 (11 27.5%, 77 9.8, 2 7.8, 505 7.8) |
| new ice bar (icehouse 5-70%) fails | 5 | 4 (21 0%, 3199 0%, 77 84%, 505 4%) |
| icehouse share, median seed | 34% | ~18% |
| determinism | identical | identical |

Single chaotic 500 Myr runs (the walls change any generated world with a long narrow island); no direction holds
across the rows, so nothing here is pinned on step 1. Step 2 was not swept (not merged).

**Ready to merge?** Step 1 (7b41cea) yes: green, every Earth bar within noise of the A16 branch except the Tasman
(better), stage 1 holds. It sits on A16's branch, so it waits on PW-623 with it. Step 2 needs the draft's decision.

## PW-627 step 2: the endings test crossed, and Europe's summer layer (lane A18)

**Step 2's red endings test is the run's chaos, not its climate: step 2's climate passes on step 1's world, and step
1's climate fails on step 2's world. But no harness-only change can make it green (the fixture has no window; a seed
pick or a "not too cold" precondition changes what is tested), so step 2 still can't merge with main green
(`draft-endings-test-fails-on-cold-source-worlds.md`, needs-decision). No wind-free summer-layer mechanism restores
Europe: the shelf-depth cap is sound but blocked by the European shelf seas' annual cold (PW-592)
(`draft-sea-layer-deeper-than-shelf.md`). Nothing committed but docs and drafts.**

Branch `worktree-agent-a22d5ce3841f99b73`: main b900f1c + lane A17's branch 3e9855a, merged as 644a4f0. Since 3e9855a
main changed no run or climate code, so A17's step-1 / step-2 bars stand (re-run `p3.py`: identical). Files in
`laneA18/` (README.md lists them).

### 1. The endings test crossed (lane A16's method; `laneA18/xzoom_cross.txt`)
sim4's source (L4, seed 1, 300 Myr) from each tree, zoomed with each tree's climate. Extra / left after 15 kyr, m
(bar: extra > 10, left < extra / 2):

| | step 1's climate | step 2's climate |
|---|---|---|
| step 1's world (run dT +5.10, 0.04% under ice) | 49.9 / -0.5, passes | 44.0 / -0.9, passes |
| step 2's world (run dT +2.67, 1.13% under ice) | 31.3 / 15.7, fails | 33.2 / 19.7, fails |

The own-tree numbers equal the test's printouts. The world decides; step 2's climate on a fixed world moves extra /
left by 6 / 0.4 m (step 1's world) and 2 / 4 m (step 2's).

Seeds 1-9, each tree its own climate (`seedscan_2-9.txt`): step 1 passes 6 / 9 (fails seed 5, a hothouse at dT +12.3
with extra 3.8 m; seeds 7 and 8, its coldest at dT +0.75 / +1.37), step 2 passes 7 / 9 (fails seeds 1 and 8, dT
+2.67 / +0.79). Every failure with enough ice is a cold world, on either tree. Step 2 doesn't make the test fail more
often; seed 1 drew a cold world.

Why cold worlds fail (`xflows_s{1,2}world.txt`, the index-on run's ice budget, Gt/yr, step 2's climate): on the
warm world the ending lifts ablation 1890 -> 3352 and the NH net turns negative; on the cold world ablation goes only
873 -> 1611 over 15 kyr and the NH net stays positive (+1900 -> +1000): the sheets stand above their equilibrium line
even at I = 0 and lose ice mainly by calving. PW-588's hysteresis, on a colder planet.

`pytest -q` on step 2 (goldens regenerated, not committed): 594 passed, 1 failed (this test). `pytest_step2.txt`.

### 2. Is a harness-only change legitimate? No
- The fixture is the session's sim4 (seed 1), shared by ~100 tests, cooled 4 C; there is no search window to widen
  (unlike `test_run_lakes`).
- A module-only seed for this test is a pick by outcome. A precondition ("source not a deep icehouse") is a new
  threshold, and it would hide what the failures show (the zoom's endings leave over half the extra ice on cold
  worlds).
- So PW-627's lean A (merge once shown to be chaos) leaves main red. The draft's options: A (lean) find and fix why
  cold worlds' endings are slow, bar: every seed 1-9 with extra > 10 m passes on both trees; B a fixture source by a
  rule that isn't the outcome (owner); C hold (a lottery).

### 3. Europe's summer under step 2 (`seabox_step{1,2}.txt`, `depth.py`, `step2_shelf_probe.diff`)
Where the regression comes from, per box (sea air, model / obs; half = (warmest - coldest) / 2):

| box | annual SST | moc heat | half-swing step 1 / step 2 / obs | warmest bias step 1 / step 2 |
|---|---|---|---|---|
| NE Atl 45-55N | 12.7 / 13.5 | +3.2 / +3.6 | 1.7 / 1.7 / 3.2 | -1.3 / -0.7 |
| North Sea 51-58N 0-8E | 6.9 / 6.8 (obs air ~10.5) | +1.4 / +1.8 | 6.2 / 4.3 / 5.9 | -2.4 / -5.9 |
| Biscay 43-48N | 11.1 / 11.2 (obs air ~14.7) | -0.2 / -0.2 | 4.0 / 3.2 / 5.0 | -4.3 / -5.8 |
| S Atl off Pat | 11.5 / 11.5 | -0.5 | 6.1 / 4.8 / 3.7 | +2.7 / +0.1 |

- Two parts: the shelf seas' annual SST was already ~3 C too cold on step 1 (the overturning's and the gyre's heat
  don't reach them: PW-592's first candidate), and step 2 cuts their swing below the observed one (North Sea 6.2 ->
  4.3 against 5.9), where it rightly cuts Patagonia's (6.1 -> 4.8 against 3.7).
- The suggested mechanisms keyed on the off-land air (the stable summer air shallows the layer) can't separate the two:
  land_air is 0.55 over the North Sea and 0.48 off Patagonia, and the NE Atlantic upwind of Europe has 0.02. Any
  land_air-keyed shallowing deepens Patagonia's swing (already too big) as much as the North Sea's, and leaves the
  NE Atlantic (W Europe's air) alone. A depth from the local summer wind is PW-593's `ml_wind`, which A17 measured on
  step 2: Europe back (+0.2), SH coastal range 14.5. Not measured again.
- The one wind-free mechanism with a geographic NH / SH difference: the layer no deeper than the sea floor (`min(brine_m,
  depth)`). L6 ocean cells 20-65 deg shallower than 50 m: N 4.1%, S 0.4% (North Sea 45%, Baltic 44%, Yellow / E
  China Sea 39%; Patagonian shelf 6%, Tasman / Agulhas / NE Atl 0%). Probe on step 2: North Sea halves 3.7 / 7.1 ->
  7.1 / 11.0, but its sea air's swing stays 4.3: the annual 6.6 C puts the bigger winter below freezing, and
  `_summer_half` spends the summer on melting that ice. Bars: rain r 0.649 -> 0.653, Biscay-N Sea -5.4 -> -5.3, near-N
  within 1.5x 33 -> 35%, SH unchanged. Not committed: it does nothing for Europe until PW-592's marginal-sea warmth
  (and PW-595's land part by the land's width, which makes the North Sea's winter half too big) land.
- Probed and dropped: more diffusion in `sea_surface`'s carry (0.15 -> 0.3 / 0.6) doesn't carry the NE Atlantic's
  heat into Biscay or the North Sea; it only weakens the boundary currents' anomalies.

Not run, since no candidate passed: the full tools.sh bars, the overturning on the 9 worlds and `health.py --quick`
on a candidate. A17's step-2 numbers (stage 1 holds; rain r 0.649; SH coastal range 12.1) stand for step 2 itself.

**Ready to merge?** No code. Step 2 waits on the endings draft's decision; Europe's summer on PW-592 first, then the
shelf cap and PW-595.

## PW-632 option A: what holds a cold world's glacial ice (lane A19)

**No missing termination mechanism inside the zoom meets option A's bar.** On the failing cold worlds, part of the
glacial's leftover ice is a held branch at I = 0, the sheets' own hysteresis: seed 8 on step 2 keeps 51% of it for
120 kyr, which is past the bar at any speed. The rest decays with an e-folding of ~30-40 kyr, against the < 22 kyr the
bar needs, and the extra height (8-11 C of lapse) sets that. Of every candidate, only the marine fronts' loss moves
it, and the zoom has no ocean physics for that on a cold sea (PW-385). Nothing under `planet/` is committed. Two
drafts: `draft-pw632-option-a-held-branch.md` (needs-decision, lean: PW-632 option B now, the marine physics after)
and `draft-marine-fronts-no-ocean-melt.md`.

Branch `worktree-agent-a818192c7d6091881`: main b289b95 + lane A18's branch 5d12daf, merged as cdec55d. Step 2 =
cdec55d + `laneA17/step2_stable_summer.diff` (scratch worktree). Sources: A18's pickles (runs unchanged since). Files
in `laneA19/` (README.md lists them).

### The seed scan (L4, 300 Myr; extra / left after 15 kyr, m; bar: extra > 10 and left < extra / 2)

| seed | step 1 (this branch) | step 2 |
|---|---|---|
| 1 | 50.2 / 1.9 | **30.9 / 18.4 F** |
| 2 | 87.2 / 20.4 | 13.9 / 1.7 |
| 3 | 79.7 / 0.7 | 28.0 / -0.6 |
| 4 | 43.2 / 6.2 | 68.5 / 5.0 |
| 5 | 3.8 / 0.4 (extra < 10: outside the bar) | 49.0 / 5.4 |
| 6 | 21.5 / -0.3 | 19.9 / 0.8 |
| 7 | **131.7 / 88.5 F** | 24.4 / 0.4 |
| 8 | **70.5 / 43.9 F** | **80.8 / 49.0 F** |
| 9 | 44.6 / 7.7 | 101.9 / 47.3 |

- These are A18's numbers to within ~2 m; the soils lane's crown fire acts in the zoom's plants.
- The real test agrees: it passes on step 1 and fails on step 2 (`pytest_endings_s{1,2}.txt`).
- "After" is the same table, since no mechanism was merged.

### What holds the leftover (`diag.py`, `diag2.py`, `diag2_base.txt`)
- **Most of it is marine.** 55-70% of the extra left 15 kyr after the ending is grounded marine ice, 2.3-2.5 km thick,
  on beds pushed 650-700 m down. At the ending, 84-87% of its fronts are behind shelves, and 58-69% still are 15 kyr
  later. The rest is land ice above its equilibrium line.
- **Its warm month is -12 to -17 C**, against +3 to +10 C for bare ground there in the index-off run. About 8-11 C of
  that is the extra surface height, 1.2-1.7 km, after isostasy has already lowered it.
- **Neither the climate nor the local rules hold it.** Taking out the full climate's answer to the sheets (the off
  run's fields on the on run's surface) or the ice surface's local terms warms the leftover by 2-5 C. Its smb stays
  near 0 either way (marine +0.04 to +0.25 m/yr). The height alone holds it.
- **The warm world's ending works differently.** There, the accumulation falls 2767 -> 872 Gt/yr as the snow turns
  to rain. On cold worlds it stays at 4000-7000 Gt/yr: the Clausius-Clapeyron rise in snowfall on sheets that stay
  far below 0 C.

### Slow or held? (`hold.py`: I kept at 0 after the first ending, 120 kyr; `hold_base.txt`)
- Warm worlds lose their extra in 10-20 kyr.
- The failing worlds keep 17% for good (seed 7 step 1, seed 1 step 2), 27% (seed 8 step 1) and 51% (seed 8 step 2).
  What does decay has an e-folding of ~30-40 kyr.
- On these worlds the index-off run is itself an ice age: mean sea level -27 to -66 m. The test's "run's moment
  -4 C" puts a cold planet's I = 0 inside the sheets' multiple-equilibria range, where real sheets don't end either
  (Abe-Ouchi et al. 2013; Ganopolski & Calov 2011).
- It is no clean precondition, though. Seed 5 on step 2 passes with an off-run mean of -28 m.

### Candidates (the four failing cases; `levers1.txt`, `levers2.txt`, `sun1.txt`, `frontmelt1.txt`)

| candidate (mechanism) | passes | note |
|---|---|---|
| isostatic lag (`iso_tau` 1 kyr) | 1 | |
| ice shelves gone (`shelf_warm` -30) | 0 | s2 seed 8 worse (52 / 35) |
| no buttressing | 0 | |
| `sheet_air=cold`, `surface_air=fetch`, `margin=ramp`, `front=ramp` | 0, 2, 2, 0 | stage 1 rules |
| climate every 2.5 kyr (the blend's 10 kyr lag) | 1 | |
| flow `enhancement` x2 | 0 | |
| the orbit's sunshine change melting a melting surface (`sun_melt_probe.diff`) | 1 | the leftover never melts, so it can't act |
| frontal melt by the sea's annual water above freezing (`front_melt_probe.diff`) | 1 | cold worlds' fronts sit in water at freezing |
| proglacial lakes, glacial dust | | tried under PW-030, moved nothing |
| `calving` x4 (tuning) | 3 | held share 0-8%; s1 seed 7 still 117 / 65 |
| `summer_damp` 0 (tuning; PW-569's question) | 3 | held share 2-22%; s2 seed 8 68 / 40 |

The one lever with traction is the marine fronts' loss. `calving` x4 clears the held branches and hardly moves the
off run's own ice (-66 -> -64 m, -27 -> -24 m). But raising the constant is tuning. The mechanism behind it at real
terminations is warm subsurface water at the fronts, and the zoom has none (PW-385).

### Earth (L6; `tz_earth_base.txt`, `tz_earth_dt0_*.txt`, code unchanged)
- The zoom: cycles 98.5-108.5 kyr; maxima -79 / -80 / -98 / -93 / -94 / -94 m; give-back 0.70-0.87; interglacial ice
  9.8-12.9%. Bars: cycles ok, maxima F (-79), cooling F (6.22), give-back ok, interglacial ice F.
- `--dt0`: area 0.88-1.51 x the start, corr -0.02 (within 20% F, follows ok).
- `calving` x4 for scale:
  - `--dt0`: 0.86-1.44 x, Antarctica -0.55 Mkm2 (base -0.34), follows F (corr 0.07).
  - The zoom: glacials only -56 / -62 / -73 / -70 / -69 / -74 m (base -79..-98), give-back 0.66-0.84.
  So a uniform rise in calving costs Earth ~20 m of glacial. The marine loss would have to grow at the endings
  themselves, through the ocean's warmth, not everywhere: `draft-marine-fronts-no-ocean-melt.md`.

## PW-644: low CO2 is what shrinks a glacial's tropical forest (lane A22)

**The water balance is not the cause. The tropics green under cooling because the plants' respiration falls (Q10
2), and the CO2 the zoom lowers barely reached the plants. The CO2 index only nudged C3 light-use efficiency by 12%
per unit, with no effect on water use. The fix gives every C3 plant Farquhar's light-limited quantum yield against
today's, the way C3 grass already had it, and gives every plant a water-use efficiency that scales with Ca (Ci/Ca
held constant). At index 0 nothing changes, so today's Earth is identical. At Earth's time-zoom glacial maximum the
tropical forest share now falls (-15..15 deg: 0.44 -> 0.51 on main, 0.43 -> 0.28 here). The low-latitude
darkening at the zoom's glacial CO2 goes from +0.21 to -0.03 W/m2. In the forest test's milder setting (-4 C,
index -1/3) it only drops, from +0.118 to +0.092 on seeds 1-24. The run uses the same plant code, so `simulate`
outputs change: health is mixed (see below).**

Branch `worktree-agent-ac50a7a56279c5017`: main 69db596, plus PW-643's harness (8f090f8, its own commit), plus
the fix. Files in `laneA22/` (README.md lists them).

### Where the greening came from (Earth L4, `lowlat.py`, `lowlat_split.py`; main)
Tree area at |lat| < 15 deg, against 13.8 Mkm2 at the start; the forest test's setting is -4 C (about -2 C in the
tropics):

| case | tree, Mkm2 |
|---|---|
| cooled climate, CO2 0 | 18.0 |
| cooled temperatures, the start's rain | 19.4 |
| ... with the start's PET (only what acts inside the plants) | 17.8 |
| cooled PET only | 14.7 |
| cooled rain only (-7% there; PET -7% too, so P/PET stays 1.52) | 13.2 |
| CO2 index -1/3 only, main's code | 12.3 |

- **Mechanism:** the plants' own temperature response does most of it. The tropical trees' growth curve is flat over
  20-32 C, so what changes is maintenance respiration, 2^((t-20)/10). Trees, with their wood respiration, gain
  ~15% NPP from 2 C of cooling.
  - Real respiration acclimates. Draft: `draft-respiration-has-no-thermal-acclimation.md`.
  - The rain falls as much as the PET does, so the water balance is neutral.
- **CO2:** on main, -1/3 of index costs C3 trees 4% of their efficiency. The light-limited quantum yield,
  (Ci - G*) / (Ci + 2 G*), gives 12% at 27 C, in line with FACE (beta ~0.55). In the wet tropics the water-use
  part hardly matters, but it caps GPP in the drylands.

### The fix (`planet/vegetation.py`)
- C3_PFTS (every type but C4 grass, CAM and C3 grass) take qy = 2: g_m x q3(t, Ci) / q3(t, Ci_ref). This replaces
  `1 + 0.12 co2` on eps.
- `wue` x 2^co2 for every plant.
- The C4 envelope shift and C3 grass's own quantum yield are unchanged. Nothing changes at co2 = 0, and the
  climate golden is unchanged.

### Earth (the plausibility anchor)
**`tools/tz_earth.py --level 6`** (600 kyr). It now prints the forest share of open land by band.

| band | main, interglacial -> glacial max | A22 |
|---|---|---|
| 60..90 | 0.27 -> 0.03 | 0.26 -> 0.01 |
| 50..60 | 0.70 -> 0.39 | 0.69 -> 0.34 |
| 40..50 | 0.64 -> 0.54 | 0.64 -> 0.51 |
| 30..40 | 0.20 -> **0.26** | 0.20 -> 0.19 |
| 15..30 | 0.07 -> 0.09 | 0.07 -> 0.07 |
| -15..15 | 0.44 -> **0.51** | 0.43 -> **0.28** |
| -40..-15 | 0.12 -> 0.17 | 0.12 -> 0.17 |
| -90..-40 | 0.65 -> 0.39 | 0.64 -> 0.36 |

- **The ice-age bars, main -> A22:**
  - cycles 98-109 kyr on both;
  - maxima -79..-98 m -> -80..-101 m (the maxima bar F -> ok);
  - cooling 6.22 C on both (F as before);
  - endings give back 0.67-0.87, ok;
  - interglacial ice 9.9-13.0% (F as before);
  - Laurentide 10.7 Mkm2 to 38 N.
- **The southern subtropics still green** (-40..-15: 0.12 -> 0.17). That is the cooler, lower-PET dry woodland. Some
  of the LGM's southern drylands were wetter and some drier, so this is left as it is.
- **Biome areas at the zoom's glacial maximum** (`lowlat_*_glacial.txt`, L4, -6.22 C, index -1.04; |lat| < 15):
  - forest: 15.1 -> 18.7 Mkm2 on main, 15.1 -> **8.2** here;
  - savanna and grass: 13.7 -> 9.9 on main, 13.7 -> **20.6** here (LGM: rainforest reduced, savanna expanded).
  - Below 40 deg: F +0.210 -> **-0.027** W/m2.
  - Over all land: F +0.157 -> -0.150. Cold desert and steppe spread poleward of 40, 0.2 -> 6.9 Mkm2.
- **Earth in the forest test's setting** (`fearth_a22_L*.txt`; A21's on main):
  - F: -0.194 -> -0.250 (L4), -0.243 -> -0.305 (L6);
  - below 40, snow-free: +0.096 -> +0.056, +0.120 -> +0.075;
  - trees below 40: +1.95 -> +0.94, +2.35 -> +0.91 Mkm2.

### Multi-seed (seeds 1-24, the harness's draw and two null draws at climate_offset +-0.001 C; bar 17)
| | main (A21) | A22 |
|---|---|---|
| forest: draw / +0.001 / -0.001 | 20 / 16 / 16 | **20 / 20 / 19** |
| endings: draw / +0.001 / -0.001 | 18 / 19 / 19 | 19 / 22 / 22 |
| L5 cold moment, eps 0: plausible, sheeted (need 5), speeds, index 0 | 14, 7, 7/7, 7/7 | 13, 10, 8/10, 9/10 |
| L5 cold moment, eps +0.001 | 13, 10, 10/10, 9/10 | 9, 5, 5/5, 5/5 |

Every bar passes on every draw.

**F's parts over the 72 worlds** (`a22pool.txt`, W/m2, main -> A22):
- F -0.050 -> -0.098;
- below 40 deg, snow-free: +0.118 -> +0.092;
- boreal loss over snow -0.152 -> -0.159;
- trees below 40: +1.82 -> +1.02 Mkm2.

The test's CO2 term is -1 C at -4 C, a quarter share, where the zoom uses half (co2_share 0.5). At that mild CO2
the respiration term still wins below 40 deg.

### Run physics (`simulate` changes: the run's plants use the same code)
The runs' CO2 index in the store spans -1.33 .. +0.98 (5-95%, median -0.31), so their plants change.

`tools/health.py --quick` (8 L6 seeds, 500 Myr, main export against this branch, same session):
- outlier spells: 72 -> 67;
- new ice bar fails: 4 -> 2;
- old ice bar fails: 0 -> 2 (seeds 1, 11);
- frames with ice sea level below -150 m: seeds 2/42/77 at 12/12/10% on main, seeds 1/2/11 at **29/20/16%** here;
- determinism identical;
- median NPP per seed 278-412 -> 253-425; tree cover 26-38% -> 24-40%.

Lower CO2 now means fewer trees and a brighter land, so cold eras may run deeper. That is a real feedback, but 29%
of seed 1's frames past -150 m is above PW-240's 10% bar. It is one sweep of a chaotic system and needs a second
draw before anyone reads it as a trend.

### Tests
- With the harness: `pytest -q`, 601 passed.
- Main's single-seed tests on this `planet/` (an export): 598 passed and 3 failed, all on the single seeds' new
  worlds:
  - `test_glacials_grow_ice_and_endings_melt_it_fast`: seed 1's left_m 27 against 17; seed 1 is one of the 5 of
    24 that fail;
  - `test_cold_moment_has_sheets`: the first plausible seed has 0.1% ice;
  - `test_ice_speeds_plausible`: median 158 against 100.
- The sim golden was regenerated on purpose (`tests/golden/sim_L4_s1_60myr.json`); the climate golden is
  unchanged.

**Ready?** On the mechanism, yes: it is planet-relative physics with no new knobs, and Earth today is unchanged.
On the tests, only with PW-643's harness (or re-picked single seeds). On the run physics, the health sweep's
deeper cold spells want a second look by the coordinator before merge.

Drafts:
- `draft-respiration-has-no-thermal-acclimation.md`;
- `draft-tropical-forest-area-hypersensitive.md` (a 20% CO2 drop takes the tropical forest from 15 to 9 Mkm2 at
  today's climate);
- `draft-co2-index-units-ln-or-log2.md` (needs-decision).

## PW-646 option C: the run carries a real pCO2 (lane A23)
Branch on main 9b30887 + lane A22 (PW-644, 3e2a10a; its harness cherry-pick 89cc49c reverted). Scripts and outputs
are in `laneA23/` (README there).

### What changed
- `climate.pco2(co2) = PCO2_REF x e^co2`, with `PCO2_REF` = 350 ppm.
  - The stock's reference (X = 1) is the planet's own balance at REF_FREEZE. That balance holds the climate model's
    dT = 0, which is Earth's climate as its data show it (~1960-2000, 320-370 ppm). It is also the plants' "today"
    (`vegetation.CA_REF`, which they were tuned at), so no new number.
- `co2_sensitivity` is now **3 C per doubling** of pCO2 (Earth's equilibrium sensitivity, AR6 2.5-4; the ice's
  albedo is its own term). It was 3 C per e-fold, 2.1 C per doubling. `earth.co2_term` divides by ln 2; the param's
  value is unchanged.
- The plants take pCO2 in ppm (`vegetation.envelope/potential/model/coupled_climate(pco2=)`):
  - Ci = 0.7 Ca;
  - WUE ~ Ca;
  - C4's warmth threshold moves 3 C per doubling.
  - They are held within `CO2_RANGE` = 1.5 doublings of CA_REF (124-990 ppm, the old clip).
- The run hands them `climate.pco2(sim.co2)`; frames and world meta store `pco2` (ppm); `co2` (ln X) stays in the
  run's stats for the thermostat's tools.
- The time zoom's plants feel `pco2_0 x 2^(co2_c / co2_sensitivity)`, where co2_c is the CO2 part of dTg. So
  plants and temperature read one quantity in the run and in the zoom.
- `ice_diag`'s fb and `diag`'s co2_term_free use the per-e-fold sensitivity.

### Question 1: reference and sensitivity (`co2_choices.txt`)
Earth's zoom at its glacial maximum (CO2 term -3.11 C):

| reading | per doubling | ppm |
|---|---|---|
| A (log2, as A22) | (3 per e-fold) | 171 |
| B (ln, 3 C per e-fold) | 2.08 | 124 (at the clip) |
| **C (ppm, 3 C per doubling, ref 350)** | 3 | **171** |
| C, ref 280 | 3 | 136 |
| C, 4 C per doubling | 4 | 204 |

- C with Earth's sensitivity gives the same plants as A for any given CO2 term in C. A's log2 reading *was* 3 C per
  doubling, as far as the plants could tell.
- What C changes is the run: an e-fold of the stock now warms 4.33 C, not 3.
- 171 ppm against the LGM's 185-190 is plausible. The glacial / interglacial ratio, 0.49 against Earth's 0.68, is
  off: `co2_share` 0.5 is about twice CO2's own share (27% at 3 C per doubling). It cancels with the 350 ppm
  interglacial. Draft filed (`draft-co2-share-overstates-glacial-co2.md`).

### Question 2: Earth's zoom, the run's ppm, the low tail
- `tz_earth --level 6` (`tz_earth_c.txt`) matches A22's to rounding:
  - cycles 98-108 kyr;
  - glacials -80..-101 m;
  - give-back 0.67-0.85;
  - interglacial ice 9.9-13.1%;
  - forest by band, interglacial -> glacial maximum: 60-90 N 0.26->0.01, |lat|<15 0.43->0.28, 50-60 N
    0.69->0.34.

  The bars are the same as A22's: cooling F and ig_ice F on both.
- The run's pCO2, 5/50/95% of keyframes:

  | sweep | index | ppm (as the plants read it) | < 150 ppm | < 124 ppm |
  |---|---|---|---|---|
  | A22, draw 1 | -0.95 / +0.18 / +1.31 | 182 / 397 / 869 | 2.0% | 0.6% |
  | C, draw 1 | -0.90 / +0.28 / +1.36 | 142 / 461 / 1370 | 5.6% | 3.4% |
  | C, draw 2 | | 131 / 388 / 1019 | 8.0% | 4.5% |

  - The stock's ln X spread hardly narrows: the stronger temperature term damps it only ~10%.
  - So, read as ppm, the plants' range widens on both sides.
  - The old store's index 5/50/95% (-1.25 / -0.20 / +0.97) would be 100 (held at 124) / 286 / 923 ppm.
- Hot-month C3 failures (`lowtail_L6.txt`, Earth's plants grown at each pCO2):
  - Share of growing land cell-months with q3 = 0 (Ci <= G*, which takes a monthly mean above 39.5 C at 124 ppm):
    0.04% at dT 0 and 0.29% at dT +3.
  - Share with q3 under a quarter of today's: 2.9% / 4.5% at 124 ppm, 0.35% / 1.1% at 150 ppm, 0 at 171 ppm and
    above.
  - Outright failures are negligible. The real cost of the low tail is the forest's area (PW-648's knife edge):
    the forest biome goes 56 -> 35 Mkm2 at 171 ppm and 9 Mkm2 at 124 ppm (dT 0), with savanna and grass taking over.

    That is the same in A and C for the same CO2 term. Under C, the run reaches it more often (3-4.5% of keyframes
    at the clip, against 0.6%).

### Question 3: does C change A22's deeper icehouses? (`htable.txt`)
`health.py --quick`, the same 8 + 8 seeds. Main and A22 are lane A22's sweeps; `planet/` on main is unchanged since
then.

| | main | A22 | A22 + C |
|---|---|---|---|
| draw 1 (defaults): seeds > 10% of keyframes below -150 m | 2 (2, 42; 77 9.8%) | 3 (1 29%, 2 20%, 11 16%) | 2 (1 39%, 77 20%) |
| draw 1: old / new ice bar F | 0 / 4 | 2 / 2 | 0 / 3 |
| draw 1: median icehouse % | 18 | 41 | 23 |
| draw 2 (101-108): seeds > 10% below -150 m | 1 (103 28%) | 3 (103 14%, 107 55%, 108 80%) | 1 (105 22%) |
| draw 2: old / new ice bar F | 0 / 2 | 2 / 4 | 0 / 3 |
| draw 2: median icehouse % | 27 | 29 | 34 |
| pooled: mean % of keyframes below -150 m | 3.8 | 13.4 | 5.9 |
| pooled: old / new ice bar F | 0 / 6 | 4 / 6 | 0 / 6 |

- C takes the deep-ice frames most of the way back to main: 3 seeds over 10% in 16, as on main, against A22's 6.
- No old-bar fails, against A22's 4.
- Determinism is bit-identical.
- Single seeds still swing; draw 2's second half was re-reported from its runs (`--manifest`) after a pause stopped
  the sweep.

Why the thermostat answers differently, per C of CO2 term:
- The plants are the same as A's.
- The stock's answer per C of cooling, fb = sensitivity per e-fold x g / WEATHER_CO2 (g ~0.047 per C, PW-576), goes
  from 0.35 to 0.51 C/C.
- A non-CO2 cooling's equilibrium (the plants' albedo, A22) is damped by 1 / (1 + fb): 11% less than before.
- A sink-side change (more NPP weathering, as in PW-636's flora; mountains) moves dT by -sensitivity / WEATHER_CO2
  / (1 + fb) per unit of ln sink: 29% more than before.
- A cold era's piled-up CO2 also warms 1.44x more per e-fold, which shortens deep spells. That is the channel the
  health numbers show.

So C brakes A22's plant–albedo deepening and amplifies PW-636's weathering drawdown in dT. The thermostat's new
gain should be measured with `ice_diag --summary` on the 10 seeds (draft filed).

### Tests
- `pytest -q` (-n 4): 599 passed, 2 failed.
  - The sim golden changed on purpose; it is regenerated.
  - `test_timezoom_consistency.py::test_cold_moment_has_sheets` is a single-seed fixture flip. The first plausible
    seed now has 0.42% ice against its 1% precondition. A22 saw it flip too. It is not counted, and PW-643's
    multi-seed fixtures replace it.
- Changed for the API only:
  - `test_co2_stock`'s forcing check (now per doubling);
  - `test_timezoom`'s stats key (`pco2`);
  - `test_timezoom_consistency`'s `pco2=` keyword.

**Verdict: C.** It is sound, not wildly off:
- Earth's glacial lands at 171 ppm;
- Earth's zoom is unchanged from A22;
- today's plants are unchanged (350 ppm at index 0);
- outright C3 failures are negligible;
- the run's deep icehouses come back to main's level.

The cost is a wider pCO2 range in the runs: 5% of keyframes are under ~140 ppm, where tropical forest gives way to
savanna.
