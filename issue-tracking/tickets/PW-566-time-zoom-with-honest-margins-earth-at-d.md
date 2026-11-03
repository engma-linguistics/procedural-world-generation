---
id: PW-566
title: "Time zoom with honest margins: Earth at dT 0 grows 3-4 Mkm2 of ice in the first weak summer and keeps it (the interglacial-ice floor)"
type: task
status: todo
parent: PW-470
milestone: later
subsystem: timezoom
effort: m
impact: high
found_by: ice-v2-stage1
blocked_by: []
relates: [PW-555, PW-460, PW-459, PW-115, PW-366]
refs: [planet/timezoom/sim.py, planet/icemass.py, docs/review/ice-v2/stage-1.md, docs/review/ice-v2-criteria.md]
created: 2026-10-22
updated: 2026-11-03
---

## Description
Stage 1b (PW-555; stage-1.md, "The interglacial ice isn't a deglaciation failure"). Earth L6 time zoom, index off
(today's climate, only the orbit swinging), Mkm2 of grounded ice (today 14.1 = 9.6% of land):

| t (kyr) | 2 (Eemian-like summer) | 14 (weak) | 46 (strong) | 200 |
|---|---|---|---|---|
| stage-1b defaults | 14.6 | 18.3 | 16.9 | 18.6 (12.6%) |
| baseline=obs | | 16.5 (t 20) | 17.2 (t 100) | 17.6 (12.0%) |
| main's zoom rules | 12.7 | 18.9 | 13.9 (9.5%) | |

With the old rules (408 m edge, 0.25 orbit gain) the ice comes and goes with the orbit. With honest margins it grows
in the first weak summer and the next strong summer doesn't take it back, a precession-scale hysteresis at today's
climate. Every interglacial of the index-on zoom lands on that floor (11.8-15.5% of land, bar 9-12), and the
recovery bar (today's ice held within 20% at dT 0) fails (+20..+32%). The start anchor isn't it (anchor=none and
anchor_rings=0 give the same), and removing the base bias (baseline=obs) only lowers it to ~12%.
Where (t 46): the Canadian Arctic islands ~0.8 Mkm2 (observed warm month +1..+2 C at 300 m), Greenland's coastal
strip and shelf ~1.0 (half marine-grounded; it spreads 0.4 Mkm2 within 2 kyr under an Eemian orbit), mountains
(Alaska, Coast Mountains, Andes, Tibet) ~0.5, Scandinavia 0.2 (base bias).
Greenland's margin cells have a balance of +0.20 m/yr today in the zoom (scratch `termprobe.py`). An ablation zone
50-150 km wide should make a 110 km margin strip's mean about nil or negative.
Suspects, in the order to measure:
- the ramp's lower quadrature point (0.21 of the iced width, ~620 m at L6) never samples the outer edge;
- the front rule (bare land the flow reaches becomes a bright edge 408 m high, PW-366);
- a cell iced in full once its mean balance is positive (no sub-cell cover for caps on near-threshold land);
- the degree-day factors on bare ice.
Needs an observed surface mass balance for Greenland (e.g. RACMO or MAR, binned by distance from the margin) as the
check. Also the next lever for PW-555 stage 1, after the air lever (3 attempts) and the base climate (baseline=obs)
both hit their stop rules: the owner's call.
- [ ] Earth zoom, index off: today's ice within 20% of its area for 100 kyr, coming and going with the orbit
- [ ] Greenland's margin balance against an observed SMB
- [ ] then interglacial ice 9-12% (tools/tz_earth.py) and the L4 endings test

Stage 1c (2026-10-22, PW-555; stage-1.md "Stage 1c"): yardstick `tools/tz_earth.py --dt0`, reference RACMO2.3p3
(`tools/tz_earth.py --greenland`). RACMO's outer 110 km strip of Greenland is +0.15 m/yr (the outer 55 km +0.01), so a
margin cell near nil is right; the L6 margin cells are -0.02 in RACMO against +0.21 in the zoom (inland +0.29 vs
+0.28). Suspects: (a) the ramp's quadrature: no effect (1.30 -> 1.29); (b) the front as the ramp's outer 10 km with the
fetch share (front=ramp, kept): 1.30 -> 1.17, within 20%; (c) the caps grown in place are the base climate's cold
mountains (Eurasia -0.9 vs +3.2 C observed; gone with baseline=obs), not the full-cell rule. What's left: the area
stays +15% and doesn't follow the orbit; Greenland +0.85 and Arctic Canada +0.83 Mkm2 by the front advancing (half
on marine beds), with Greenland's N and E margins 2-5 C too cold in summer (the ice-surface air, see
draft-zoom-ice-surface-too-cold-on-greenland). Interglacials 11.4-13.1% (bar 9-12).
- [x] Earth zoom, index off: today's ice within 20% of its area for 100 kyr (1.17 max)
- [ ] ... coming and going with the orbit (flat at +15%)
- [x] Greenland's margin balance against an observed SMB (RACMO2.3p3, cached)

## Updates
- 2026-11-03: Parked 11-03 per fresh-eyes review (docs/review/fresh-eyes/2026-11-03.md s3): milestone v2 -> later. Ice-age epic PW-470 is parked post-v1 (owner 10-28 timebox); PW-467 is the one kept as the timeboxed item.
- 2026-10-23: Status needs-decision -> todo. Coordinator (2026-10-24): owner defers geophysics; not an owner question. The physics lane decides it against the v1/v2 north star (seed robustness first) when it reaches it.
- 2026-10-23: Milestone v1 -> v2 (owner approved shrinking v1 to its real gates, 2026-10-24; docs/review/board/triage-2026-10-24.md).
- 2026-10-22: Created from inbox draft draft-earth-zoom-does-not-hold-todays-ice-at-dt0.md (found by ice-v2-stage1).
