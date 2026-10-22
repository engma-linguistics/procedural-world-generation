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

**Tests and scorecard:** see the end of this section.
