---
title: "Stage 3 with the redesigned fetch is green and meets the SH-range and rain bars, but humid summers stay +3-4 C and W Europe/Fennoscandia are below main's: merge?"
type: task
status: needs-decision
parent: PW-470
milestone: v1
subsystem: climate
effort: xs
impact: high
found_by: base-climate-laneA12
blocked_by: []
relates: [PW-587, PW-588, PW-573, PW-352, PW-457, PW-581, PW-586, PW-580]
refs: [planet/climate.py, docs/review/base-climate/stages.md, docs/review/base-climate/laneA12/]
---

## Description
Lane A12 redesigned the fetch (PW-587 option B) and landed it with the rest of stage 3 on its branch. The parts are
the per-time reach, the PET-referenced energy split, the mountain rule and the humidity floor. The section is
"Stage 3, round 2 attempt 1" in stages.md.

The fetch: summer air = arriving sea air + (sum_h / fetch_h + (1 − sum_h / fetch_h) × the land's share within
fetch_km) × (the land's own summer − the arriving sea air).
- The arriving sea air is weighted along the wind over `fetch_km`.
- fetch_km = 1000 km and fetch_h = 3500 m. Both are distances, so they don't depend on the grid.

Results:
- `uv run pytest -q` passes (568), with the goldens regenerated on purpose.
- The endings test: 58 / 1.4 m, and 58–59 / 1.3–2.4 at −3.9 / −4.1 C.

Earth L6, main → this:

| bar | main | this | verdict |
|---|---|---|---|
| humid warmest within 2.5 C: SE USA / SE China / NE USA / Great Lakes | +4.8 / +4.9 / +6.0 / +6.1 | +3.6 / +3.3 / +3.7 / +3.5 | better, not met |
| ... Labrador / HB lowlands / Pampas / E Australia | +4.2 / +5.6 / +5.6 / +4.4 | +2.0 / +3.7 / +4.3 / +1.8 | better, 2 of 4 met |
| SH coastal range ≤ 1.3× NCEP 9.6 | 14.3 (1.49×) | 12.4 (1.29×) | pass |
| W Europe warmest / Fennoscandia warmest | +0.4 / −5.2 | −2.1 / −5.7 | worse (the sea air: own draft) |
| dry-region summer rain N / S (obs 167 / 200) | 660 / 1623 | 602 / 1165 | pass |
| rain r ≥ 0.617 | 0.622 | 0.620 | pass |
| Köppen group / exact | 70.5 / 30.9 | 69.5 / 31.7 | −1.0 / +0.8 |
| stage-1/2 (NH Sv, open share, Norway open, winters) | 14.41, 92%, 100% | 14.37, 92%, 100% | hold |

No setting of fetch_km (700–1400) or fetch_h (2500–5000) meets both the SH range and W Europe
(`laneA12/stage3_probe_fetch_sens.txt`). W Europe's loss is the sea's summer air, 2.3–3.8 C too cold off Europe
(`draft-near-land-sea-summer-air-cold-north-warm-south.md`).

Options:
- A: merge, under the owner's principle. It is a sounder mechanism, better overall, and green. W Europe and
  Fennoscandia go to the SST ticket.
- B: hold stage 3 until the near-land SST is fixed.
- C: merge without the fetch (the old candidate). That fails the SH bar and leaves the land-cools-sea flaw out of the
  picture.

Lean: A.
