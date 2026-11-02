---
id: PW-1362
title: "NH subtropical seas are 2.3-3.5 C too cool in the summer half (Gulf 24.6 vs NCEP air 27.2): the Gulf's showers never fire"
type: task
status: todo
parent: null
milestone: v2
subsystem: ocean
effort: m
impact: med
found_by: lane132
blocked_by: []
relates: [PW-593, PW-1321, PW-015]
refs: [docs/review/base-climate/rain-supply/round1.md, docs/review/base-climate/rain-supply/seaair.py, docs/review/base-climate/rain-supply/seaair_L6.txt, docs/review/base-climate/rain-supply/sstswap.py, docs/review/base-climate/rain-supply/screens.md, "planet/climate.py::sea_surface", "planet/climate.py::_sea_half", "planet/climate.py::_summer_half", tools/moisture_regions.py, docs/review/base-climate/rain-supply/round2.md, docs/review/base-climate/rain-supply/seaparts.py, "planet/climate.py::upwelling_cooling"]
created: 2026-11-02
updated: 2026-11-02
---

## Description
In plain words: in the summer half-year, the model's warm western seas in the northern hemisphere are about 3 C
cooler than the real ones. That holds for the sea under the rain and for the finished one.

Earth L6, summer-half means, the model's finished sea air against NCEP's 2 m air:

| sea | model (C) | NCEP (C) |
|---|---|---|
| Gulf of Mexico | 24.6 | 27.2 |
| W Atlantic subtropics | 22.9 | 25.0 |
| E Atlantic subtropics | 20.7 | 23.4 |
| NW Pacific subtropics | 22.6 | 25.0 |

There are two parts:
- PW-593's small NH summer swing (W Atlantic half-swing 1.6 C against 3.0);
- an annual mean that is ~2 C too cool.

Effect on the rain:
- The air can hold ~15% less water, so these seas hold 0.8x NCEP's vapour.
- The Gulf's summer showers never fire. All its rain is large-scale, 523 mm against GPCP's 1239, because the air's
  moist static energy stays below the tropics' reference aloft.
- With NCEP's sea air (lane 132's sstswap.py, 15-50 N), the Gulf's vapour comes to 36.3 mm (obs 39) and its rain to
  673 mm.
- The coasts don't gain from it, though (see draft-rain-coasts-are-through-flow-not-supply).

The coordinator may prefer to fold this into PW-593.

- [ ] Gulf and W Atlantic summer-half sea air within ~1 C of NCEP on Earth

## Updates
- 2026-11-02: Lane 134 diagnosis (round2.md section 4): W Atlantic / NW Pacific annual means right, deficit all swing (PW-593);
  Gulf annual -2.2 C, mostly box-wide coastal upwelling 1.45 C (draft-gulf-upwelling-box-wide); E Atlantic annual -1.5. Suggest
  folding the swing part into PW-593.
- 2026-11-02: Created from inbox draft draft-nh-subtropical-seas-cool-summer-for-rain.md (found by lane132).
