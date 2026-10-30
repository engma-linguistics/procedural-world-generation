---
id: PW-1093
title: Earth's mid-latitude land is ~1.7x too wet (40-60 N, Siberia, Mongolia) while the sea under the same storm tracks is too dry
type: task
status: todo
parent: PW-015
milestone: v2
subsystem: climate
effort: m
impact: med
found_by: lane28
blocked_by: []
relates: [PW-998, PW-026, PW-821]
refs: [planet/climate.py, tools/earth_check.py, tools/moisture_budget.py, docs/review/base-climate/coasts/README.md, tools/moisture_regions.py, docs/review/base-climate/moisture-budget/README.md]
created: 2026-10-30
updated: 2026-10-30
---

## Description
In plain words. On Earth's own map, the model rains far too much on the northern
mid-latitude land: about 1.7 times what the rain gauges (GPCC) record. It was already like
this before the coasts package (PW-998), and the package made it a little wetter. Over the
sea at the same latitudes it's the other way round: the model rains less than the satellite
record (GPCP). So the land-against-sea contrast is inverted, which points at where the
air's vapour falls out, more than at how much there is.

earth_check L6, main before the coasts merge (7d788025) / with it (79c8c289) / observed,
mm/yr:

| | before | with coasts | observed |
|---|---|---|---|
| land 40-50 N | 909 | 952 | 537 (GPCC) |
| land 50-60 N | 906 | 971 | 582 (GPCC) |
| sea 40-50 N | 973 | 1010 | 1298 (GPCP) |
| sea 50-60 N | 837 | 947 | 1152 (GPCP) |
| W Siberia | 609 | 703 | 503 |
| E Siberia | 352 | 432 | 295 |
| Gobi/Mongolia | 556 | 601 | 157 |
| NE USA | 1392 | 1490 | 1032 |
| W Europe | 1214 | 1147 | 911 |
| northward vapour transport at 50 N (Sv) | 0.46 | 0.65 | 0.52 implied |

L7 is the same to within a few percent (W Siberia 696, E Siberia 436, 50-60 N land 967 vs
587). The southern mid-latitude land band (40-50 S) is about right (978 vs 904), but
Patagonia is 2x too wet (921 vs 405). The land's summer-half share of rain is 0.69 against
GPCC's 0.65.

Diagnosis candidates only, none probed yet. Check them with tools/moisture_budget.py per
region and half-year (kernel terms, winds) before changing anything:
1. **The sea doesn't rain out its vapour along the storm tracks.** The sea is short by
   20-25% at 40-60 N while the land downstream is too wet. That fits a rain kernel which
   over the sea converts too little of the vapour it carries into rain, so the vapour lands
   on the first coast and inland. Test: rain efficiency (P/PW) over the N Atlantic and N
   Pacific storm tracks against over Europe and Siberia, compared with NCEP's PW and GPCP/GPCC.
2. **The poleward eddy drift (PW-998 round 3) carries too much vapour north.** Northward
   transport at 50 N went 0.46 to 0.65 Sv, against an implied 0.52 (it was 12% short and is
   now 25% over), and lane 28's state probes showed +15-20% rain at 40-60 from round 3. This
   adds to the wetness but doesn't cause it: the land was already 1.7x before. The drift is
   also what made the polar land right (60-80 N within 3% of GPCC), so the drift's polar
   share and its mid-latitude share may need separating, not a smaller drift.
3. **Land evaporation recycles too much over continental interiors.** Siberia's and
   Mongolia's summer rain could be locally recycled vapour, if land evaporation from wet
   soil, or the soil bucket's refill, is too generous. Lane 25's deserts diagnosis found land
   imports ~1.9x the net vapour at the monsoon margins; the same check is worth doing at 50 N.
   Test: the share of interior rain from land evaporation against the share brought in.
4. **Summer convection over warm continents.** The summer-half share is 0.69 vs 0.65, and
   Mongolia's error is mostly summer-type (model Dwb against Kottek BWk). A shower rate that
   is too easy on warm land would wet the interiors in summer. Test: the Apr-Sep against
   Oct-Mar split per region.
5. **The westerlies' inland reach (PW-026).** If winter maritime air goes too far inland
   with too much vapour, Siberia's winter would be the wet half instead. The same
   half-year split tells candidates 4 and 5 apart.

Don't tune the eddy drift or the shower rates until the budget says which half-year and
which source carries the excess. Earth is a plausibility anchor, not a target: the bar is
"plausible", not GPCC parity.

- [ ] Per region (W/E Siberia, Mongolia, NE USA, W Europe) and half-year: where the excess rain comes from (sea vapour brought in vs land recycling) and in which half
- [ ] A written diagnosis choosing among candidates 1-5, before any change
- [ ] Any fix keeps the polar land (60-80 N) near GPCC and doesn't push Earth's B share further below Kottek's 30% (now 25.2%)

## Updates
- 2026-10-30: Owner 10-30 D11: moisture/monsoon-coast work parked for v2; an agent will find a downloadable drag source.
- 2026-10-30: Lane 58 budget (docs/review/base-climate/moisture-budget/README.md, tools/moisture_regions.py; kernel re-runs on the recorded Earth L6/L7
  inputs). The excess is summer: 88% at 40-50 N, 70% at 50-60 N. It is imported sea vapour (land P - E 2.26 Sv,
  published runoff ~1.15; land E about right, below NCEP in the summer interiors). None of 1-5 is the cause:
  (1) storm-track sea rain x1.5 moves 40-60 N land -25 mm; (2) no drift -64 at 50-60 N but polar land 399 -> 299;
  drift 0.8 -11; (3) land E -20% moves -35, ruled out; (4) showers x0.5 -73 / -4, supply-limited; (5) supported
  for 50-60 N winter only (winter interiors import 3x observed; W Siberia winter 534 -> 399 at 0.7x wind).
  The 40-50 N lever is monsoon_wind's cross-isobar inflow: whole-Earth solves 0.45 -> 0.2 give 40-50 N
  952 -> 817, Gobi 601 -> 284, B 25.2 -> 31.5, but SE USA 636 -> 382, Pampas 401 -> 190, corr 0.721 -> 0.681.
  Lean: one soundness round (inflow depth + convergence lift; drafts), no drift or shower retune. 50-60 N summer
  (Siberia, Canada) resists every lever tried.
- 2026-10-30: Created from inbox draft draft-midlatitude-land-too-wet.md (found by lane28).
