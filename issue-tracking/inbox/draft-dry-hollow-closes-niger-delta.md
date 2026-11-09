---
title: "The dry-catchment rule closes the inner Niger delta on Earth L7: the Niger ends in a lake near Lake Debo instead of reaching the sea"
type: task
status: todo
parent: null
subsystem: hydrology
effort: s
impact: med
found_by: scout260
blocked_by: []
relates: [PW-054, PW-831, PW-430]
refs: [planet/hydrology.py::_dry_hollows, planet/hydrology.py::_settle, planet/hydrology.py::DRYLAND_AI, docs/review/wetlands/scout260.md, docs/review/wetlands/scout260/earth_wet.py, docs/review/wetlands/scout260/earth_capture.py, docs/review/basins/scout251.md]
---

## Description
In plain words: the rule merged for PW-054 (a hollow stays a closed basin when the land draining into it is
desert on average) also catches a big river that rises in wet hills and crosses a dry plain. On Earth's terrain
at L7 the Niger ends in a closed lake in its inner delta (14.5-15.0 N, 4.3-4.4 W, near Lake Debo) and never reaches
Timbuktu or the sea. The real Niger loses about 40% of its water in the inner delta and passes the rest on
(inputs ~1490 m3/s, Timbuktu ~900 m3/s, 1955-1996; Mahe et al. 2009, cited in IAHS 2011
iahs.info/uploads/dms/16775.26-138-143-344-30-Mahe-et-al-corr.pdf).

Numbers (scout 260, `earth_wet.py`, Earth world's hydrology inputs as built, baseline: the same inputs with
`DRY_HOLLOWS = False`):
- model climate L7: main ends the Niger in a sink with 2962 m3/s arriving; with the rule off it reaches the sea
  (Dire 3219 m3/s). Inland 21.8% -> 21.4% of ice-free land.
- observed (GPCC) rain through the model's water balance, L7: main ends it at 15.0 N with 434 m3/s left after the
  delta lake; rule off: Dire 677 m3/s, to the sea.
- L6 routes the upper Niger west into the Senegal on the cell-mean terrain, so the check needs L7.

Why: `_dry_hollows` judges a hollow by the area-mean rain against 0.65 x Oudin PET over its whole catchment;
the Niger's catchment above the delta is mostly Sahel, so it counts as dry even though most of the water comes
from the wet Guinea highlands, and the closed-lake balance then swallows the river in a small lake (~8000 km2
at ~2.7 m/yr open-water evaporation). Generated worlds will have the same case (exotic rivers into a dry
interior), where it makes rivers end too early and lifts the inland share for the wrong reason.

What to try: judge the catchment by where its water comes from, not its area: e.g. keep the hollow only if the
part of the catchment that yields runoff is dry too (runoff-weighted P/PET, or no upstream sub-basin with
P/PET above 1 supplying more than half the inflow). Earth check: Niger reaches Dire at L7, inland and false
positives as scout 251's (13.5 / 19.4%, false + 3.6 / 6.8%).

What breaks if never done: Earth's third river of Africa (and generated worlds' exotic rivers) ends in a
desert lake; the inland share and lake counts include it.
- [ ] Niger reaches the sea at L7 on Earth with the rule on
- [ ] Earth inland share and false positives within 0.5 points of scout 251's
