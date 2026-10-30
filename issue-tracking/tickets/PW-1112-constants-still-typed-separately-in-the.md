---
id: PW-1112
title: Constants still typed separately in the ice time zoom, and year length and km-per-degree still disagree between files
type: task
status: todo
parent: null
milestone: null
subsystem: infra
effort: s
impact: low
found_by: refactor-lane-59
blocked_by: []
relates: [PW-1034, PW-445]
refs: [planet/constants.py, planet/timezoom/kernels.py, planet/timezoom/sim.py, planet/timezoom/sources.py, planet/climate.py, planet/lineages/contacts.py, planet/lineages/demes.py]
created: 2026-10-30
updated: 2026-10-30
---

## Description
In plain words. Refactor 1 gave the model one file for the shared physical numbers (`planet/constants.py`: seconds per year, gravity, ice density, sea-water heat capacity, the 14.5 C reference temperature) and pointed every copy with the same value at it. Three groups were left on purpose.

1. The ice time zoom (`timezoom/kernels.py`: `RHO_G = 917.0 * 9.81`, the 917 in the snow-to-ice step, `YEAR_S = 3.15576e7`; `timezoom/sim.py`: `RHO_I * 9.81`, `14.5 + ...`; `timezoom/sources.py`: `- 14.5`) because the ice lane was editing those files. They can switch to `constants.GRAV`, `RHO_ICE`, `T_REF_C` without changing any number. Its year length is `3.15576e7`, not the shared `3.156e7`, so that one changes ice results by 0.01 percent and needs a golden update.
2. Two other year lengths: `climate.YEAR_S = 365.25 * 86400` (used for the sea's heat storage) differs from the shared `3.156e7` by 0.01 percent. Choosing one value moves outputs a little, so it needs a deliberate golden update (PW-1034).
3. Kilometres per degree of latitude: 111.2 in `climate.py` (jet gradient), 111.0 in `lineages/contacts.py` and `lineages/demes.py`, while the radius gives 111.19. One `KM_PER_DEG = R_KM * pi / 180` changes those outputs slightly.

- [ ] switch the time zoom's copies (no output change) once the ice lane is merged
- [ ] decide the one year length and one km-per-degree, update goldens, and note it on PW-1034

## Updates
- 2026-10-30: Created from inbox draft draft-refactor1-timezoom-constants-left.md (found by refactor-lane-59).
