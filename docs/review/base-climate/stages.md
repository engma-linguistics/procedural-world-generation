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
