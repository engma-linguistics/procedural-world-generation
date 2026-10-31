---
id: PW-1224
title: One L6 draw ends in a CO2 crash (pCO2 36 ppm, 10 C below pre-industrial) at the 36-draw hard-bar tally
type: task
status: todo
parent: null
milestone: v1
subsystem: climate
effort: m
impact: high
found_by: lane92
blocked_by: []
relates: [PW-1156, PW-1158, PW-1163, PW-244]
refs: [docs/review/v1-cut/checks.md, docs/review/v1-cut/tally_L6.txt, docs/review/v1-cut/tally.py]
created: 2026-10-31
updated: 2026-10-31
---

## Description
In the lane 92 pooled tally (36 L6 1 Gyr draws, rolls 0.0005 and 0.001, code e5b526ff), 0 of 36 were frozen over in the
judged window, 0 boiled, 0 lost oceans. But draw `l6fix` seed 639472 at roll 0.001 (climate_offset 0.002) ends
in a CO2 crash: pCO2 falls from 373 ppm at 952 Myr to 54 ppm at 993 Myr and 36 ppm at 1000 Myr, with the true mean T 9.9 C
below pre-industrial at the end (dT -10.2 C), land ice peak 33.7% of land (below the 40% frozen-over line, so the
frozen-over test does not see it). The finish moment fails, so the draw is a soft fail too. The cause on the step
record is the volcanic source: source_raw falls from 3238 at 930 Myr to 890 at the end (src 0.265 against sink
0.60 at the end) while the sink's raw value only falls from 673 to 406. That is the source-variance mechanism of PW-1156 and PW-1158,
now showing up without a frozen-over world. A second draw (`l6c_p` seed 733847, roll 0.001) dipped to 88 ppm at one step but
recovered to 327 ppm by the end.
Under Daniel's two-tier bar a CO2 crash is a hard failure that must be 100% passing. No number has been set for
"crash" (see the companion draft on hard-bar definitions); lane 92 used pCO2 below 100 ppm at any step after 300 Myr.
Decision for the coordinator: is a crash at the very end of a run a v1 blocker (it is what a viewer would open on)?
What to try: read this draw's source series first (written diagnosis before any sweep), then decide between a floor on
the source's dip and the PW-1158 / PW-1163 pair.
- [ ] a written diagnosis of why the source drops by about 70% over the last 70 Myr of this draw
- [ ] a ruling on whether it blocks the tag

## Updates
- 2026-10-31: Lane 95 plant floor merged: this draw now bottoms at 85 ppm (was 36) and recovers to 120. Still under lane 92's 100 ppm line; crash line put to Daniel as D32.
- 2026-10-31: Daniel 10-31 (D29): C. Build the plant-starvation weathering floor, then set the crash line on the tally's evidence (PW-1223). If it fails, move to v2. Plate-speed question to v2 (PW-1158).
- 2026-10-31: lane 94 diagnosis, docs/review/v1-cut/co2-crash-diagnosis.md (bit-identical rerun; offset is 0.001, not 0.002). Cause: a late assembly (sutures 982/984, largest continent 21->36%) halves trench length and plate speed; the source is 92% arc slab flux (ridges 6%, r 0.92 with arcs), so it falls 3.5x. The sink responds near design but has no plant-starvation floor (FERT 0.44 at 36 ppm), and its tropical weathering cools least (0.044/C vs 0.070). Direction plausible (Mills 2017, Mueller 2024); depth a defect (Pagani 2009). Lean: not a v1 blocker; candidate 1 (plants starve below 124 ppm, drafted) lifts this draw only to ~70 ppm; no source/CO2 floor (clamp).
- 2026-10-31: lane 92: confirmed hard failure (CO2 crash) in the pooled 36-draw L6 tally; see docs/review/v1-cut/checks.md. Bar not loosened.
- 2026-10-31: Created from inbox draft draft-l6-co2-crash-639472-roll001.md (found by lane92).
