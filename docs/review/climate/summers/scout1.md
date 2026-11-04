# Scout 172: are low-latitude summers still too hot? (PW-1279)

## In plain words
No. On the Earth analogue the warmest month is no longer 3-4 C too hot. At 0-20 deg it is 1.6 C too cool; at 20-40 deg it is 0.4 C too warm; at 40-60 deg it is level. Land at or above 35 C is 1.0% against 1.9% observed. Recommend closing PW-1279 as fixed by PW-1325 (orbit response), PW-1326 B+C and PW-1327 (summer split). One caveat: no stored world was made on the fixed code (see "Worlds"), so the Earth-like-world number rests on lane 135's re-solve of dba204.

## What was measured
`tools/earth_check.py --level 7` on current main (1ecdad3a), 2 cores, 2m44s, plus a band script on the same model output (scratch, deleted). Ice-free land, area-weighted, 60 S to 60 N. Baseline: the repo's "observed" fields in data/earth/L7.npz, which are NCEP/NCAR Reanalysis 1 2 m temperature, 1991-2020 monthly long-term means (tools/earth_data.py header; `obs_t_warm` is the warmest month of that cycle). The ticket quoted CRU instead. NCEP and CRU differ, so the last column below is the better like-for-like check: does the swing from annual mean to warmest month match?

| Land band | Model warmest month | NCEP warmest month | Diff | Model annual mean | NCEP annual mean | Warmest minus annual: model vs NCEP |
|---|---|---|---|---|---|---|
| 0-10 deg | 23.8 | 24.9 | -1.1 | 23.2 | 23.4 | 0.7 vs 1.5 |
| 10-20 deg | 25.9 | 28.0 | -2.2 | 21.6 | 23.9 | 4.3 vs 4.1 |
| 0-20 deg | 24.9 | 26.5 | -1.6 | 22.4 | 23.7 | 2.5 vs 2.8 |
| 20-30 deg | 28.6 | 27.9 | +0.7 | 19.3 | 20.6 | 9.3 vs 7.3 |
| 30-40 deg | 22.8 | 22.8 | 0.0 | 11.1 | 11.8 | 11.8 vs 11.0 |
| 20-40 deg | 26.0 | 25.6 | +0.4 | 15.6 | 16.7 | 10.4 vs 8.9 |
| 40-60 deg | 18.3 | 18.5 | -0.1 | 3.8 | 3.0 | 14.6 vs 15.4 |

Hot tail, land 0-60 deg: warmest month >= 30 C is 16.9% (NCEP 18.3%); >= 35 C is 1.0% (NCEP 1.9%). Before the fixes the diagnosis had 7.9% at >= 35 C and +2.1 C at 20-40 deg (PW-1326).

## Against the ticket's numbers
The ticket's dba204 versus Earth, 0-20 deg: 30.5 vs 26.5 C at annual means 23.1 vs 23.7. Today's Earth analogue is 24.9 vs 26.5 at 22.4 vs 23.7, so the model's own tropics now run slightly cool, not hot. Its warmest-minus-annual swing (2.5 C) is close to the observed 2.8 C.

## Worlds
Every stored world in worlds/ was written 2026-11-01 or earlier (newest 0af5ae, 11-01 04:38). The fixes merged on 11-02 (PW-1327 and PW-1326 B+C at fdc631a4, PW-1325 at 7015d691). So no stored world shows the fixed code, and I did not re-measure worlds or run a new one. The world-side evidence is lane 135's re-solve of dba204 on the fixed orbit rule (PW-1325 update): warmest month 0-20 deg 30.6 -> 25.5 C against 25.4 C with no orbit at all; land >= 30 C 45.0% -> 15.5%; >= 35 C 17.9% -> 2.9%. Against this Earth run (>= 35 C: 1.0% model, 1.9% NCEP) that world's tail is still hotter, but dba204 has more tropical land than Earth, as the ticket already flagged. That re-solve did not include PW-1326/1327, so a world made on current main should be a bit lower still.

## What remains (small, not PW-1279)
- Southern Hemisphere 30-40 deg: warmest month 26.4 vs 23.1 NCEP (+3.4), annual mean only +0.6, so the summer swing is 2.8 C too large (Pampas +5.4 C in earth_check's list). This is the dry-land summer split again. 20-30 deg also has +2.0 C extra swing, but its annual mean is 1.4 C cold, so the warmest month still lands near right.
- 10-20 deg is 2.2 C cool in the warmest month with the right swing; the real error is the 2.3 C cool annual mean (not a summer problem).

## Recommendation
Close PW-1279 with these numbers (Earth analogue: 0-20 deg -1.6 C, 20-40 deg +0.4 C, tail 1.0% vs 1.9% at >= 35 C). For world-side confirmation at no simulation cost, run docs/review/base-climate/summer-heat/world_bands.py on the next world made after 11-02. If anything is kept open, it is the southern dry-land swing, not the tropics: the one lever is the summer split's boundary-layer depth (`split_bl_max`), but it trades against Arabia, US Southwest and India (PW-1326), so it belongs in its own ticket.
