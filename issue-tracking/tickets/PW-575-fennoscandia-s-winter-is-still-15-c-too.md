---
id: PW-575
title: "Fennoscandia's winter is still 15 C too cold with the Norwegian Sea open: the winter winds over the Nordic Seas blow offshore, and the air's winds never see the sea's own warmth"
type: task
status: todo
parent: PW-570
milestone: later
subsystem: climate
effort: l
impact: high
found_by: base-climate-laneA
blocked_by: []
relates: [PW-458, PW-346, PW-570, PW-015]
refs: [planet/climate.py, tools/overturning_report.py, docs/review/base-climate/stages.md]
created: 2026-10-22
updated: 2026-11-03
---

## Description
Found closing PW-458 (lane A, stage 1). The overturning now sinks in the Nordic Seas and keeps the Norwegian
Sea open all winter. Its coldest-month sea air is +0.6 C (NCEP +3.5). But Fennoscandia's coldest month only warms
from 18.5 to 14.7 C too cold (Earth L6, `tools/overturning_report.py --earth`). The approved plausibility bar is
±6 C.

**Measured** (Earth L6, coldest month, model / NCEP; winter wind = mean east / north components of `wind_jan`,
model units):

| box | Tc | NCEP | winter wind E / N |
|---|---|---|---|
| Norway coast land 58–71N 4–14E | −14.8 | −5.2 | +0.22 / +0.09 |
| Sweden 58–68N 14–22E | −24.6 | −8.3 | +0.06 / +0.02 |
| Finland 60–70N 22–32E | −27.1 | −10.8 | +0.03 / +0.01 |
| Norwegian Sea 62–72N 5W–12E | +0.9 | +2.9 | **−0.21 / −0.15** |
| Barents Sea 70–78N 20–50E | −18.2 | −6.5 | −0.41 / −0.11 |
| British Isles | −1.2 | +4.7 | +0.80 / +0.44 |

**The mechanism.**
- Over the Nordic and Barents seas the winter wind blows from the land, out to sea (north-easterly). The interior is
  close to calm. So `_air_temps`' carry brings no sea air in, and the land relaxes to its own winter.
- On Earth the Icelandic low sits over the warm Nordic water. On its east side the winter wind is a strong
  south-westerly onto Norway, and the storms carry the sea's warmth far inland.
- In `climate.compute` the winds come from `monsoon_wind` on the sea-level temperatures. Over the sea those are the
  **latitude's** sea air, `t_sea_air`, without the currents or the overturning. So the model's wind can't make a low
  over a warm polar sea: the Siberian high's continent-wide part reaches out over a sea it sees as cold.
- Tried, and dropped: recomputing the air's winds after the overturning with its warmth (and its milder winter) over
  the sea. Norway's coast went only −14.8 → −14.1 C. `monsoon_wind`'s land-sea part is capped poleward of 40N
  (0.21 at 65N), so the polar band's northerlies win.

**What to try** (stage 2, the sea's air, or its own ticket):
- the winds from the full sea surface (currents and overturning), not the latitude's sea air;
- the cap on the land-sea winds at high latitudes;
- the storms' eddy heat transport onto the land in winter. The carry's diffusion (0.25) is all it has today, and
  the storm tracks (`storm_track`) are only used for the rain.

Generated planets have the same gap wherever a warm current or an overturning reaches a polar sea.
- [ ] Fennoscandia's coldest month within ±6 C of NCEP on Earth L6, with the Norwegian Sea still open in winter
- [ ] the winter wind over a warm polar sea onshore on its continent's coast

## Updates
- 2026-11-03: Triage 11-03: v2 -> later: calibration or second-order physics refinement, not needed for the planet to be stable or for the culinary goal
- 2026-10-23: Milestone v1 -> v2 (owner approved shrinking v1 to its real gates, 2026-10-24; docs/review/board/triage-2026-10-24.md).
- 2026-10-22: 2026-10-22 merged (lane A6, attempt 2): wind belts follow the air masses (front_shift); winter air over land relaxes in time (air_m 1000 m). Fennoscandia coldest-month bias -11.9 -> -8.9 C (bar +-6 not met: Barents/N Greenland Sea freeze, new ticket); Norwegian Sea winds now onshore; London +1.6, Stockholm -8.9; rain r 0.622, Koppen 70.3. Merged as a mechanism improvement (owner principle).
- 2026-10-22: Created from inbox draft draft-nordic-winter-winds-offshore.md (found by base-climate-laneA).
