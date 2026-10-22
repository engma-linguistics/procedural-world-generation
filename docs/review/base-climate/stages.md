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

Attempts used on PW-582: 3 of 3.
